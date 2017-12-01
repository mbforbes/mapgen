"""
Working with OpenStreetMap XML files.
"""

# imports
import code
from collections import Counter
import os
import xml.etree.ElementTree as ET
from typing import List, Tuple


# TODO: these distinctions worth it?

class MapObj(object):
    features: List[str]

class Node(MapObj):
    point: Tuple[float, float]

class Road(MapObj):
    points: List[Tuple[float, float]]

class Building(MapObj):
    points: List[Tuple[float, float]]


# playing

def convert_polys(
        geo_bounds: Tuple[float, float, float, float],
        pixel_bounds: Tuple[int, int],
        geo_polys: List[List[Tuple[float, float]]]) -> List[List[Tuple[float, float]]]:
    """Converts polys from geo_bounds to pixel_bounds.

    Arguments:
        geo_bounds: minlat, minlon, maxlat, maxlon
        pixel_bounds: width, height
        geo_polys: list of polygons (point lists) in lat, lon format

    Returns:
        pixel_polys: list of polygons (point lists) in x, y pixel format
    """
    minlat, minlon, maxlat, maxlon = geo_bounds
    lonrange = maxlon - minlon
    latrange = maxlat - minlat
    width, height = pixel_bounds

    res = []
    for poly in geo_polys:
        cur = []
        for lat, lon in poly:
            x = ((lon - minlon) / lonrange) * width
            y = ((maxlat - lat) / latrange) * height
            cur.append((x, y))
        res.append(cur)
    return res


def get_features(tag_el: ET.Element) -> List[str]:
    """Gets any features that we're considering and returns them."""
    feature_set = {'building', 'highway', 'water'}
    if 'k' not in tag_el.attrib:
        return []
    key = tag_el.attrib['k']
    if key in feature_set:
        return [key]
    return []


def get_color(features: List[str]) -> str:
    if 'building' in features:
        return 'brown'
    if 'highway' in features:
        return 'yellow'
    if 'water' in features:
        return 'blue'
    return 'lime'


def get_line_width(features: List[str]) -> int:
    # NOTE: this doesn't do what we want yet, as all highways are already
    # yellow!
    if 'highway' in features:
        return 5
    return 1


def render_v2(root: ET.Element, in_path: str):
    # file crap
    title = '.'.join(os.path.basename(in_path).split('.')[:-1])
    out_fn = title + '.html'
    out_path = os.path.join(os.path.dirname(in_path), out_fn)

    # settings
    geo_bounds_el = [child for child in root if child.tag == 'bounds'][0]
    geo_bounds = (
        float(geo_bounds_el.attrib['minlat']),
        float(geo_bounds_el.attrib['minlon']),
        float(geo_bounds_el.attrib['maxlat']),
        float(geo_bounds_el.attrib['maxlon']),
    )
    pixel_bounds = (800, 600)

    # build node mapping (from id -> node)
    node_map = {int(child.attrib['id']): child for child in root if child.tag == 'node'}
    ways = [child for child in root if child.tag == 'way']
    print('INFO: Found {} ways'.format(len(ways)))

    # extract stuff
    # TODO: keep going


