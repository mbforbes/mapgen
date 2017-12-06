# imports
# ---

# builtins
import code
from math import sqrt
import os
from typing import Dict, Set, Tuple, List
import xml.etree.ElementTree as ET

# local
import osm
import geo
from geo import Point, Line
import svg


# code
# ---

def backtrack_ref(node_combine: Dict[int, int], query: int) -> int:
    """Traverses a mapping an arbitrary number of steps to lookup the base
    ref.

    Example. Say node_combine maps:
        x -> y
        y -> z
        z -> w

    Then the following should happen:
        w == backtrack_ref(x)
        w == backtrack_ref(y)
        w == backtrack_ref(z)
        w == backtrack_ref(w)
    """
    while query in node_combine:
        query = node_combine[query]
    return query


def geo_dist(nodeA: ET.Element, nodeB: ET.Element):
    """Computes a geo distance function.

    Currently, does l2 in lat, lon space.
    """
    latA, lonA = float(nodeA.attrib['lat']), float(nodeA.attrib['lon'])
    latB, lonB = float(nodeB.attrib['lat']), float(nodeB.attrib['lon'])
    l2_dist = sqrt((latA - latB)**2 + (lonA - lonB)**2)
    return l2_dist


def build(
        node_map: Dict[int, ET.Element], ways: List[ET.Element],
        thresh: float = 1e-4) -> Dict[int, Set[int]]:
    """Builds a road network graph by combinging nodes at intersections and
    then using road paths as edges.

    TODO: eventually much of this belongs in OSM

    Args:
        thresh: l2 distance in lat, lon space under which nodes will be merged.
    """
    # combine nodes in ways only (not in other polys as we might collapse fine
    # grained building features)

    # first find all nodes that are part of road ways (also build road way list
    # now because why not)
    road_nds = set()  # type: Set[int]
    road_ways = []
    for way in ways:
        # only consider roads
        features = osm.get_way_features(way)
        if 'highway' not in features:
            continue

        road_ways.append(way)
        nds = [child for child in way if child.tag == 'nd']
        road_nds.update([int(nd.attrib['ref']) for nd in nds])

    print('Original: {} road nds'.format(len(road_nds)))

    # then, make a mapping to combine refs when they're within thresh (O(n^2))
    node_combine = {}  # type: Dict[int, int]
    road_nd_lst = list(road_nds)
    for i in range(len(road_nd_lst)):
        for j in range(i+1, len(road_nd_lst)):
            raw_id_i = road_nd_lst[i]
            raw_id_j = road_nd_lst[j]

            # backtrack refs to get "true" nodes.
            id_i = backtrack_ref(node_combine, raw_id_i)
            id_j = backtrack_ref(node_combine, raw_id_j)

            # if they've already been merged, do nothing
            if id_i == id_j:
                continue

            # compute dist
            node_i = node_map[id_i]
            node_j = node_map[id_j]
            dist = geo_dist(node_i, node_j)

            # code.interact(local=dict(globals(), **locals()))

            # how we update ids here determines whether we're following
            # transitive chains of distances below thresh. we do right now. if
            # not, would we need to do multiple passes?
            if dist < thresh:
                node_combine[id_j] = id_i

    combined_nd_lst = set([backtrack_ref(node_combine, ref) for ref in road_nd_lst])
    print('After merging: {} road nds'.format(len(combined_nd_lst)))

    # construct graph
    graph = {}  # type: Dict[int, Set[int]]
    for way in road_ways:
        nds = [child for child in way if child.tag == 'nd']
        for i in range(len(nds) - 1):
            id_i = backtrack_ref(node_combine, int(nds[i].attrib['ref']))
            id_j = backtrack_ref(node_combine, int(nds[i+1].attrib['ref']))

            if id_i not in graph:
                graph[id_i] = set()
            if id_j not in graph:
                graph[id_j] = set()
            graph[id_i].add(id_j)
            graph[id_j].add(id_i)

    return graph


def display(
        in_path: str, node_map: Dict[int, ET.Element],
        geo_bounds: Tuple[float,float,float,float],
        graph: Dict[int, Set[int]]):
    # file crap
    title = '.'.join(os.path.basename(in_path).split('.')[:-1])
    out_fn = title + '-graph.html'
    out_path = os.path.join(os.path.dirname(in_path), out_fn)

    # settings
    pixel_bounds = (800, 600)

    # extract points and lines
    geo_lines = []  # type: List[Line]
    geo_points = []  # type: List[Point]
    for node_id, neighbor_ids in graph.items():
        node = node_map[node_id]
        geo_points.append((float(node.attrib['lat']), float(node.attrib['lon'])))
        for neighbor_id in neighbor_ids:
            neighbor = node_map[neighbor_id]
            geo_lines.append([
                (float(node.attrib['lat']), float(node.attrib['lon'])),
                (float(neighbor.attrib['lat']), float(neighbor.attrib['lon'])),
            ])

    # convert
    pixel_lines = geo.convert_polys(geo_bounds, pixel_bounds, geo_lines)
    pixel_points = geo.convert_points(geo_bounds, pixel_bounds, geo_points)

    # render
    contents = '\n'.join([
        svg.header(pixel_bounds), svg.lines(pixel_lines),
        svg.circles(pixel_points), svg.footer(),
    ])
    print('Saving to "{}"'.format(out_path))
    with open(out_path, 'w') as f:
        f.write(contents)


def main():
    fn = 'data/north-winds.osm'
    node_map, ways, geo_bounds = osm.preproc(fn)

    graph = build(node_map, ways)
    display(fn, node_map, geo_bounds, graph)


if __name__ == '__main__':
    main()
