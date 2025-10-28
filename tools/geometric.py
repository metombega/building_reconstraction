from shapely.geometry import Point, LineString
# import shapely

def point_to_line_dist(p, line):
    p = Point(p)
    line = LineString(line)
    distance = p.distance(line)
    return distance

def point_to_point_dist(p1, p2):
    p1 = Point(p1)
    p2 = Point(p2)
    return p1.distance(p2)

def lines_are_overlap(line1, line2):
    intersection = LineString(line1).intersection(LineString(line2))
    return intersection.length > 0

if __name__ == "__main__":
    print(point_to_line_dist((0,0), ((3,4),(6,6))))
    line1 = [(3, 5), (5, 5)]
    line2 = [(3, 5), (5, 5)]
    intersection = LineString(line1).intersection(LineString(line2))
    is_overlap = intersection.length > 0
    print(is_overlap)
