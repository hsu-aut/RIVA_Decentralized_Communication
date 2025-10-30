from constants import *
from world.obstacles import OBSTACLES
from world.start_positions import START_POSITIONS
from world.functions import *
from vehicle.rover.rover import Rover
from vehicle.draw_functions import *
from output_logger.functions import *
import pygame
 

def main():
    pygame.init()
 
    # initialising the screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Rover Simulator")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 16)
    
 
    rover_times_data = [[] for i in range(NUMBER_OF_ROVERS+3)]          # list to store the elapsed time to reach the target per rover and the performed communications
    network_load_data = [[0] for i in range(CYCLES * 2)]                # list to store the network load per time
    
    for sim_cycle in range(CYCLES):
        # rover startpositions
        #START_POSITIONS = {1: (125, 50), 2: (165, 50), 3: (250, 450), 4: (480, 440), 5: (480, 560), 6: (40, 550), 7: (30, 40), 8: (90, 330), 9: (390, 130), 10: (570, 580)}
        #START_POSITIONS = {1: (150, 170), 2: (520, 310), 3: (250, 450), 4: (480, 440), 5: (480, 560), 6: (40, 550), 7: (30, 40), 8: (90, 330), 9: (390, 130), 10: (570, 580)}
        #START_POSITIONS = generate_random_start_positions(NUMBER_OF_ROVERS, OBSTACLES, WIDTH, HEIGHT, INITIAL_DISTANCE)
        start_time = pygame.time.get_ticks()
                    
        # initialising count variables
        simulation_time = 0                           
        number_of_rovers_in_target = 0
        useful_comms = 0
        not_useful_comms = 0
        
        # generating rover instances
        rovers = [Rover(ID, START_POSITIONS[sim_cycle][ID], TARGET_COORDINATES, WIDTH, HEIGHT, COMM_TYPE, simulation_time) for ID in range(1, NUMBER_OF_ROVERS + 1)]
                    
        # Main loop
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            screen.fill(WHITE)
            
            # Draw the target and obstacles
            pygame.draw.rect(screen, BLACK, (TARGET_COORDINATES[0]-6, TARGET_COORDINATES[1]-6, 20, 20))
            text_surface = font.render("G", True, WHITE)
            screen.blit(text_surface, (TARGET_COORDINATES[0]-3, TARGET_COORDINATES[1]-3))
            for obstacle in OBSTACLES:
                pygame.draw.polygon(screen, RED, obstacle)
            
            # move and draw the rovers
            
            for rover in rovers:
                rover.move()
                rover.sim_time = simulation_time
                draw_rover(rover, screen)
                draw_path(rover, screen)
                
                # Check if rover has reached the target
                if rover.reached_target and not rover.counted:
                    number_of_rovers_in_target += 1
                    rover.counted = True
                    rover.elapsed_time_to_target = simulation_time
                    print(f"Elapsed simulated time until Rover {rover.id} has reached the target: {rover.elapsed_time_to_target:.1f}s")
                    
                    # Check if all rovers have reached the target
                    if number_of_rovers_in_target >= NUMBER_OF_ROVERS:
                        for rover in rovers:
                            useful_comms += rover.useful_comms
                            not_useful_comms += rover.not_useful_comms
                        print("All Rovers have reached the target!")
                        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000  
                        print(f"Elapsed real time: {elapsed_time:.1f}s")
                        print("Number of useful communications: ", useful_comms)
                        print("Number of not useful communications: ", not_useful_comms)
                        running = False          
            simulation_time += TIME_STEP                            
                       
            #storing the network load and mean EAR every full second
            if round(simulation_time, 2) == round(simulation_time):
                active_communications = sum(rover.active_communications for rover in rovers)
                network_load_data[2*sim_cycle].append(simulation_time)
                network_load_data[2*sim_cycle+1].append(active_communications)
                for rover in rovers:
                    
                    rover.active_communications = 0
 
                mean_of_known_obstacles = sum(rover.number_of_known_obstacles for rover in rovers)/NUMBER_OF_ROVERS
                
            pygame.display.flip()
            clock.tick(50)
        
        #storing the elapsed simulation time per rover until reaching target + number of communications after each simulation cycle
        store_rover_times(rovers, rover_times_data, useful_comms, not_useful_comms)
       
    #saving data to csv files after all simulation cycles        
    write_rover_times_to_file(COMM_TYPE, NUMBER_OF_ROVERS, rover_times_data, 'rover_times_data.csv')
    write_data_to_file(COMM_TYPE, CYCLES, NUMBER_OF_ROVERS, network_load_data, 'network_load_data.csv')
    
    pygame.quit()
 
if __name__ == "__main__":
    main()