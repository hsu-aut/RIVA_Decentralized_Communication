import threading
import random
import time
from shapely.geometry import Point, Polygon
from world.obstacles import OBSTACLES
from constants import COM_LOSS_RATE
 
COMM_DELAY_S = 1.2                                      # communication deactivation in seconds for time-triggered communication
 
def no_comm():
    pass
 
def time_comm(sender, comm_candidates, instantiated_rovers):          # TimingBased
    def comm_reactivation(sender):
        start_time = sender.sim_time
        # Function to rectivate communication after delay
        while sender.comm_active == False:  
            time.sleep(0.3)                             # delay to not update end_time too often, which causes performance issues for larger number of simulated rovers
            end_time = sender.sim_time
            if end_time - start_time >= COMM_DELAY_S:
                sender.comm_active = True
    
    comm_candidate = comm_candidates[0]
    for receiver_id, receiver in instantiated_rovers.items():
        if receiver != sender and not receiver.reached_target:  # Avoid sending message to itself and to instances that reached the target
            receiver.active_communications += 1
            threading.Thread(target=delayed_receive_message, args=(receiver, comm_candidate, sender)).start()
    threading.Thread(target=comm_reactivation, args=(sender,)).start()
    sender.comm_candidates.pop(0)           # Clear the first item of comm_candidates as it was just communicated
 
