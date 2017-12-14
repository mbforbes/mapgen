"""
Building "block w/ buildings" dataset.
"""

# builtins
import argparse
import code
from typing import Dict, Set, Tuple, List, FrozenSet

# 3rd party
from tqdm import tqdm

# local
import buildings
import graph
import osm
from polygon import DiscretePoly


def match_buildings_blocks(
        building_pixels: List[DiscretePoly],
        block_pixels: List[DiscretePoly]) -> Dict[int, List[int]]:
    """
    Returns: mapping from block index to list of building indices that are
        inside of it.
    """
    res = {}  # type: Dict[int, List[int]]

    # check each against the other
    for i, block in enumerate(tqdm(block_pixels)):
        res[i] = []
        for j, building in enumerate(building_pixels):
            if graph.polygon_contains(block, building):
                res[i].append(j)

    return res


def gen_for_file(in_fn: str, out_dir: str, ir_w: int, ir_h: int, res: int) -> None:
    intermediate_resolution = (ir_w, ir_h)

    node_map, ways, geo_bounds = osm.preproc(in_fn)

    # blocks
    print('Extracting blocks...')
    g = graph.build(node_map, ways)
    block_geos, block_refs, block_pixels = graph.find_blocks(g, node_map, geo_bounds, intermediate_resolution)

    # buildings
    print('Extracting buildings...')
    building_geos, building_refs = buildings.get(node_map, ways)
    building_pixels = graph.geo_ways_to_pixel_coords(building_geos, geo_bounds, intermediate_resolution)

    # find buildings in blocks
    print('Matching buildings to blocks...')
    block_map = match_buildings_blocks(building_pixels, block_pixels)

    # TODO: render
    code.interact(local=dict(globals(), **locals()))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'in_fn',
        type=str,
        help='path to input osm file')
    parser.add_argument(
        'out_dir',
        type=str,
        help='path to output directory to save images')
    parser.add_argument(
        '--out_res',
        type=int,
        default=250,
        help='output image resolution in pixels (per side)')
    parser.add_argument(
        '--ir_w',
        type=int,
        default=800,
        help='intermediate resolution (for raster tests): width')
    parser.add_argument(
        '--ir_h',
        type=int,
        default=600,
        help='intermediate resolution (for raster tests): height')
    args = parser.parse_args()

    gen_for_file(args.in_fn, args.out_dir, args.ir_w, args.ir_h, args.out_res)


if __name__ == '__main__':
    main()
