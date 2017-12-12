# imports
# ---

# builtins
from typing import List, Tuple, Set, Dict, Union

# local
from geo import Point, Line, Polyline, Polygon


# code
# ---

def header(pixel_bounds: Tuple[float, float]) -> str:
    return '<!DOCTYPE html>\n<html>\n<body>\n\n<svg width="{}" height="{}">\n'.format(
        *pixel_bounds)


def footer() -> str:
    return '\n</svg>\n\n</body>\n</html>'


def polygons(polygons: List[Polygon], color: str = '#ef8a62') -> str:
    els = []
    for polygon in polygons:
        points = ' '.join(','.join(str(coord) for coord in point) for point in polygon)
        els.append(
            '<polygon points="{}" style="fill:{};stroke:black;stroke-width:1" fill-opacity="0.4"/>'.format(
                points,
                color,
            )
        )
    return '\n'.join(els)


def lines(lines: Union[List[Polyline], List[Line]], color: str = '#b2df8a', line_width: int = 3) -> str:
    """
    Note: This works for lists of either lines or polylines (i.e., it doesn't
    care how many points are in the line).
    """
    els = []  # type: List[str]
    for line in lines:
        points = ' '.join(','.join(str(coord) for coord in point) for point in line)
        els.append(
            '<polyline points="{}" style="fill:none;stroke:{};stroke-width:{}" />'.format(
                points,
                color,
                line_width,
            )
        )
    return '\n'.join(els)


def circles(points: List[Point], color: str = '#1f78b4', r: int = 3) -> str:
    els = []  # type: List[str]
    for x, y in points:
        els.append(
            '<circle cx="{}" cy="{}" r="{}" fill="{}" stroke="black" />'.format(
                x, y, r, color
            )
        )
    return '\n'.join(els)
