import os
import csv
import numpy as np

def write_rover_times_to_file(COMM_TYPE, NUMBER_OF_ROVERS, data, filename):
    output_folder = os.path.join(os.getcwd(), 'simulation', 'output_logger', 'plotted_data')
    output_path = os.path.join(output_folder, filename)
    with open(output_path, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(["Communication Type: ", COMM_TYPE])
        writer.writerow(["Number of Rovers: ", NUMBER_OF_ROVERS])
        writer.writerow([])
        max_length = max(len(d) for d in data)
        writer.writerow([f'Cycle {i+1}' for i in range(max_length)])
        for item in data:
            writer.writerow(item)

def write_data_to_file(COMM_TYPE, CYCLES, NUMBER_OF_ROVERS, data, filename):
    output_folder = os.path.join(os.getcwd(), 'simulation', 'output_logger', 'plotted_data')
    output_path = os.path.join(output_folder, filename)
       
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(["Communication Type: ", COMM_TYPE])
        writer.writerow(["Number of Rovers: ", NUMBER_OF_ROVERS])
        writer.writerow([])
        
        header_row = []
        for i in range(CYCLES * 2 - 1):
            if i % 2 == 0:
                header_row.append(f'Cycle {i//2 + 1}')
            else:
                header_row.append('')
        writer.writerow(header_row)
                 
        for elements in zip(*data):
            formatted_elements = []
            for i, element in enumerate(elements):
                if i % 2 == 0:
                    formatted_elements.append("{:.2f}".format(element))
                else:
                    formatted_elements.append(element)
            writer.writerow(formatted_elements)
        
def store_rover_times(rovers, rover_times, useful_comms, not_useful_comms):
    for rover in rovers:
        rover_times[rover.id - 1].append(round(rover.elapsed_time_to_target))
    rover_times[-2].append(useful_comms)
    rover_times[-1].append(not_useful_comms)