def plan_aware_comm(sender, comm_candidates, instantiated_rovers, theta=0.3, horizon=4):
    """
    Plan-Aware Communication (timing-focused) according to "Planning-aware_Communication_for_Decentralised_Multi-Robot_Coordination".
    Idee: Plane den *Zeitpunkt* für Kommunikation. Wähle den Empfänger,
    dessen prognostizierte Unsicherheit σ̂_j(t) innerhalb der nächsten T Schritte
    zuerst die Schranke θ überschreitet – und sende dann genau jetzt.

    Args:
        sender: aktueller Rover (braucht .sim_time, .comm_active, .comm_candidates, etc.)
        comm_candidates: Liste der Nachrichtenkandidaten (höchste Priorität an Index 0)
        instantiated_rovers: dict[id -> rover]
        theta: Unsicherheitsgrenze (Timing-Trigger)
        horizon: Planungshorizont in Schritten (T>=1)

    """
    import threading, time, math

    if not comm_candidates:
        return

    # Kandidaten-Empfänger (keine Selbstsendung, keine schon fertigen)
    receivers = [
        r for r in instantiated_rovers.values()
        if r is not sender and not getattr(r, "reached_target", False)
    ]
    if not receivers:
        return

    # --- Hilfsfunktionen: verbesserte σ̂-Modelle ---
    def distance_to_rover(r):
        """Berechnet die Distanz zwischen sender und receiver"""
        try:
            dx = sender.x - r.x
            dy = sender.y - r.y
            return math.sqrt(dx*dx + dy*dy)
        except:
            return 100.0  # Fallback-Distanz

    def baseline_sigma(r):
        """Berechnet die Baseline-Unsicherheit für einen Rover"""
        s = 0.0
        
        # Basis-Unsicherheit basierend auf Distanz zum Ziel
        try:
            dist_to_target = r.distance_to_target
            s += min(1.0, dist_to_target / 200.0)  # Normalisiert auf 0-1
        except:
            s += 0.5
        
        # Unsicherheit basierend auf Anzahl bekannter Hindernisse
        try:
            known_obstacles = r.number_of_known_obstacles
            total_obstacles = len(OBSTACLES) if 'OBSTACLES' in globals() else 10
            s += (total_obstacles - known_obstacles) / total_obstacles * 0.5
        except:
            s += 0.3
        
        # Unsicherheit basierend auf Distanz zwischen Rovern
        try:
            dist = distance_to_rover(r)
            s += min(0.4, 50.0 / max(dist, 1.0))  # Nähere Rover = höhere Unsicherheit
        except:
            s += 0.2
            
        return min(1.0, s)  # Clamp auf 0-1

    def sigma_forecast(r, steps):
        """Prognostiziert die Unsicherheitsentwicklung über die nächsten Schritte"""
        s0 = baseline_sigma(r)
        
        # Wachstumsrate basierend auf verschiedenen Faktoren
        growth = 0.0
        
        # Wachstum basierend auf Distanz zwischen Rovern
        try:
            dist = distance_to_rover(r)
            growth += min(0.3, 30.0 / max(dist, 1.0))
        except:
            growth += 0.1
        
        # Wachstum basierend auf Bewegung zum Ziel
        try:
            if r.distance_to_target > sender.distance_to_target:
                growth += 0.2  # Rover ist weiter weg = mehr Unsicherheit
        except:
            growth += 0.1
        
        # Wachstum basierend auf Anzahl bekannter Hindernisse
        try:
            known_obstacles = r.number_of_known_obstacles
            total_obstacles = len(OBSTACLES) if 'OBSTACLES' in globals() else 10
            if known_obstacles < total_obstacles * 0.5:
                growth += 0.2  # Wenig bekannte Hindernisse = mehr Unsicherheit
        except:
            growth += 0.1
        
        growth = max(0.1, min(growth, 0.5))  # Clamp für Stabilität
        
        # Lineares Wachstum mit leichtem exponentiellen Faktor
        return [s0 + k * growth + (k * k * 0.01) for k in range(1, steps + 1)]

    # --- Timing-Entscheidung: frühesten θ-Bruch im Horizont finden ---
    best = None  # (t_cross, receiver, sigma_path)
    for r in receivers:
        seq = sigma_forecast(r, horizon)  # σ̂[1..T]
        t_cross = None
        for t, s in enumerate(seq, start=1):
            if s > float(theta):
                t_cross = t
                break
        if t_cross is not None:
            if best is None or t_cross < best[0] or (t_cross == best[0] and seq[t_cross-1] > best[2][t_cross-1]):
                best = (t_cross, r, seq)

    # Falls *kein* Überschreiten von θ in [1..T] prognostiziert: nichts senden (Timing sagt "zu früh")
    if best is None:
        return

    # Wenn der früheste Bruch bereits bei t=1 liegt, ist *jetzt* der richtige Zeitpunkt zu senden.
    t_cross, receiver, _ = best
    if t_cross > 1:
        # Noch nicht fällig -> früh raus (du kannst optional ein "deadline_at" merken)
        return

    # --- Senden (punkt-zu-punkt) ---
    comm_candidate = comm_candidates[0]
    receiver.active_communications += 1
    threading.Thread(
        target=delayed_receive_message,
        args=(receiver, comm_candidate, sender),
        daemon=True
    ).start()

    # Reaktivierung/Backoff
    def comm_reactivation(agent):
        start_time = agent.sim_time
        while agent.comm_active is False:
            time.sleep(0.3)
            if agent.sim_time - start_time >= COMM_DELAY_S:
                agent.comm_active = True
                break
    threading.Thread(target=comm_reactivation, args=(sender,), daemon=True).start()

    # Konsumierten Kandidaten entfernen
    sender.comm_candidates.pop(0)