def render(root: ET.Element, in_path: str):
    """Just renders OSM tree below root to SVG"""
    # could pass most of the immediate below in if desired

    # file crap
    title = '.'.join(os.path.basename(in_path).split('.')[:-1])
    out_fn = title + '.html'
    out_path = os.path.join(os.path.dirname(in_path), out_fn)

    # settings
    geo_bounds_el = [child for child in root if child.tag == 'bounds'][0]
    geo_bounds = (
        float(geo_bounds_el.attrib['minlat']),
        float(geo_bounds_el.attrib['minlon']),
        float(geo_bounds_el.attrib['maxlat']),
        float(geo_bounds_el.attrib['maxlon']),
    )
    pixel_bounds = (800, 600)

    # build node mapping (from id -> node)
    node_map = {int(child.attrib['id']): child for child in root if child.tag == 'node'}
    ways = [child for child in root if child.tag == 'way']
    print('INFO: Found {} ways'.format(len(ways)))

    # extract polys
    geo_meta_polys = []
    geo_meta_roads = []
    for way in ways:
        # 'points': [(float,float)], 'features': [str] <-- don't know how to get yet
        meta_poly = {
            'points': [],
            'features': [],
        }
        tags, nds = [], []
        for child in way:
            if child.tag == 'tag':
                tags.append(child)
            elif child.tag == 'nd':
                nds.append(child)
            else:
                print('WARNING: Weird sub-way element found: {}'.format(child.tag))

        for tag in tags:
            # get any features from a tag
            meta_poly['features'] += get_features(tag)

        objtype = "obj"
        # roads appear to be not closed.
        if len(nds) >= 2 and nds[0].attrib['ref'] != nds[-1].attrib['ref']:
            objtype = "road"

        for nd in nds:
            # look up the node and add to list of points
            node = node_map[int(nd.attrib['ref'])]
            meta_poly['points'].append((float(node.attrib['lat']), float(node.attrib['lon'])))

        # add to the relevant list
        if objtype == "obj":
            geo_meta_polys.append(meta_poly)
        elif objtype == "road":
            geo_meta_roads.append(meta_poly)

    # get just geo ones for now
    geo_polys = [geo_meta_poly['points'] for geo_meta_poly in geo_meta_polys]
    geo_roads = [geo_meta_road['points'] for geo_meta_road in geo_meta_roads]

    # convert
    pixel_polys = convert_polys(geo_bounds, pixel_bounds, geo_polys)
    pixel_roads = convert_polys(geo_bounds, pixel_bounds, geo_roads)

    # add back in any features
    pixel_meta_polys = []
    for i, geo_meta_poly in enumerate(geo_meta_polys):
        pixel_poly = pixel_polys[i]
        pixel_meta_polys.append({
            'points': pixel_poly,
            'features': geo_meta_poly['features'],
        })
    pixel_meta_roads = []
    for i, geo_meta_road in enumerate(geo_meta_roads):
        pixel_road = pixel_roads[i]
        pixel_meta_roads.append({
            'points': pixel_road,
            'features': geo_meta_road['features'],
        })


    # create doc
    header = '<!DOCTYPE html>\n<html>\n<body>\n\n<svg width="{}" height="{}">\n'.format(*pixel_bounds)
    inner_els = []
    for i, pixel_meta_poly in enumerate(pixel_meta_polys):
        points = ' '.join(','.join(str(coord) for coord in point) for point in pixel_meta_poly['points'])
        inner_els.append(
            '<polygon points="{}" style="fill:{};stroke:black;stroke-width:1" />'.format(
                points,
                get_color(pixel_meta_poly['features'])
            )
        )
    for i, pixel_meta_road in enumerate(pixel_meta_roads):
        points = ' '.join(','.join(str(coord) for coord in point) for point in pixel_meta_road['points'])
        inner_els.append(
            '<polyline points="{}" style="fill:none;stroke:{};stroke-width:{}" />'.format(
                points,
                get_color(pixel_meta_road['features']),
                get_line_width(pixel_meta_road['features']),
            )
        )
    footer = '\n</svg>\n\n</body>\n</html>'

    # write out
    with open(out_path, 'w') as f:
        f.write('\n'.join([header] + inner_els + [footer]))

def tag_dist(els: List[ET.Element]) -> Tuple[Counter, Counter]:
    """Find the distributions of keys and vals """

