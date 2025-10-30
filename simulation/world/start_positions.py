import random
from shapely.geometry import Point, Polygon
from world.obstacles import OBSTACLES

def is_position_in_obstacle(x, y, obstacles):
    """Check if a position (x, y) is inside any obstacle"""
    point = Point(x, y)
    for obstacle in obstacles:
        polygon = Polygon(obstacle)
        if polygon.contains(point):
            return True
    return False

def generate_random_start_positions(num_rovers, obstacles, width, height, min_distance_from_obstacles=15):
    """Generate random start positions that are not in obstacles"""
    positions = {}
    attempts = 0
    max_attempts = 10000  # Prevent infinite loops
    
    for rover_id in range(1, num_rovers + 1):
        position_found = False
        while not position_found and attempts < max_attempts:
            x = random.randint(min_distance_from_obstacles, width - min_distance_from_obstacles)
            y = random.randint(min_distance_from_obstacles, height - min_distance_from_obstacles)
            
            if not is_position_in_obstacle(x, y, obstacles):
                positions[rover_id] = (x, y)
                position_found = True
            attempts += 1
        
        if not position_found:
            # Fallback: use a safe position if no valid position found
            positions[rover_id] = (width // 2, height // 2)
    
    return positions

'''
# Original 10 sets with 10 positions each (unchanged)
START_POSITIONS = [{1: (409, 163), 2: (396, 209), 3: (350, 492), 4: (195, 161), 5: (472, 294), 6: (213, 57), 7: (599, 11), 8: (487, 316), 9: (541, 166), 10: (592, 564)},
                   {1: (508, 69), 2: (82, 451), 3: (585, 78), 4: (86, 168), 5: (337, 594), 6: (581, 197), 7: (277, 533), 8: (354, 485), 9: (514, 15), 10: (90, 327)},
                   {1: (438, 541), 2: (336, 33), 3: (539, 471), 4: (357, 299), 5: (404, 445), 6: (348, 257), 7: (380, 496), 8: (562, 491), 9: (450, 335), 10: (293, 315)},
                   {1: (121, 375), 2: (591, 114), 3: (13, 113), 4: (339, 14), 5: (345, 168), 6: (315, 14), 7: (539, 459), 8: (207, 309), 9: (588, 589), 10: (73, 584)},
                   {1: (364, 259), 2: (4, 551), 3: (192, 231), 4: (594, 526), 5: (342, 509), 6: (474, 464), 7: (267, 133), 8: (379, 375), 9: (573, 498), 10: (26, 579)},
                   {1: (243, 63), 2: (356, 273), 3: (109, 126), 4: (502, 13), 5: (165, 166), 6: (433, 571), 7: (192, 591), 8: (457, 197), 9: (442, 218), 10: (369, 25)},
                   {1: (391, 186), 2: (323, 31), 3: (20, 80), 4: (180, 261), 5: (318, 327), 6: (578, 533), 7: (585, 466), 8: (519, 64), 9: (259, 333), 10: (186, 547)},
                   {1: (134, 325), 2: (579, 534), 3: (506, 290), 4: (13, 220), 5: (41, 536), 6: (231, 297), 7: (128, 583), 8: (480, 35), 9: (348, 473), 10: (457, 451)},
                   {1: (576, 227), 2: (237, 467), 3: (297, 194), 4: (566, 410), 5: (245, 496), 6: (359, 217), 7: (144, 345), 8: (249, 511), 9: (229, 303), 10: (149, 44)},
                   {1: (224, 283), 2: (517, 326), 3: (559, 217), 4: (2, 173), 5: (16, 1), 6: (478, 343), 7: (519, 227), 8: (148, 577), 9: (220, 317), 10: (407, 320)}]
'''


# Generate 10 sets with 50 positions
# Set random seed for reproducible results
random.seed(42)

START_POSITIONS = []
for set_num in range(10):
    random.seed(42 + set_num)  # Different seed for each set
    positions_50 = generate_random_start_positions(50, OBSTACLES, 600, 600, 15)
    START_POSITIONS.append(positions_50)
