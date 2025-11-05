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

from typing import Tuple
from shapely.geometry import LineString, Point
import math

def _to_vec(ls: LineString) -> Tuple[float, float]:
    """Direction vector of a (non-degenerate) LineString based on its endpoints."""
    (x1, y1), (x2, y2) = ls.coords[0], ls.coords[-1]
    return (x2 - x1, y2 - y1)

def _is_parallel(v1: Tuple[float, float], v2: Tuple[float, float], *, tol=1e-12) -> bool:
    """Check if two vectors are parallel (cross product ~ 0)."""
    return abs(v1[0]*v2[1] - v1[1]*v2[0]) <= tol

def _intersection_infinite(p1, p2, q1, q2, *, tol=1e-12) -> Tuple[float, float]:
    """
    Intersection of two infinite lines defined by points p1->p2 and q1->q2.
    Returns (x, y). Raises ValueError if lines are (near-)parallel.
    """
    x1, y1 = p1; x2, y2 = p2
    x3, y3 = q1; x4, y4 = q2
    # Solve:
    # (x1,y1) + t*(x2-x1, y2-y1)  =  (x3,y3) + u*(x4-x3, y4-y3)
    den = (x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4)
    if abs(den) <= tol:
        raise ValueError("Lines are parallel or nearly parallel; no unique intersection.")
    det1 = x1*y2 - y1*x2
    det2 = x3*y4 - y3*x4
    x = (det1*(x3 - x4) - (x1 - x2)*det2) / den
    y = (det1*(y3 - y4) - (y1 - y2)*det2) / den
    return (x, y)

def parallelogram_center_from_parallel_lines(lines1, lines2, *, tol: float = 1e-12) -> Point:
    """
    Given two pairs of parallel Shapely LineStrings (a1//a2 and b1//b2),
    compute the (x,y) point at the center of the parallelogram formed by
    the infinite lines.
    
    Returns a shapely.geometry.Point.

    Notes:
      - Works even if the finite segments do not physically intersect (it uses
        their infinite extensions).
      - Validates parallelism within 'tol'.
    """
    a1 = LineString(lines1[0])
    a2 = LineString(lines1[1])
    b1 = LineString(lines2[0])
    b2 = LineString(lines2[1])
    # Validate non-degenerate lines
    for ls in (a1, a2, b1, b2):
        if len(ls.coords) < 2:
            raise ValueError("Each LineString must have at least 2 coordinates.")
        (x1, y1), (x2, y2) = ls.coords[0], ls.coords[-1]
        if math.hypot(x2 - x1, y2 - y1) <= tol:
            raise ValueError("A LineString is degenerate (zero length).")

    va1 = _to_vec(a1); va2 = _to_vec(a2)
    vb1 = _to_vec(b1); vb2 = _to_vec(b2)

    if not _is_parallel(va1, va2, tol=tol):
        raise ValueError("First pair (a1, a2) are not parallel.")
    if not _is_parallel(vb1, vb2, tol=tol):
        raise ValueError("Second pair (b1, b2) are not parallel.")
    # Ensure the two families are not mutually parallel (otherwise no parallelogram)
    if _is_parallel(va1, vb1, tol=tol):
        raise ValueError("The two line families are parallel to each other; no parallelogram.")

    # Intersections (infinite lines)
    p11 = _intersection_infinite(a1.coords[0], a1.coords[-1], b1.coords[0], b1.coords[-1])
    p12 = _intersection_infinite(a1.coords[0], a1.coords[-1], b2.coords[0], b2.coords[-1])
    p21 = _intersection_infinite(a2.coords[0], a2.coords[-1], b1.coords[0], b1.coords[-1])
    p22 = _intersection_infinite(a2.coords[0], a2.coords[-1], b2.coords[0], b2.coords[-1])

    # Center of a parallelogram = average of all four vertices
    cx = (p11[0] + p12[0] + p21[0] + p22[0]) / 4.0
    cy = (p11[1] + p12[1] + p21[1] + p22[1]) / 4.0
    return (cx, cy)

def find_close_points(set1: list, set2: list, dist, remove_doubles=False):
    close_points = []
    for p1 in set1:
        for p2 in set2:
            p1 = Point(p1)
            p2 = Point(p2)
            if p1.distance(p2) < dist:
                close_points.append(((p1.x+p2.x)/2, (p1.y+p2.y)/2))
                if remove_doubles:
                    set1.remove(p1)
                    set2.remove(p2)
    
    return close_points

def combine_close_points(set1, set2, dist):
    close_points = []
    to_remove = []
    for p1 in set1:
        for p2 in set2:
            p1 = Point(p1)
            p2 = Point(p2)
            if p1.distance(p2) < dist:
                close_points.append(((p1.x+p2.x)/2, (p1.y+p2.y)/2))
                to_remove.append(p1.x,p1.y)
                to_remove.append(p2.x,p2.y)
    
    return close_points - to_remove

def combine_close_points(point_list, dist):
    to_add = []
    to_remove = []
    for i in range(len(point_list)-1):
        for j in range(i+1, len(point_list)):
            p1 = Point(point_list[i])
            p2 = Point(point_list[j])
            if p1.distance(p2) < dist:
                to_add.append(((p1.x+p2.x)/2, (p1.y+p2.y)/2))
                to_remove.append((p1.x,p1.y))
                to_remove.append((p2.x,p2.y))
    point_list = point_list + to_add
    point_list = [p for p in point_list if p not in to_remove]
    return point_list

def find_close_points_by_axis(point_list, dist):
    same_axis_points = []
    segments = []
    for i in range(len(point_list)-1):
        for j in range(i+1, len(point_list)):
            p1 = point_list[i]
            p2 = point_list[j]
            if abs(p1[1] - p2[1]) < dist or abs(p1[0] - p2[0]) < dist:
                same_axis_points.append(p1)
                same_axis_points.append(p2)
                segments.append([p1,p2])
    
    return segments, same_axis_points

