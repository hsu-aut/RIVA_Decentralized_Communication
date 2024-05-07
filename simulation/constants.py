from world.obstacles import OBSTACLES

# definition of colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
 
# definition of world
WIDTH = 600
HEIGHT = 600
NUMBER_OF_OBSTACLES = len(OBSTACLES)

# number of simulation cycles
CYCLES = 1
  
# rover specifics
NUMBER_OF_ROVERS = 2
COMM_TYPE = "Integrated"                  # choices: No_Comm, Timing_Selective, Content_Selective, Receiver_Selective, Integrated, Full_Comm
INITIAL_DISTANCE = 30                     # initial distance to any obstacles
TARGET_COORDINATES = (110, 50)
 
# internal simulation time step
TIME_STEP = 0.01 