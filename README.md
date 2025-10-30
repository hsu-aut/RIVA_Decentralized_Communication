# RIVA_Decentralized_Communication

## Preliminaries:
  1. Install necessary requirements --> pip install requirements.txt

## Using the Map Generator:
  1. Open the file "map.xlsx" and define the positions of obstacles
       - Black cells will be obstacles
       - White cells will be free of obstacles
  2. Open the folder "map_generator" in your Integrated Development Environments (IDE), i.e. VS Code
  3. Run the file "map_generator.py" --> a list with the coordinates of the obstacles will be generated --> obstacles.py
  4. Copy the file into the folder "simulation/world"

## Using the Simulation:
  1. Open the folder "simulation" in your IDE
  2. Configure your individual simulation in the file constants.py
       - CYCLES: 1-10, defining how many simulation cycles shall be performed
       - NUMBER_OF_ROVERS: 2-50, defining how many rovers shall be included
       - COMM_TYPE: [NoCom, PlaCom, UtiCom, RecCom, IntCom, FulCom], defining the communication type for the simulation cycles
       - further configuration parameters, if necessary
  3. run the file "main.py"
  4. The simulation output data will be saved in several files in simulation/output_logger/plotted_data

Enjoy!
