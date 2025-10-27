from shapely.geometry import Point, LineString

def point_to_line_dist(p, line):
    p = Point(p[0], p[1])
    line = LineString([(line[0][0], line[0][1]), (line[1][0], line[1][1])])

    distance = p.distance(line)
    # print(distance)  # → 4.0
    return distance

def point_to_point_dist(p1, p2):
    p1 = Point(p1)
    p2 = Point(p2)
    return p1.distance(p2)

if __name__ == "__main__":
    print(point_to_line_dist((0,0), ((3,4),(6,6))))