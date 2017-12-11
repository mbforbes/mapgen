"""
Extracting buildings from map file(s)
"""

# imports
# ---

# builtins
import code
from typing import List, Tuple

# 3rd party
from tqdm import tqdm

# local
import geo
import osm
import polygon


def main():
    fn = 'data/north-winds.osm'
    res = 100

    node_map, ways, geo_bounds = osm.preproc(fn)
    print('Extracting buildings')
    buildings = [way for way in ways if 'building' in osm.get_way_features(way)]
    print('Extracting geo polys')
    geo_polys = [osm.way_to_geo_poly(node_map, b) for b in buildings]
    print('Converting to pixel polys')
    pixel_polys = [geo.convert_poly(g, (res, res)) for g in geo_polys]
    print('Rasterizing pixel polys')
    rasters = [polygon.brute_force_raster(p, res) for p in tqdm(pixel_polys)]
    d = polygon.display_raster
    d(rasters[0])
    code.interact(local=dict(globals(), **locals()))


if __name__ == '__main__':
    main()
