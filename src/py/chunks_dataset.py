"""
Building "fill in buildings of chunks of city" dataset.

First candidate lat, lon and pixel sizing:
    * lat:   47.66617 -- 47.67109 range = 0.00492
    * lon: -122.39438 -- -122.38707  range = 0.00731
    * pixels: 500 x 500

Easiest will be to collect map chunks by letting OpenStreetMaps segment off
lat, lon chunks by giving them the range (rather than trying to determine how
to deal with truncating ways and polygons myself). So this code should handle
just a single .osm file at a time.
"""

# imports
# ---

# builtins
from collections import Counter
import code
import os
import typing
from typing import List, Tuple, Set, Dict, Optional

# 3rd party
from tqdm import tqdm

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
        ('water', 'water'),
    ]
    for key, cat in key_categories:
        if key in features:
            return cat

    # secondary: try at more detailed key/vals
    kv_categories = [
        # not a footpath, but an area to walk on
        ('man_made', 'pier', 'walkarea'),

        # things that are "highway"s but for people, not cars
        ('highway', 'path', 'footpath'),
        ('highway', 'steps', 'footpath'),
        ('highway', 'pedestrian', 'footpath'),
        ('highway', 'footway', 'footpath'),
        ('highway', 'track', 'footpath'),

        # parks / greenery
        ('liesure', 'park', 'park'),
        ('landuse', 'meadow', 'park'),
        ('natural', 'wood', 'park'),
    ]
    for key, val, cat in kv_categories:
        if key in features and features[key] == val:
            return cat

    # backup: some have very little info
    backup = [
        ('highway', 'highway'),
        # ('source', 'water'),
    ]
    for key, cat in backup:
        if key in features:
            return cat

    return None


def get_out_path(prefix: str, num: int, out_dir: str) -> str:
    return os.path.join(out_dir, '{}-{}.txt'.format(prefix, num))


def rest_buffer_stringify(rest_buffer: Dict[str, List[str]]) -> str:
    """
    Need to make sure geo objects drawn in particular order so that, e.g.,
    water doesn't get drawn on top of piers.
    """
    res = ''
    order = ['water', 'park', 'highway', 'walkarea', 'footpath']
    ordered_rest = []  # type: List[str]
    for o in order:
        ordered_rest += rest_buffer[o]
    return '\n'.join(ordered_rest)


def process_file(
        in_path: str, a_dir: str, b_dir: str, res: Tuple[int, int],
        prefix: str, num: int) -> bool:
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
    c = Counter()  # type: typing.Counter[str]

    rest_buffer = {
        'highway': [],
        'park': [],
        'walkarea': [],
        'water': [],
        'footpath': [],
    }  # type: Dict[str, List[str]]
    building_buffer = []  # type: List[str]
    for way_el in way_els:
        features = osm.get_way_detailed_features(way_el)
        category = get_category(features)

        # debugging
        for feat_k, feat_v in features.items():
            c['{},{}'.format(feat_k,feat_v)] += 1

        # if the way isn't one of the things we're considering, ignore it
        if category is None:
            continue

        # go from way -> pixels
        way_geo, way_ids = osm.transform_way(node_map, way_el, False)
        way_pixels = geo.convert_points_discrete(
            geo_bounds,
            pixel_bounds,
            way_geo)

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

    # if there were 0 buildings, skip this file.
    if len(building_buffer) == 0:
        # print('Skipping {} (0 buildings found)'.format(in_path))
        return False

    # write out. A gets only rest, B gets rest + buildings
    # print('Writing with {}'.format(in_path))
    rest_str = rest_buffer_stringify(rest_buffer)
    with open(get_out_path(prefix, num, a_dir), 'w') as f:
        f.write(rest_str)
    with open(get_out_path(prefix, num, b_dir), 'w') as f:
        f.write(rest_str)
        f.write('\n'.join(building_buffer))
        f.write('\n')
    return True


def main():
    # settings
    input_range_inclusive = 2966
    out_idx = 0

    for trial_idx in tqdm(range(input_range_inclusive + 1)):
        # try processing it
        success = process_file(
            'data/chunks/osm/seattle-{}.osm'.format(trial_idx),
            'data/chunks/A/',
            'data/chunks/B/',
            (500, 500),
            'seattle',
            out_idx)

        # increase idx if it worked (i.e., > 0 buildings)
        if success:
            out_idx += 1


if __name__ == '__main__':
    main()
