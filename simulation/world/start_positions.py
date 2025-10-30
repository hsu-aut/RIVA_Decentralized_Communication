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

# Generate 10 sets with 50 positions
# Set random seed for reproducible results
random.seed(42)

START_POSITIONS = []
for set_num in range(10):
    random.seed(42 + set_num)  # Different seed for each set
    positions_50 = generate_random_start_positions(50, OBSTACLES, 600, 600, 15)
    START_POSITIONS.append(positions_50)
