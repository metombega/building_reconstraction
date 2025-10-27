from shapely.geometry import LineString
from shapely.strtree import STRtree

def count_crossings(
    seg, segments,
    include_endpoints=True,   # count intersections that only touch at endpoints
    include_colinear=True     # count colinear overlaps as “crossings”
):
    """
    seg: ((x1,y1),(x2,y2))
    segments: iterable of ((x1,y1),(x2,y2))
    returns: int
    """
    target = LineString(seg)
    geoms  = [LineString(s) for s in segments]

    # Fast candidate filtering by bbox
    tree = STRtree(geoms)
    candidate_indices = tree.query(target)

    count = 0
    for idx in candidate_indices:
        g = geoms[idx]
        if target.equals(g):
            continue

        if target.crosses(g):
            count += 1
            continue

        if include_endpoints and target.touches(g):
            count += 1
            continue

        if include_colinear:
            inter = target.intersection(g)
            # Any 1D intersection (positive length) counts as colinear overlap,
            # including containment or partial overlap.
            if (inter.geom_type in ("LineString", "MultiLineString")) and inter.length > 0:
                return -1

    return count

if __name__ == "__main__":
    myseg = ((0,0), (0,10))
    segs = [((0,1), (6,6)),((0,2), (-6,-6)),((5,5), (6,6))]
    a = count_crossings(seg=myseg,segments=segs,include_endpoints=True, include_colinear=True)
    print(a)