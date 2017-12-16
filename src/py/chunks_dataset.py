"""
Building "fill in buildings of chunks of city" dataset.

First candidate lat, lon and pixel sizing: * lat:   47.66617 -- 47.67109
    range = 0.00492 * lon: -122.39438 -- -122.38707  range = 0.00731 * pixels:
    500 x 500

Easiest will be to collect map chunks by letting OpenStreetMaps segment off
lat, lon chunks by giving them the range (rather than trying to determine how
to deal with truncating ways and polygons myself). So this code should handle
just a single .osm file at a time.
"""

# imports
# ---

# builtins
from collections import Counter
import os
import typing
from typing import List, Tuple, Set, Dict, Optional

# local
import geo
import osm
import polygon


# functions
# ---

def get_category(features: Dict[str, str]) -> Optional[str]:
    """
    From the set of way features, returns a single one as the category.

    This is probably overkill, as we'll likely only have one, but we have to
    make sure that we pick one.
    """
    # priority order. maps feature key to its category
    key_categories = [
        ('building', 'building'),
        ('highway', 'highway'),
        ('water', 'water'),
    ]
    for key, cat in key_categories:
        if key in features:
            return cat

    # secondary: try at more detailed key/vals
    kv_categories = [
        ('man_made', 'pier', 'walkway'),
    ]
    for key, val, cat in kv_categories:
        if key in features and features[key] == val:
            return cat

    # backup: some have very little info
    backup = [
        ('source', 'water')
    ]
    for key, cat in backup:
        if key in features:
            return cat

    return None


def get_out_path(in_path: str, out_dir: str) -> str:
    prefix, _ = os.path.basename(in_path).split('.')
    return os.path.join(out_dir, '{}.txt'.format(prefix))


def rest_buffer_stringify(rest_buffer: Dict[str, List[str]]) -> str:
    """
    Need to make sure geo objects drawn in particular order so that, e.g.,
    water doesn't get drawn on top of piers.
    """
    res = ''
    order = ['water', 'highway', 'walkway']
    for o in order:
        res += '\n'.join(rest_buffer[o]) + '\n'
    return res


def process_file(in_path: str, a_dir: str, b_dir: str, res: Tuple[int, int]) -> None:
    """
    want:
    - list of ways. for each way:
       - feature, [pixel points]
    """
    # setup
    res_w, res_h = res
    pixel_bounds = (res_w - 1, res_h - 1)
    node_map, way_els, geo_bounds = osm.preproc(in_path)

    # debugging
    # c = Counter()  # type: typing.Counter[str]

    rest_buffer = {
        'highway': [],
        'walkway': [],
        'water': [],
    }
    building_buffer = []  # type: List[str]
    for way_el in way_els:
        features = osm.get_way_detailed_features(way_el)
        category = get_category(features)

        # debugging
        # for feat in features:
        #     c[feat] += 1

        # if the way isn't one of the things we're considering, ignore it
        if category is None:
            continue

        # go from way -> pixels
        way_geo, way_ids = osm.transform_way(node_map, way_el, False)
        way_pixels = geo.convert_points_discrete(
            geo_bounds,
            pixel_bounds,
            way_geo)

        # TODO: maybe try not flipping y

        # TODO: see if we need to clamp pixels to range (processing might
        # handle w/ out-of-domain renders just not being visible)

        # get out representation
        line = '{};{}'.format(
            category,
            polygon.poly2str(way_pixels))

        # write out to desired buffer
        if category == 'building':
            building_buffer.append(line)
        else:
            rest_buffer[category].append(line)

    # debug output
    # print('Geo features found:')
    # for feat, freq in c.most_common():
    #     print('{} \t {}'.format(freq, feat))

    # write out. A gets only rest, B gets rest + buildings
    rest_str = rest_buffer_stringify(rest_buffer)
    with open(get_out_path(in_path, a_dir), 'w') as f:
        f.write(rest_str)
    with open(get_out_path(in_path, b_dir), 'w') as f:
        f.write(rest_str)
        f.write('\n'.join(building_buffer))
        f.write('\n')


def main():
    # tmp: see how well we're doing
    process_file('data/chunk-test-1.osm', 'data/chunks/A/', 'data/chunks/B/', (500, 500))


if __name__ == '__main__':
    main()