def utility_aware_comm(
    sender,
    comm_candidates,
    instantiated_rovers,
    duplicate_penalty=0.1  # Markov: Duplikate stark abwerten
):
    """
    Utility-Aware Communication (content-focused) according to "Information Distribution in Multi-Robot Systems_Generic, Utility-Aware Optimization Middleware":
    - Idee:
        (1) Utility-Skalar U(c) = 1/(1+Distanz(region,zum Ziel))
        (2) Markov-Annahme: nahezu identische Inhalte stark abwerten
    """

    # Speicher für einfache Markov-Deduplication (Fingerprints) pro Sender
    if not hasattr(sender, "_last_fingerprints"):
        sender._last_fingerprints = set()

    # --- 1) Utility-Skalar ---
    def content_assessment(sender, comm_candidates):
        selected_comm_candidates = []
        total_distance = sum(
            instance.distance_to_target
            for instance in instantiated_rovers.values()
            if not instance.reached_target
        )
        num_instances = sum(
            1 for instance in instantiated_rovers.values()
            if not instance.reached_target
        )
        avg_distance_to_target = total_distance / num_instances if num_instances != 0 else 0

        for candidate in comm_candidates:
            if Polygon(candidate).distance(Point(sender.target_coordinates)) < avg_distance_to_target:
                selected_comm_candidates.append(candidate)
        return selected_comm_candidates

    prelim = content_assessment(sender, comm_candidates)

    # --- 2) Utility bestimmen & Kandidaten priorisieren ---
    #     U(c) = 1 / (1 + Distanz(region, target))
    #     Duplikate -> * duplicate_penalty
    scored = []
    tgt = Point(sender.target_coordinates)

    for cand in prelim:
        poly = Polygon(cand)
        d = poly.distance(tgt)
        base_u = 1.0 / (1.0 + d)

        # einfacher Fingerprint für „nahezu identisch“
        fp = (round(poly.area, 3), round(poly.centroid.x, 2), round(poly.centroid.y, 2))
        u = base_u * (duplicate_penalty if fp in sender._last_fingerprints else 1.0)

        scored.append((u, fp, cand))

    # nach Nutzen absteigend
    scored.sort(key=lambda x: x[0], reverse=True)

    # --- 3) Senden  ---
    to_remove = []
    for u, fp, cand in scored:
        if u <= 0.0:
            continue

        for receiver_id, receiver in instantiated_rovers.items():
            if receiver != sender and not receiver.reached_target:
                receiver.active_communications += 1
                threading.Thread(
                    target=delayed_receive_message,
                    args=(receiver, cand, sender),
                    daemon=True
                ).start()

        # Markov-Status aktualisieren & aus Queue entfernen
        sender._last_fingerprints.add(fp)
        to_remove.append(cand)

    for c in to_remove:
        try:
            sender.comm_candidates.remove(c)
        except ValueError:
            pass 
 
def receiver_aware_comm(
    sender,
    comm_candidates,
    instantiated_rovers,
    tau_comm=0.0,     # Mindest-Teamgewinn (Best-Response Schwelle)
    tau_accept=0.0,   # Mindest-Eigennutzen für Empfänger (opt-in)
):
    """
    Receiver-Aware Communication according to "A Best-Response Algorithm With Voluntary Communication and Mobility Protocols for Mobile Autonomous Teams Solving the Target Assignment Problem":
    - Idee:
        (1) Best-Response-Score Δ_team für jeden (Empfänger, Kandidat)
        (2) freiwillige Kommunikation: nur adressieren, wenn Δ_self des Empfängers >= tau_accept
        
    Annahmen:
      - sender/receiver haben .target_coordinates
      - receiver.distance_to_target existiert
      - delayed_receive_message(receiver, comm_candidate, sender)
    """

    def comm_receiver_assessment(sender, instantiated_rovers):
        comm_receiver = []
        for receiver_id, receiver in instantiated_rovers.items():
            if receiver != sender and not receiver.reached_target and receiver.distance_to_target > sender.distance_to_target:
                comm_receiver.append(receiver)
        return comm_receiver

    # --- dein bestehender Empfänger-Pool ---
    comm_receiver = comm_receiver_assessment(sender, instantiated_rovers)
    if not comm_receiver:
        return

    # Hilfsfunktionen
    def _pt(xy, default=(0.0, 0.0)):
        if xy is None:
            return Point(default)
        if isinstance(xy, (list, tuple)) and len(xy) == 2:
            return Point(float(xy[0]), float(xy[1]))
        return Point(default)

    sender_target = _pt(getattr(sender, "target_coordinates", None))

    for comm_candidate in list(comm_candidates):
        poly = Polygon(comm_candidate)
        task_pt = poly.centroid  # Task-Repräsentation aus Kandidat (leichtgewichtige Proxy)
        d_sender_task = sender_target.distance(task_pt)

        # Score-Liste: (Δ_team, receiver, Δ_self)
        scored = []
        for receiver in comm_receiver:
            rcv_target = _pt(getattr(receiver, "target_coordinates", None))
            d_recv_task = rcv_target.distance(task_pt)

            # Best-Response: teamweiter Grenznutzen, wenn Info an diesen Empfänger geht
            delta_team = d_sender_task - d_recv_task

            # Annahme: wird es auch für den Empfänger besser?
            # Näherungsweise mit seinem aktuellen distance_to_target vs. hypothetischer Task-Distanz
            delta_self = float(getattr(receiver, "distance_to_target", 0.0)) - d_recv_task

            # Schwellen prüfen
            if delta_team >= tau_comm and delta_self >= tau_accept:
                scored.append((delta_team, receiver, delta_self))

        if not scored:
            # Niemand profitiert genug -> überspringen
            continue

        # Broadcast an die ausgewählten Empfänger
        for _, receiver, _ in scored:
            receiver.active_communications += 1
            threading.Thread(
                target=delayed_receive_message,
                args=(receiver, comm_candidate, sender),
                daemon=True
            ).start()

        # Kandidat wurde kommuniziert -> aus Queue entfernen
        try:
            sender.comm_candidates.remove(comm_candidate)
        except ValueError:
            pass 
 
     
