"""Let's see if we can rasterize a polygon."""

from typing import List, Tuple, Union

DiscretePoint = Tuple[int, int]
DiscretePoly = List[DiscretePoint]
Point = Tuple[float, float]
Poly = List[Point]
Raster = List[List[str]]


def display_raster(raster: Raster) -> None:
    for row in raster:
        print(' '.join(row))


def brute_force_raster(poly: Union[DiscretePoly, Poly], resolution: int) -> Raster:
    '''
    All coordinates in `poly` should be in the range [0, resolution).
    '''
    res = []
    for y in reversed(range(resolution)):
        row = []
        for x in range(resolution):
            inside = point_in_polygon(poly, (x, y))
            row.append('+' if inside else '.')
        res.append(row)
    return res


def point_in_polygon(poly: Union[DiscretePoly, Poly], point: DiscretePoint) -> bool:
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
    display_raster(brute_force_raster(triangle, 101))
    display_raster(brute_force_raster(cmplx, 101))


if __name__ == '__main__':
    main()
