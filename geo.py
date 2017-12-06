# imports
# ---

from typing import List, Tuple


# types
# ---

Point = Tuple[float, float]
Line = Tuple[Point, Point]
Polyline = List[Line]


# code
# ---

def convert_points(
        geo_bounds: Tuple[float, float, float, float],
        pixel_bounds: Tuple[int, int],
        geo_points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    minlat, minlon, maxlat, maxlon = geo_bounds
    lonrange = maxlon - minlon
    latrange = maxlat - minlat
    width, height = pixel_bounds

    res = []
    for lat, lon in geo_points:
        x = ((lon - minlon) / lonrange) * width
        # note that y is different because SVG coordinate system has 0,0 at top
        # left.
        y = ((maxlat - lat) / latrange) * height
        res.append((x, y))
    return res


def convert_polys(
        geo_bounds: Tuple[float, float, float, float],
        pixel_bounds: Tuple[int, int],
        geo_polys: List[List[Tuple[float, float]]]) -> List[List[Tuple[float, float]]]:
    """Converts polys from geo_bounds to pixel_bounds.

    Arguments:
        geo_bounds: minlat, minlon, maxlat, maxlon
        pixel_bounds: width, height
        geo_polys: list of polygons (point lists) in lat, lon format

    Returns:
        pixel_polys: list of polygons (point lists) in x, y pixel format
    """
    return [convert_points(geo_bounds, pixel_bounds, poly) for poly in geo_polys]
