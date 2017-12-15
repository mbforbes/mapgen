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


def main():
    # TODO: this!
    pass


if __name__ == '__main__':
    main()