def detective(root: ET.Element) -> None:
    # basic stats about top-level children
    # ---
    print('\nGeneral\n{}\n'.format('-'*80))

    c = Counter(child.tag for child in root)
    # => Counter({'node': 36072, 'way': 3866, 'relation': 51, 'bounds': 1})

    # Basic types:
    #    - node     = lat/lon point in space (optional altitude). Seem to be
    #                 atoms of OSM.
    #    - way      = ordered list of nodes (ideally >= 2), closed when last ==
    #                 first (should also be annotated; likely want to treat as
    #                 closed when either is true). Open examples: road, stream,
    #                 railway. Closed examples: park, school.
    #    - relation = higher level semantics. Most vague. Examples: bus route,
    #                 turn restriction, waterways (maybe even streets, bridges,
    #                 tunnels)
    #
    # Semantics are given to the above structural elements with tags denoting
    # one or more of a huge set of Map Features:
    # [https://wiki.openstreetmap.org/wiki/Map_Features]

    # From this, my hypothesis is that nodes will haven no children, that ways
    # will have (childless) nodes as children, and relations will have ways or
    # nodes as children. Let's check this out.
    metaset = {}
    for child in root:
        if child.tag not in metaset:
            metaset[child.tag] = Counter()
        for grandchild in child:
            metaset[child.tag][grandchild.tag] += 1
    for tag, grandchildren in metaset.items():
        print(tag, grandchildren)
    # =>
    # bounds Counter()
    # node Counter({'tag': 5380})
    # way Counter({'nd': 39546, 'tag': 19776})
    # relation Counter({'member': 2062, 'tag': 303})

    # bounds
    # ---
    print('\nBounds\n{}\n'.format('-'*80))
    all_bounds = [child for child in root if child.tag == 'bounds']
    print('bounds:', len(all_bounds))
    bounds = all_bounds[0]
    print(bounds.tag, bounds.attrib)

    # way(point) investigation
    # ---
    print('\nWaypoints\n{}\n'.format('-'*80))

    # Hmmm... OK, weird. What are nd? Nodes? How many tags do ways have? Let's
    # investigate...
    children = root.getchildren()
    ways = [child for child in children if child.tag == 'way']
    print('ways:', len(ways))

    # dispaly example way
    print('example way:', ways[0].tag, ways[0].attrib)

    # first, how many tags do ways have?
    way_tags = Counter()
    way_tag_children = Counter()
    for way in ways:
        tags = [child for child in way.getchildren() if child.tag == 'tag']
        way_tags[len(tags)] += 1
        for tag in tags:
            way_tag_children[len(tag.getchildren())] += 1
    print('tags/way:', way_tags)
    # => tags/way: Counter({6: 2561, 2: 683, 1: 245, 10: 98, 3: 55, 4: 53,
    #                       9: 46, 5: 26, 11: 23, 7: 18, 8: 16, 13: 14, 0: 12,
    #                       12: 8, 14: 7, 15: 1})
    # OK, so more than one. I guess each feature is tagged separately.
    print('children/tag of waypoint:', way_tag_children)
    # => children/tag of waypoint: Counter({0: 19776})
    # phew, at least that's as expected. `tag`s are leaves.

    # Let's check out the tag distribution.
    way_tag_keys, way_tag_vals = Counter(), Counter()
    for way in ways:
        tags = [child for child in way if child.tag == 'tag']
        for tag in tags:
            for k, v in tag.attrib.items():
                if k == 'k':
                    way_tag_keys[v] += 1
                elif k == 'v':
                    way_tag_vals[v] += 1
                else:
                    print('WARNING! Weird tag key "{}" found'.format(k))
    print('way tag keys:', way_tag_keys)
    print('way tag vals:', way_tag_vals)

    # Now, let's check out nodes.
    way_nd_children = Counter()
    for way in ways:
        nds = [child for child in way.getchildren() if child.tag == 'nd']
        for nd in nds:
            way_nd_children[len(nd.getchildren())] += 1
    print('children/nd of waypoint:', way_nd_children)
    # => children/nd of waypoint: Counter({0: 39546})
    # phew! also as expected. `nd`s are leaves. Why not call them `node`s...

    # So `nd`s don't have any properties, but I think that they're just
    # references to the top level list of nodes! At least god I hope so.
    found, total = 0, 0
    node_map = {child.attrib['id']: child for child in children if child.tag == 'node'}
    for way in ways:
        nds = [child for child in way.getchildren() if child.tag == 'nd']
        for nd in nds:
            total += 1
            nid = nd.attrib['ref']
            if nid not in node_map:
                print('WARNING! nd {} not found in node list'.format(nid))
            else:
                found += 1
    print('{}/{} `nd`s found in `node` list'.format(found, total))

    # (top-level) node investigation
    # ---
    print('\nNodes\n{}\n'.format('-'*80))

    nodes = [child for child in children if child.tag == 'node']
    print('nodes:', len(nodes))

    # dispaly example node
    print('example node:', nodes[0].tag, nodes[0].attrib)

    # just to confirm that tags of top-level nodes are all leaves
    node_tag_children = Counter()
    for node in nodes:
        # already verified above that tags are the only children of nodes
        tags = node.getchildren()
        for tag in tags:
            node_tag_children[len(tag.getchildren())] += 1
    print('children/tag of node:', node_tag_children)
    # => children/tag of node: Counter({0: 5380})
    # phew! As expected. `tag`s of `node`s are leaves.

    # check out the tag distribution over top-level nodes
    node_tag_keys, node_tag_vals = Counter(), Counter()
    for node in nodes:
        tags = node.getchildren()
        for tag in tags:
            for k, v in tag.items():
                if k == 'k':
                    node_tag_keys[v] += 1
                elif k =='v':
                    node_tag_vals[v] += 1
    # (commenting out for now as they print a lot)
    # print('node tag keys:', node_tag_keys)
    # print('node tag vals:', node_tag_vals)
    # => node tag keys: Counter({'source': 916, 'addr:city': 847,
    #   'addr:housenumber': 847, 'addr:street': 847, 'addr:postcode': 846,
    #   'name': 112, 'highway': 93, 'gtfs:stop_id': 91, 'public_transport': 91,
    #   'ref': 91, 'bus': 54, 'source:addr:id': 51, 'created_by': 50,
    #   'amenity': 39, 'gtfs:dataset_id': 37, 'crossing': 32,
    #   'traffic_calming': 31, 'attribution': 19, 'capacity': 19, 'fee': 19,
    #   'note': 19, 'operator': 19, 'sdot:bike_rack:condition': 19,
    #   'sdot:bike_rack:facility': 19, 'sdot:bike_rack:id': 19,
    #   'sdot:bike_rack:type': 19, 'source:license': 19, 'source:url': 19,
    #   'noexit': 9, 'cuisine': 8, 'ele': 4, 'gnis:feature_id': 4,
    #   'start_date': 4, 'website': 4, 'wheelchair': 4, ...
    #
    # These are mostly metadata that we don't care about. The values are mostly
    #   addresses and build numbers.

    # relations
    # ---

    # I don't think I'm going to investigate relations just yet, as I don't
    # think I'll be dealing with that level of semantics for a while (if ever).


    # play around
    # ---
    code.interact(local=dict(globals(), **locals()))


def main():
    # parse XML tree and get root
    fn = 'data/north-winds.osm'
    tree = ET.parse(fn)
    root = tree.getroot()

    # try to figure out the format
    # detective(root)

    # do some basic renderering
    render(root, fn)


if __name__ == '__main__':
    main()