from typing import Tuple
from shapely.geometry import LineString, Point, Polygon, box
import math

def _line_normal_and_offset(ls: LineString, *, tol=1e-12) -> Tuple[Tuple[float,float], float]:
    """
    Return a unit normal vector n and offset c for the infinite line of `ls`,
    such that the line is { x | n·x = c } with n unit length.
    """
    (x1, y1), (x2, y2) = ls.coords[0], ls.coords[-1]
    vx, vy = x2 - x1, y2 - y1
    L = math.hypot(vx, vy)
    if L <= tol:
        raise ValueError("Degenerate LineString (zero length).")
    # Unit direction
    ux, uy = vx / L, vy / L
    # A unit normal (rotate +90°)
    nx, ny = -uy, ux
    # Offset: n·p for any point p on the line
    c = nx * x1 + ny * y1
    return (nx, ny), c

def _pair_to_strip(a: LineString, b: LineString, *, M=1e6, tol=1e-12) -> Polygon:
    """
    Convert two parallel lines into a (very long) rectangular strip Polygon bounded by them.
    Uses a long midline segment buffered with square caps to emulate an infinite strip.
    """
    (na, ca) = _line_normal_and_offset(a, tol=tol)
    (nb, cb) = _line_normal_and_offset(b, tol=tol)

    # Ensure normals point in the same (or opposite) direction; make them consistent
    # If dot(n_a, n_b) < 0, flip one so "up" is consistent
    if na[0]*nb[0] + na[1]*nb[1] < 0:
        nb = (-nb[0], -nb[1])
        cb = -cb

    # Check parallelism via cross-product ~ 0
    if abs(na[0]*nb[1] - na[1]*nb[0]) > 1e-10:
        raise ValueError("Lines in a pair are not parallel.")

    # Midline normal & offset
    n = na  # unit
    cmin, cmax = sorted((ca, cb))
    c_mid = 0.5 * (cmin + cmax)
    half_width = 0.5 * (cmax - cmin)

    if half_width <= tol:
        # Practically the same line; use a very thin strip
        half_width = tol

    # A point on the midline: x0 = c_mid * n (since ||n||=1 ⇒ n·x0 = c_mid)
    x0 = (c_mid * n[0], c_mid * n[1])

    # Direction along the strip (parallel to the original lines) is d = rotate -90° of n
    d = (n[1], -n[0])  # unit as well

    # Build a very long segment along the midline and buffer it to make the strip
    L = M  # long enough to cover our big bbox
    p1 = (x0[0] - L * d[0], x0[1] - L * d[1])
    p2 = (x0[0] + L * d[0], x0[1] + L * d[1])
    mid_seg = LineString([p1, p2])
    # Square caps avoid rounded ends interacting oddly with other strips
    strip = mid_seg.buffer(half_width + 1e-9, cap_style=2)
    return strip

def center_of_three_parallel_pairs(
    a1: list, a2: list,
    b1: list, b2: list,
    c1: list, c2: list,
    *,
    bbox_extent: float = 1e6,
    tol: float = 1e-9
) -> Tuple:
    """
    Given three pairs of parallel Shapely LineStrings, compute the (x, y) point
    at the 'middle' of the polygon formed by the intersection of the three strips
    (the regions between each pair). Returns centroid of the intersection polygon.

    Raises:
        ValueError if the intersection is empty or numerically ill-conditioned.
    """
    a1 = LineString(a1)
    a2 = LineString(a2)
    b1 = LineString(b1)
    b2 = LineString(b2)
    c1 = LineString(c1)
    c2 = LineString(c2)
    # Start with a huge bounding box, then clip by each strip
    poly = box(-bbox_extent, -bbox_extent, bbox_extent, bbox_extent)

    for (p, q) in ((a1, a2), (b1, b2), (c1, c2)):
        strip = _pair_to_strip(p, q, M=bbox_extent, tol=tol)
        poly = poly.intersection(strip)
        if poly.is_empty:
            return None
            # raise ValueError("No common intersection region for the three strips.")
        # If intersection returns a MultiPolygon, take its union to keep things clean
        if poly.geom_type == "MultiPolygon":
            poly = poly.buffer(0)

    # If result is Polygon (usual), take centroid; if LineString/Point (degenerate), return that
    if poly.is_empty:
        return None
        # raise ValueError("No common intersection region for the three strips.")
    if poly.geom_type == "Polygon":
        ctr = poly.centroid
    elif poly.geom_type == "MultiPolygon":
        # Choose the largest component’s centroid
        largest = max(poly.geoms, key=lambda g: g.area)
        ctr = largest.centroid
    else:
        # Degenerate cases: intersection is a segment or a point
        ctr = poly.representative_point()

    return (ctr.x, ctr.y)

if __name__ == "__main__":

    # Pair A: horizontal bands y=0 and y=4
    a1 = LineString([(-10, 0), (10, 0)])
    a2 = LineString([(-10, 4), (10, 4)])

    # Pair B: slope +1 lines y=x-1 and y=x+3
    b1 = LineString([(-10, -11), (10, 9)])
    b2 = LineString([(-10, -7),  (10, 13)])

    # Pair C: slope -1 lines y=-x+2 and y=-x+6
    c1 = LineString([(-10, 12), (10, -8)])
    c2 = LineString([(-10, 16), (10, -4)])

    center = center_of_three_parallel_pairs(a1, a2, b1, b2, c1, c2)
    print(center.x, center.y)  # middle of the hexagon (or degenerate polygon)

