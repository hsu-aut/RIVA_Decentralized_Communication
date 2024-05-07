import threading
import random
import time
from shapely.geometry import Point, Polygon
 
COMM_DELAY_S = 1.2                                      # communication deactivation in seconds for time-triggered communication
 
def no_comm():
    pass
 
def timing_selective_comm(sender, comm_candidates, instantiated_rovers):
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
 
def content_selective_comm(sender, comm_candidates, instantiated_rovers):
    def content_assessment(sender, comm_candidates):
        selected_comm_candidates = []
        total_distance = sum(instance.distance_to_target for instance in instantiated_rovers.values() if not instance.reached_target)
        num_instances = sum(1 for instance in instantiated_rovers.values() if not instance.reached_target)
        avg_distance_to_target = total_distance / num_instances if num_instances != 0 else 0
            
        for candidate in comm_candidates:
            if Polygon(candidate).distance(Point(sender.target_coordinates)) < avg_distance_to_target:
                selected_comm_candidates.append(candidate)
        return selected_comm_candidates
    
    selected_comm_candidates = content_assessment(sender, comm_candidates)
    if selected_comm_candidates:      
        for comm_candidate in selected_comm_candidates:
            for receiver_id, receiver in instantiated_rovers.items():
                if receiver != sender and not receiver.reached_target:  # Avoid sending message to itself and to instances that reached the target
                    receiver.active_communications += 1
                    threading.Thread(target=delayed_receive_message, args=(receiver, comm_candidate, sender)).start()
        for comm_candidate in selected_comm_candidates:
            sender.comm_candidates.remove(comm_candidate)           # Clear the item of comm_candidates which was just communicated
 
def receiver_selective_comm(sender, comm_candidates, instantiated_rovers):
    def comm_receiver_assessment(sender, instantiated_rovers):
        comm_receiver = []
        for receiver_id, receiver in instantiated_rovers.items():
            if receiver != sender and not receiver.reached_target and receiver.distance_to_target > sender.distance_to_target:
                comm_receiver.append(receiver)
        return comm_receiver
    
    comm_receiver = comm_receiver_assessment(sender, instantiated_rovers)
    if comm_receiver:    
        for comm_candidate in comm_candidates:    
            for receiver in comm_receiver:
                receiver.active_communications += 1
                threading.Thread(target=delayed_receive_message, args=(receiver, comm_candidate, sender)).start()
            sender.comm_candidates.remove(comm_candidate)           # Clear the item of comm_candidates which was just communicated       
 
     
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
    if end_of_delay:
        receiver.receive_message(obstacle, sender)
