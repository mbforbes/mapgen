"""Let's see if we can rasterize a polygon."""

from typing import List, Tuple

DiscretePoint = Tuple[int, int]
DiscretePoly = List[DiscretePoint]
Raster = List[List[str]]


def display_raster(raster: Raster) -> None:
    for row in raster:
        print(' '.join(row))


def brute_force_raster(poly: DiscretePoly) -> Raster:
    res = []
    for y in reversed(range(100)):
        row = []
        for x in range(100):
            inside = point_in_polygon(poly, (x, y))
            row.append('+' if inside else '.')
        res.append(row)
    return res


def point_in_polygon(poly: DiscretePoly, point: DiscretePoint) -> bool:
    x, y = point
    prev_vertex = poly[-1]
    oddNodes = False
    for v_x, v_y in poly:
        pv_x, pv_y = prev_vertex
        if (v_y < y and pv_y >= y) or (pv_y < y and v_y >= y):
            # there might be an intersection.
            if v_x + (y - v_y) / (pv_y - v_y) * (pv_x - v_x) < x:
                oddNodes = not oddNodes
        prev_vertex = (v_x, v_y)
    return oddNodes


def main() -> None:
    triangle = [
        (0, 0),
        (50, 100),
        (100, 0),
    ]
    cmplx = [
        (0, 0),
        (50, 100),
        (100, 50),
        (50, 75),
    ]
    display_raster(brute_force_raster(triangle))
    display_raster(brute_force_raster(cmplx))


if __name__ == '__main__':
    main()
