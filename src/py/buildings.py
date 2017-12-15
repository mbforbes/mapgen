"""
Extracting buildings from map file(s)
"""

# imports
# ---

# builtins
import code
import pickle
from typing import List, Tuple, Dict
import xml.etree.ElementTree as ET

# 3rd party
from PIL import Image
from tqdm import tqdm

# local
import geo
import osm
import polygon


def str_raster_to_bin(raster: List[List[str]]) -> List[Tuple[int,int,int]]:
    res = []
    for line in raster:
        for symbol in line:
            res.append((0,0,0) if symbol == '+' else (255,255,255))
    return res


def get(
        node_map: Dict[int, ET.Element],
        ways: List[ET.Element]) -> Tuple[List[List[Tuple[float, float]]], List[List[int]]]:
    """
    Retrieve buildings.
    """
    buildings_raw = [way for way in ways if 'building' in osm.get_way_features(way)]
    building_geos, building_refs = osm.transform_ways(node_map, buildings_raw)
    return building_geos, building_refs


def test_build():
    fn = 'data/north-winds.osm'
    res = 100

    node_map, ways, geo_bounds = osm.preproc(fn)
    print('Extracting buildings')
    buildings = [way for way in ways if 'building' in osm.get_way_features(way)]
    print('Extracting geo polys')
    geo_polys, _ = osm.transform_ways(node_map, buildings)
    print('Converting to pixel polys')
    pixel_polys = [geo.convert_poly(g, (res, res)) for g in geo_polys]
    print('Rasterizing pixel polys')
    rasters = [polygon.brute_force_raster(p, res) for p in tqdm(pixel_polys)]
    d = polygon.display_raster
    d(rasters[0])
    code.interact(local=dict(globals(), **locals()))


def test_render():
    res = 100
    fn = 'data/north-winds-building-str-rasters.pkl'
    with open(fn, 'rb') as f:
        str_rasters = pickle.load(f)

    for i, r in enumerate(str_rasters):
        img = Image.new('RGB', (res, res))
        img.putdata(str_raster_to_bin(r))
        img.save('data/buildings/nw-{}.png'.format(i))


def main():
    # test_build()
    test_render()


if __name__ == '__main__':
    main()
