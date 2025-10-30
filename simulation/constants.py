from world.obstacles import OBSTACLES

# definition of colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
 
# definition of world
WIDTH = 600
HEIGHT = 600
NUMBER_OF_OBSTACLES = len(OBSTACLES)

# internal simulation time step
TIME_STEP = 0.01



'''
Prameters to be chosen by User
'''

# number of simulation cycles
CYCLES = 1                                # 1-10
  
# rover specifics
NUMBER_OF_ROVERS = 3                     # 1-50
COMM_TYPE = "IntCom"                       # choices: NoCom, PlaCom, UtiCom, RecCom, IntCom, FulCom
INITIAL_DISTANCE = 30                     # initial distance to any obstacles
TARGET_COORDINATES = (110, 50)
 
# communication loss rate (0.0 = 0%, 0.04 = 4%, 0.08 = 8%, 0.12 = 12%)
COM_LOSS_RATE = 0.0 