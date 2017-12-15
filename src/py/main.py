# local
import graph
import osm


def main():
    fn = 'data/north-winds.osm'
    node_map, ways, geo_bounds = osm.preproc(fn)


if __name__ == '__main__':
    main()
