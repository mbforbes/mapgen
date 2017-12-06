"""
Working with OpenStreetMap XML files.
"""

# imports
# ---

# builtin
import code
from collections import Counter
import os
from math import sqrt
import random
from typing import List, Tuple, Set, Dict
import xml.etree.ElementTree as ET

# local
import geo


# TODO: Make high level format some day so other modules don't have to deal
# with elements.

# class MapObj(object):
#     features: List[str]

# class Node(MapObj):
#     point: Tuple[float, float]

# class Road(MapObj):
#     points: List[Tuple[float, float]]

# class Building(MapObj):
#     points: List[Tuple[float, float]]


# playing

def get_way_features(way_el: ET.Element) -> Set[str]:
    """Gets any features that we're considering and returns them.

    TODO: eventually belongs in OSM
    """
    features = set()
    for child in way_el:
        if child.tag == 'tag':
            features.update(get_tag_features(child))
    return features


def get_tag_features(tag_el: ET.Element) -> Set[str]:
    """Gets any features that we're considering and returns them.

    TODO: eventually belongs in OSM
    """
    feature_set = {'building', 'highway', 'water'}
    if 'k' not in tag_el.attrib:
        return set()
    key = tag_el.attrib['k']
    if key in feature_set:
        return set([key])
    return set()


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

def get_geo_bounds(root: ET.Element) -> Tuple[float, float, float, float]:
    """
    Returns minlat, minlon, maxlat, maxlon
    """
    geo_bounds_el = [child for child in root if child.tag == 'bounds'][0]
    return (
        float(geo_bounds_el.attrib['minlat']),
        float(geo_bounds_el.attrib['minlon']),
        float(geo_bounds_el.attrib['maxlat']),
        float(geo_bounds_el.attrib['maxlon']),
    )

def render_v2(root: ET.Element, in_path: str):
    # file crap
    title = '.'.join(os.path.basename(in_path).split('.')[:-1])
    out_fn = title + '.html'
    out_path = os.path.join(os.path.dirname(in_path), out_fn)

    # settings
    geo_bounds = get_geo_bounds(root)
    pixel_bounds = (800, 600)

    # build node mapping (from id -> node)
    node_map = {int(child.attrib['id']): child for child in root if child.tag == 'node'}
    ways = [child for child in root if child.tag == 'way']
    print('INFO: Found {} ways'.format(len(ways)))

    # extract stuff
    # TODO: keep going


def render(
        in_path: str, node_map: Dict[int, ET.Element], ways: List[ET.Element],
        geo_bounds: Tuple[float,float,float,float]):
    """Just renders OSM tree below root to SVG"""
    # could pass most of the immediate below in if desired

    # file crap
    title = '.'.join(os.path.basename(in_path).split('.')[:-1])
    out_fn = title + '.html'
    out_path = os.path.join(os.path.dirname(in_path), out_fn)

    # settings
    pixel_bounds = (800, 600)

    # reporting to have some idea of scale
    print('Lat range: {:.5f} -- {:.5f} (delta: {:.5f})'.format(
        geo_bounds[0], geo_bounds[2], abs(geo_bounds[2] - geo_bounds[0])
    ))
    print('Lon range: {:.5f} -- {:.5f} (delta: {:.5f})'.format(
        geo_bounds[1], geo_bounds[3], abs(geo_bounds[3] - geo_bounds[1])
    ))

    # build node mapping (from id -> node)
    print('INFO: Found {} ways'.format(len(ways)))

    # extract polys
    geo_meta_polys = []
    geo_meta_roads = []
    geo_road_points = []
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

        meta_poly['features'] = get_way_features(way)

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
            for point in meta_poly['points']:
                geo_road_points.append(point)

    # collapse geo road points (test before trying to turn into a graph)
    thresh = 1e-4
    toremove = set()
    for i in range(len(geo_road_points)):
        for j in range(i+1, len(geo_road_points)):
            p1 = geo_road_points[i]
            p2 = geo_road_points[j]
            l2_diff = sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
            # could end up with some really bad chaining of small distances and
            # deleting all intermediate points but probably fine
            if l2_diff < thresh:
                toremove.add(j)
    filtered_geo_road_points = [pt for i, pt in enumerate(geo_road_points) if i not in toremove]

    # get just geo ones for now
    geo_polys = [geo_meta_poly['points'] for geo_meta_poly in geo_meta_polys]
    geo_roads = [geo_meta_road['points'] for geo_meta_road in geo_meta_roads]

    # convert
    pixel_polys = geo.convert_polys(geo_bounds, pixel_bounds, geo_polys)
    pixel_roads = geo.convert_polys(geo_bounds, pixel_bounds, geo_roads)
    pixel_road_points = geo.convert_points(geo_bounds, pixel_bounds, filtered_geo_road_points)

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
    for x, y in pixel_road_points:
        inner_els.append(
            '<circle cx="{}" cy="{}" r="{}" fill="orange" stroke="black" />'.format(
                x, y, 3)#random.randint(1, 5))
        )
    footer = '\n</svg>\n\n</body>\n</html>'

    # write out
    with open(out_path, 'w') as f:
        f.write('\n'.join([header] + inner_els + [footer]))


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


def preproc(fn: str) -> Tuple[Dict[int, ET.Element], List[ET.Element], Tuple[float,float,float,float]]:
    tree = ET.parse(fn)
    root = tree.getroot()
    node_map = {int(child.attrib['id']): child for child in root if child.tag == 'node'}
    ways = [child for child in root if child.tag == 'way']
    geo_bounds = get_geo_bounds(root)

    return node_map, ways, geo_bounds


def main():
    # parse XML tree and get root
    fn = 'data/north-winds.osm'
    node_map, ways, geo_bounds = preproc(fn)

    # try to figure out the format
    # detective(root)

    # do some basic renderering
    render(fn, node_map, ways, geo_bounds)


if __name__ == '__main__':
    main()
