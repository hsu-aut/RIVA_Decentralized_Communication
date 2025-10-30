import numpy as np
from shapely.geometry import Polygon, Point, MultiPolygon, LineString


MIN_DISTANCE = 15

def check_overlap(L1, L2):
    for geofences_in_WM in L2:
        if isinstance(Polygon(geofences_in_WM).union(Polygon(L1)), MultiPolygon):
            continue
        else:
            return True
    return False


def avoiding_WP_generation(geofence_corners, min_distance):
    """
    Generate one new point at each corner of the geofence so that the point is placed on the bisecting angle.
    :param geofence_corners: The vertices of the geofence as a list of tuples [(x1, y1), (x2, y2), ...].
    :param min_distance: The distance from the geofence corners to the new points.
    :return: A list of new points in the format [(x1, y1), (x2, y2), ...].
    """
    new_points = []

    num_corners = len(geofence_corners)
    for i in range(num_corners):
        # Get the current corner and the previous and next corners to form angle bisector
        current_corner = np.array(geofence_corners[i])
        previous_corner = np.array(geofence_corners[(i - 1) % num_corners])
        next_corner = np.array(geofence_corners[(i + 1) % num_corners])

        # Compute the vectors from the current corner to the previous and next corners
        vector_previous = previous_corner - current_corner
        vector_next = next_corner - current_corner

        # Calculate the bisecting angle between the two vectors (using exterior angle bisect)
        bisecting_vector = vector_next / np.linalg.norm(vector_next) + vector_previous / np.linalg.norm(vector_previous)
        bisecting_vector /= np.linalg.norm(bisecting_vector)

        # Compute the new point at a distance of min_distance along the bisecting vector
        new_point = tuple((current_corner - min_distance * bisecting_vector).tolist())

        new_points.append(new_point)

    return new_points


'''
possible_avoiding_WP = [] 
# Beispielaufruf:
L1 = [[(130, 90), (140, 90), (140, 100), (130, 100)], [(1, 1), (1, 2), (2, 2), (2, 1)]] 
L2 = [[(1, 1), (1, 2), (2, 2), (2, 1)]]
L3 = [[(1, 0), (1, 1), (2, 1), (2, 0)]]

for p in L1:
    possible_avoiding_WP.extend(avoiding_WP_generation(p, MIN_DISTANCE))    
    
#print(Polygon(L1).touches(Polygon(L3)))
#print(Polygon(L1).intersects(Polygon(L3)))
#print(Polygon(L1).contains(Polygon(L3)))
print(L1)
print(possible_avoiding_WP)
'''

'''
point = Point(50,85)
point2 = Point(40,85)
point3 = Point(55,85)
line = LineString([point, point2])
obstacle = [(50, 80), (60, 80), (60, 90), (50, 90)]
obstacle_polygon = Polygon(obstacle)

print(obstacle_polygon.contains(point))
print(obstacle_polygon.intersects(point))
print(line.intersects(obstacle_polygon))
print(obstacle_polygon.intersects(line))

print(obstacle_polygon.contains(point3))
print(obstacle_polygon.intersects(point3))
'''

#print(len(obstacles))
