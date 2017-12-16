"""
Downloads chunks from an OSM server.

Some geo ranges.

Greater Seattle:
- lon: -122.4275 -- -122.1096
- lat:   47.4290 --   47.7726
"""

# imports
# ---

# builtins
import argparse
import glob
import os
import sys

# 3rd party
import requests


# main
# ---

def scrape(fn: str, left: float, right: float, bottom: float, top: float) -> None:
    # settings
    max_retries = 5
    # url_format = 'http://overpass-api.de/api/map?bbox=-122.3446,47.5970,-122.3150,47.6172'
    url_format = 'http://overpass-api.de/api/map?bbox={:.5f},{:.5f},{:.5f},{:.5f}'

    for attempt in range(max_retries):
        r = requests.get(url_format.format(left, bottom, right, top))
        if r.status_code != 200:
            # retry
            continue

        # success
        print('INFO: Writing to "{}"...'.format(fn))
        with open(fn, 'wb') as f:
            f.write(r.content)
        return

    # at this point, the service is down, connections are bad, our our IP was
    # banned (or something). if this happens, will building in a "start index"
    # into the system to skip the ones already downloaded (and maybe --force to
    # ignore existence of files)
    print('ERROR: failed after {} retries; aborting...'.format(max_retries))
    sys.exit(1)


def scrape_range(
        min_lon: float, min_lat: float, max_lon: float, max_lat: float,
        lon_window: float, lat_window: float, out_dir: str,
        prefix: str) -> None:

    # user friendly: estimate nubmer of requests.
    approx = int((max_lat - min_lat) / lat_window) * int((max_lon - min_lon) / lon_window)
    print('INFO: Will download approximately {} map chunks.'.format(approx))

    # left / right / bottom / top represent the current window
    left = min_lon
    right = left + lon_window
    bottom = min_lat
    top = bottom + lat_window


    # iterate by lon, then lat
    idx = 0
    while top < max_lat:
        fn = os.path.join(out_dir, '{}-{}.osm'.format(prefix, idx))
        scrape(fn, left, right, bottom, top)

        # update window. slide to right if possible.
        left = right
        right = left + lon_window
        if right > max_lon:
            # reset lon
            left = min_lon
            right = left + lon_window
            # move lat up
            bottom = top
            top = bottom + lat_window

        idx += 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'out_dir',
        type=str,
        help='path to output directory to save chunks')
    parser.add_argument(
        'prefix',
        type=str,
        help='name to use for files')
    parser.add_argument(
        'min_lon',
        type=float,
        help='minimum longitude')
    parser.add_argument(
        'min_lat',
        type=float,
        help='minimum latitude')
    parser.add_argument(
        'max_lon',
        type=float,
        help='maximum longitude')
    parser.add_argument(
        'max_lat',
        type=float,
        help='maximum latitude')
    parser.add_argument(
        '--lon_window',
        type=float,
        default=0.00731,
        help='longitude delta per capture window')
    parser.add_argument(
        '--lat_window',
        type=float,
        default=0.00492,
        help='latitude delta per capture window')
    args = parser.parse_args()

    # safety check
    pattern = os.path.join(args.out_dir, args.prefix) + '*'
    if len(glob.glob(pattern)) > 0:
        print('ERROR: Files matching "{}" already exist. Exiting.'.format(pattern))

    # scrape
    scrape_range(
        args.min_lon, args.min_lat, args.max_lon, args.max_lat,
        args.lon_window, args.lat_window, args.out_dir, args.prefix)


if __name__ == '__main__':
    main()
