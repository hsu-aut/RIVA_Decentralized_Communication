from shapely import Polygon, MultiPolygon

def obstacle_in_world_model(O1, O2):
    """
    Checks if obstacle O1 is already included in obstacle O2 (world model)
    """
    new_polygon = Polygon(O1)
    for obstacles_in_WM in O2:
        if Polygon(obstacles_in_WM).contains(new_polygon):
            return True
    return False

def world_model_update(O1, O2):
    """
    Updates (appends) the World Model O2 with the obstacle O1
    """
    if check_overlap(O1, O2):
        i = overlap_index(O1, O2)
        O2[i] = merge(O1, O2[i])
    else:
        O2.append(O1)

def check_overlap(O1, O2):
    """
    Checks if obstacle O1 overlaps with obstacle O2 (world model)
    """
    for obstacles_in_WM in O2:
        if isinstance(Polygon(O1).union(Polygon(obstacles_in_WM)), MultiPolygon):
            continue
        else:
            return True
    return False

def overlap_index(O1, O2):
    for i, geofences_in_WM in enumerate(O2):
        if isinstance(Polygon(O1).union(Polygon(geofences_in_WM)), MultiPolygon):
            continue
        else:
            return i

def merge(O1, O2):
    """
    Merges obstacle O1 with obstacle O2 (world model)
    """
    polygon1 = Polygon(O1)
    polygon2 = Polygon(O2)
    merged_polygon = polygon1.union(polygon2)
    simplified_merged_polygon = merged_polygon.simplify(tolerance=1, preserve_topology=False) #get rid of multiple points on the same line
    merged_polygon_points = list(simplified_merged_polygon.exterior.coords)         
    merged_polygon_points.pop()
    if len(merged_polygon_points) == 5:                 #ensuring that a merged obstacle only includes 4 points
        merged_polygon_points.pop()
    return merged_polygon_points
    
