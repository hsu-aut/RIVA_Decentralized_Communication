import random
from shapely.geometry import Point, Polygon
from vehicle.navigation import avoiding_WP_generation

def generate_random_start_positions(num_positions, obstacles, WIDTH, HEIGHT, INITIAL_DISTANCE):
    start_positions = []
    obstacle_polygons = [Polygon(avoiding_WP_generation(obstacle, INITIAL_DISTANCE)) for obstacle in obstacles]

    while len(start_positions) < num_positions:
        # generate random coordinates
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        
        # check whether the generated point does not intersect an obstacle
        point = Point(x, y)
        inside_obstacle = False
        for obstacle_polygon in obstacle_polygons:
            if obstacle_polygon.intersects(point):
                inside_obstacle = True
                break
        
        if not inside_obstacle:
            start_positions.append((x, y))
    
    start_positions_dict = {i+1: pos for i, pos in enumerate(start_positions)}
    return start_positions_dict
