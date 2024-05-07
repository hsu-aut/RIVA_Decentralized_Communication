from world.obstacles import OBSTACLES
import random
from shapely import Polygon, Point
from vehicle.communication import *
from vehicle.navigation import *
from vehicle.world_model import *
 
 
MIN_DISTANCE = 15                   # minimal distance for an avoiding WP around an obstacle for Rovers
SPEED = 0.2                         # move speed: 0.1 == 1 m/s == 3,6km/h
MAX_MEMORY_COMM_CANDIDATES = 3      # memory limit for comm_candidates
 
 
# definition of class Rover
class Rover:
    instantiated_rovers = {}
    
    def __init__(self, id, start_position, target_coordinates, WIDTH, HEIGHT, COMM_TYPE, sim_time):
        self.id = id
        self.x, self.y = start_position
        self.target_coordinates = target_coordinates                                            # mission definition: reaching the target
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.comm_type = COMM_TYPE
        self.radius = 10                                                                        # radius for drawing
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))   # colour for drawing
        self.world_model = []                                                                   # internal world model of the rover including obstacles
        self.avoiding_WP = []                                                                   # possible WP to avoid obstacles
        self.move_points = [target_coordinates]                                                 # list of WP that will be used to reach target (initialized with target_coordinat)
        self.comm_candidates = []                                                               # list of candidates that could be communicated when possible
        self.comm_active = True                                                                 # parameter to indicate, if communication is possible at the requested time (only relevant for some communication paradigms)
        Rover.instantiated_rovers[self.id] = self                                               # team registration
        self.counted = False                                                                    # relevant for counting the rovers, which reached the target
        self.reached_target = False                                                             # relevant for counting the rovers, which reached the target
        self.useful_comms = 0                                                                   # relevant for counting usefull communications
        self.not_useful_comms = 0                                                               # relevant for counting not usefull communications
        self.moved_distance = 0                                                                 # distance moved by the rover in meter [m]
        self.sim_time = sim_time                                                                # internal simulation time
        self.elapsed_time_to_target = 0                                                         # elapsed time until target reached [s]
        self.active_communications = 0                                                          # number of communications currently in the network
        self.number_of_known_obstacles = 0                                                      # relevant for evaluation of Environmental Awareness Ratio
        self.distance_to_target = distance_to_target(self.move_points, self.x, self.y)          # distance to target following all move_points
        
                
    def move(self):
        if not self.reached_target:
            if self.move_points:
                current_target_x, current_target_y = self.move_points[0]
            # handling of unlikely error event
            else:
                self.move_points = perform_navigation(self.world_model, self.x, self.y, self.target_coordinates, self.WIDTH, self.HEIGHT, MIN_DISTANCE)
                current_target_x, current_target_y = self.move_points[0]
            #heading to target
            dx = current_target_x - self.x
            dy = current_target_y - self.y
            #distance to target
            distance_next_WP = ((dx ** 2) + (dy ** 2)) ** 0.5
 
            # observation of the world until target is reached
            self.obstacle_detection()
            self.communication()
 
            #WP management
            if distance_next_WP <= 1:  
                self.x = current_target_x
                self.y = current_target_y
                self.move_points.pop(0)  
                if not self.move_points and self.distance_to_target <= 1:
                    self.reached_target = True
                else:
                    self.move_points = perform_navigation(self.world_model, self.x, self.y, self.target_coordinates, self.WIDTH, self.HEIGHT, MIN_DISTANCE)                     # setting back to target, in case of error
            else:
                # moving the rover
                self.x += dx / distance_next_WP * SPEED
                self.y += dy / distance_next_WP * SPEED
                self.moved_distance += ((((dx / distance_next_WP * SPEED) ** 2) + ((dy / distance_next_WP * SPEED) ** 2)) ** 0.5)/10    # /10 as 10units in the world = 1m
                self.distance_to_target = distance_to_target(self.move_points, self.x, self.y)
                       
    def obstacle_detection(self):
        detection_range = Point(self.x, self.y).buffer(25)                              #sensor range
 
        #check if obstacles are in sensor range
        for obstacle in OBSTACLES:
            if detection_range.intersects(Polygon(obstacle)) and not obstacle_in_world_model(obstacle, self.world_model): #detection of unknown obstacle
                
                # update of world model
                self.number_of_known_obstacles += 1
                if len(self.comm_candidates) >= MAX_MEMORY_COMM_CANDIDATES:         # ensuring max length of comm_candidate
                    self.comm_candidates.pop(0)                                     # removal of first element (FIFO)
                self.comm_candidates.append(obstacle)
                world_model_update(obstacle, self.world_model)
                
                # update of navigation if detected obstacle intersects with current path
                if worldmodel_intersects_path(self.world_model, self.move_points, self.x, self.y, MIN_DISTANCE):
                    self.move_points = perform_navigation(self.world_model, self.x, self.y, self.target_coordinates, self.WIDTH, self.HEIGHT, MIN_DISTANCE)                                                    
                
    def communication(self):            
        # perform communication
        if self.comm_type == "No_Comm":
            no_comm()
        elif self.comm_type == "Timing_Selective":
            if self.comm_active and self.comm_candidates:
                self.comm_active = False
                timing_selective_comm(self, self.comm_candidates, self.instantiated_rovers)
        elif self.comm_type == "Content_Selective":
            if self.comm_candidates:
                content_selective_comm(self, self.comm_candidates, self.instantiated_rovers)
        elif self.comm_type == "Receiver_Selective":
            if self.comm_candidates:
                receiver_selective_comm(self, self.comm_candidates, self.instantiated_rovers)
        elif self.comm_type == "Integrated":
            if self.comm_active and self.comm_candidates:
                self.comm_active = False
                integrated_comm(self, self.comm_candidates, self.instantiated_rovers)
        else:
            if self.comm_candidates:
                full_comm(self, self.comm_candidates, self.instantiated_rovers)
                                         
                
    def receive_message(self, obstacle, sender):
        if not self.reached_target:                                 # only receive data if target not reached
            if obstacle_in_world_model(obstacle, self.world_model): #reception of already known obstacle
                self.not_useful_comms += 1
            else:                                                   #reception of unknown obstacle
                # update of world model
                self.number_of_known_obstacles += 1
                world_model_update(obstacle, self.world_model)
 
                # update of navigation if percepted obstacle intersects with current path
                if worldmodel_intersects_path(self.world_model, self.move_points, self.x, self.y, MIN_DISTANCE):   
                    self.move_points = perform_navigation(self.world_model, self.x, self.y, self.target_coordinates, self.WIDTH, self.HEIGHT, MIN_DISTANCE)
                    self.useful_comms += 1
                else:  # not usefull communication
                    self.not_useful_comms += 1
        else:
            self.not_useful_comms += 1  
            
