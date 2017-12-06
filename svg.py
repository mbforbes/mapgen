# imports
# ---

# builtins
from typing import List, Tuple, Set, Dict

# local
from geo import Line, Point


# code
# ---

def header(pixel_bounds: Tuple[float, float]) -> str:
    return '<!DOCTYPE html>\n<html>\n<body>\n\n<svg width="{}" height="{}">\n'.format(
        *pixel_bounds)


def footer() -> str:
    return '\n</svg>\n\n</body>\n</html>'


def lines(lines: List[Line], color: str = '#b2df8a', line_width: int = 3) -> str:
    """
    Note: This would also work for polylines, e.g, List[List[Point]] instead of List[Line]
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