def integrated_comm(sender, comm_candidates, instantiated_rovers):
    def comm_reactivation(sender):
        start_time = sender.sim_time
        # Function to rectivate communication after delay
        while sender.comm_active == False:  
            time.sleep(0.3)                 # delay to not update end_time too often, which causes performance issues for larger number of simulated rovers
            end_time = sender.sim_time
            if end_time - start_time >= COMM_DELAY_S:
                sender.comm_active = True
    
    def team_utility_assessment(sender, comm_candidates):
        selected_comm_candidates = []
        total_distance = sum(instance.distance_to_target for instance in instantiated_rovers.values() if not instance.reached_target)
        num_instances = sum(1 for instance in instantiated_rovers.values() if not instance.reached_target)
        avg_distance_to_target = total_distance / num_instances if num_instances != 0 else 0
 
        for candidate in comm_candidates:
            if Polygon(candidate).distance(Point(sender.target_coordinates)) < avg_distance_to_target:
                selected_comm_candidates.append(candidate)
        return selected_comm_candidates
    
    def comm_receiver_assessment(sender, instantiated_rovers):
        comm_receiver = []
        for receiver_id, receiver in instantiated_rovers.items():
            #if receiver != sender and not receiver.reached_target and Point(sender.x, sender.y).distance(Point(receiver.x, receiver.y)) > DIST_THRESHOLD:
            if receiver != sender and not receiver.reached_target and receiver.distance_to_target > sender.distance_to_target:
                comm_receiver.append(receiver)
        return comm_receiver
    
    
    selected_comm_candidates = team_utility_assessment(sender, comm_candidates)
    comm_receiver = comm_receiver_assessment(sender, instantiated_rovers)
    if comm_receiver and selected_comm_candidates:    
        for comm_candidate in selected_comm_candidates:    
            for receiver in comm_receiver:
                receiver.active_communications += 1
                threading.Thread(target=delayed_receive_message, args=(receiver, comm_candidate, sender)).start()
        for comm_candidate in selected_comm_candidates:
            sender.comm_candidates.remove(comm_candidate)           # Clear the item of comm_candidates which was just communicated
        threading.Thread(target=comm_reactivation, args=(sender,)).start()
    else:
        sender.comm_active = True
        
def full_comm(sender, comm_candidates, instantiated_rovers):
    for receiver_id, receiver in instantiated_rovers.items():
        for candidate in comm_candidates:    
            if receiver != sender and not receiver.reached_target:  # Avoid sending message to itself and to rovers that reached the target
                receiver.active_communications += 1
                threading.Thread(target=delayed_receive_message, args=(receiver, candidate, sender)).start()
    sender.comm_candidates = []
 
def delayed_receive_message(receiver, obstacle, sender):
    end_of_delay = False
    start_time = receiver.sim_time
    # Function to send message with delay
    delay_ms = random.randint(50, 100)/1000  # Generate random delay between 50 and 100 ms
    while end_of_delay == False:  
        time.sleep(0.05)                 # delay to not update end_time too often, which causes performance issues for larger number of simulated rovers
        end_time = receiver.sim_time
        if end_time - start_time >= delay_ms:
            end_of_delay = True
    
    # Simulate message loss based on COM_LOSS_RATE
    if random.random() < COM_LOSS_RATE:
        # Message is lost - do not deliver it
        return
    
    if end_of_delay:
        receiver.receive_message(obstacle, sender)
        
   