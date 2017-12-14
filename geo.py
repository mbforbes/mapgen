# imports
# ---

import math
from typing import List, Tuple


# types
# ---

Point = Tuple[float, float]
DiscretePoint = Tuple[int, int]
Polygon = List[Point]
Line = Tuple[Point, Point]
Polyline = List[Point]


# code
# ---

def get_geo_range(geo_polys: List[Polygon]) -> Tuple[float, float, float, float]:
    """Returns (minlat, minlon, maxlat, maxlon)"""
    minlat, minlon, maxlat, maxlon = 90.0, 180.0, -90.0, -180.0
    for geo_poly in geo_polys:
        for lat, lon in geo_poly:
            minlat = min(minlat, lat)
            minlon = min(minlon, lon)
            maxlat = max(maxlat, lat)
            maxlon = max(maxlon, lon)
    return (minlat, minlon, maxlat, maxlon)


def convert_poly(geo_poly: Polygon, pixel_bounds: Tuple[int, int]) -> Polygon:
    """
    Converts geo_poly from geo (lat, lon) space to pixel (x, y) space, where if
    px, py = pixel_bounds, the pixel coordinates will range [0, px), [0, py);
    i.e., pixel_bounds are exclusive so that the resulting image size is
    exactly pixel_bounds.
    """
    geo_bounds = get_geo_range([geo_poly])

    # shift pixel bounds by -1, -1 because the other methods are inclusive
    px, py = pixel_bounds
    shifted_pixel_bounds = (px - 1, py - 1)

    # note: scaling both x and y to same amount even though the shape may not
    # have square bounds. because of this, we learn shapes in a scale-invariant
    # way, and then pick the bounding boxes separately. we could change this to
    # respect the lat/lon ratio, but lat & lon do not map to pixels the same
    # way (this is globe location-dependent).
    return convert_points(geo_bounds, shifted_pixel_bounds, geo_poly)


def convert_points_discrete(
        geo_bounds: Tuple[float, float, float, float],
        pixel_bounds: Tuple[int, int],
        geo_points: List[Point],
        flip_y: bool = True) -> List[DiscretePoint]:
    pts = convert_points(geo_bounds, pixel_bounds, geo_points, flip_y)
    return [(int(math.floor(p[0])), int(math.floor(p[1]))) for p in pts]


def convert_points(
        geo_bounds: Tuple[float, float, float, float],
        pixel_bounds: Tuple[int, int],
        geo_points: List[Point],
        flip_y: bool = True) -> List[Point]:
    minlat, minlon, maxlat, maxlon = geo_bounds
    lonrange = maxlon - minlon
    latrange = maxlat - minlat
    width, height = pixel_bounds

    res = []
    for lat, lon in geo_points:
        x = ((lon - minlon) / lonrange) * width
        # we may flip_y because SVG coordinate system has 0,0 at top left.
        if flip_y:
            y = ((maxlat - lat) / latrange) * height
        else:
            y = abs(((lat - maxlat) / latrange) * height)
        res.append((x, y))
    return res


def convert_polys(
        geo_bounds: Tuple[float, float, float, float],
        pixel_bounds: Tuple[int, int],
        geo_polys: List[Polygon]) -> List[Polygon]:
    """Converts polys from geo_bounds to pixel_bounds.

    Arguments:
        geo_bounds: minlat, minlon, maxlat, maxlon
        pixel_bounds: width, height
        geo_polys: list of polygons (point lists) in lat, lon format

    Returns:
        pixel_polys: list of polygons (point lists) in x, y pixel format
    """
    return [convert_points(geo_bounds, pixel_bounds, poly) for poly in geo_polys]
