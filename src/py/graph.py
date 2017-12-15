# imports
# ---

# builtins
import code
from math import sqrt
import os
from collections import deque
import math
import pickle
from typing import Dict, Set, Tuple, List, FrozenSet
import xml.etree.ElementTree as ET

# 3rd party
from tqdm import tqdm

# local
import osm
import geo
from geo import Point, Line, Polygon
import polygon
from polygon import DiscretePoly
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


def find_blocks_dummy(graph: Dict[int, Set[int]]) -> List[List[int]]:
    """
    Dummy "block finder" just to test visualizing blocks.
    """
    # return dummy poly
    poly = []
    for i, key in enumerate(graph.keys()):
        if i > 7:
            break
        poly.append(key)
    poly.append(key)
    return [poly]


def strpath(path: List[int]) -> str:
    return '[{}]'.format(','.join(str(n) for n in path))


def can_add_to_shortest(cur: int, curpath: List[int], shortest: Dict[int, List[List[int]]]) -> bool:
    # if shortest hasn't found cur yet, then yes (because BFS finds shortest
    # path lens)
    if cur not in shortest:
        return True

    assert len(curpath) >= 2, 'algorithm expects paths to be >= 2 in len'

    # if the path is just 2 (i.e., directly from start to this node), but a
    # different path has already been added, then our graph construction is
    # weird; that means we have multiple paths from the start to cur. let's not
    # add it for now.
    if len(curpath) == 2:
        return False

    # now, for the interesting case. We want to add only if we've found a new
    # path to this node that is unique; i.e., the middle nodes (excluding start
    # and cur) have nothing in common with any other paths.
    curpath_middle_nodes = set(curpath[1:-1])
    for existing_path in shortest[cur]:
        existing_path_middle_nodes = set(existing_path[1:-1])
        if len(existing_path_middle_nodes.intersection(curpath_middle_nodes)) > 0:
            return False
    return True


def find_rings_at(graph: Dict[int, Set[int]], start: int, maxdist = 7) -> List[List[int]]:
    # print('Starting at node: {}'.format(start))
    start_path = [start]  # type: List[int]
    shortest = {}  # type: Dict[int, List[List[int]]]
    q = deque([(start, start_path)])

    # first, find sets of unique paths to surrounding nodes
    while len(q) > 0:
        cur, curpath = q.popleft()
        # print()
        # print('Considering {} {}'.format(cur, strpath(curpath)))
        # print('Shortest: {}'.format(str(shortest)))
        if can_add_to_shortest(cur, curpath, shortest):
            if cur not in shortest:
                shortest[cur] = []
            shortest[cur].append(curpath)

        # TODO: we should also stop here depending on shortest, right? either
        # make sure cur wasn't in shortest, or use the can_add_to_shortest()
        # test?
        if len(curpath) < maxdist:
            for neighbor in graph[cur]:
                # no backtracking
                if neighbor not in curpath:
                    q.append((neighbor, curpath + [neighbor]))

    # now, extract rings as immediate neighbors with > 1 path to them
    # print()
    # print('Final shortest: {}'.format(str(shortest)))
    rings = []
    for candidate in shortest.keys():
        paths = shortest[candidate]
        # print('Paths found for {}: {}'.format(candidate, len(paths)))
        if len(paths) > 1:
            # just use first two found
            p1 = paths[0]
            p2 = paths[1]
            rings.append(p1 + list(reversed(p2[1:-1])))

    return rings


def polygon_contains(bigger: DiscretePoly, smaller: DiscretePoly) -> bool:
    """Tests whether bigger contains smaller.

    NOTE: doing an approximate check here. Checking whether `smaller` is inside
    `bigger` by checking whether each point of `smaller` is inside `bigger`.
    This is not exact because spiky polygons could have empty regions that
    would confuse things. (For those regions, depending on the application,
    it's actually not clear what the desired result should be.)
    """
    for point in smaller:
        # if point not in bigger and not polygon.point_in_polygon(bigger, point):
        if not polygon.point_in_polygon(bigger, point):
            # print('{}  not in bigger'.format(str(point)))
            return False
    return True


def filter_encompassing_blocks(
        blocks: List[List[int]],
        pixel_blocks: List[DiscretePoly]) -> Set[int]:

    # check each pair and remove as needed
    toremove = set()
    for i in tqdm(range(len(blocks))):
        bi = pixel_blocks[i]
        for j in range(i+1, len(blocks)):
            bj = pixel_blocks[j]
            if polygon_contains(bi, bj):
                toremove.add(i)
            if polygon_contains(bj, bi):
                toremove.add(j)

    return toremove


def find_blocks(
        graph: Dict[int, Set[int]], node_map: Dict[int, ET.Element],
        geo_bounds: Tuple[float,float,float,float],
        pixel_bounds: Tuple[int, int]) -> Tuple[List[Polygon], List[List[int]], List[DiscretePoly]]:
    """
    Returns 2-tuple of:
        - list of blocks in ID format: each block is list of node IDs
        - list of blocks in polygon format in pixel_bounds space
    """
    # find unique rings
    blocks_map = {}  # type: Dict[FrozenSet[int], List[int]]
    for n in tqdm(graph.keys()):
        for ring in find_rings_at(graph, n):
            if frozenset(ring) not in blocks_map:
                blocks_map[frozenset(ring)] = ring

    # rasterize blocks
    blocks = list(blocks_map.values())
    geo_blocks, pixel_blocks = ways_to_pixel_coords(blocks, node_map, geo_bounds, pixel_bounds)

    # find encompassing blocks to remove
    toremove = filter_encompassing_blocks(blocks, pixel_blocks)

    # print('Encompass filtering: before {}, after {} (removed {})'.format(
    #     len(blocks),
    #     len(block_res),
    #     len(toremove),
    # ))

    # return blocks that aren't on the to-remove list in all three formats (ref
    # list, geo poly, pixel poly)
    geo_res = []
    block_res = []
    pixel_res = []
    for idx in range(len(blocks)):
        if idx not in toremove:
            geo_res.append(geo_blocks[idx])
            block_res.append(blocks[idx])
            pixel_res.append(pixel_blocks[idx])

    return geo_res, block_res, pixel_res


def geo_ways_to_pixel_coords(
        geo_ways: List[Polygon],
        geo_bounds: Tuple[float,float,float,float],
        pixel_bounds: Tuple[int, int]) -> List[DiscretePoly]:

    # convert to pixels
    pixel_ways_float = geo.convert_polys(geo_bounds, pixel_bounds, geo_ways)

    # floor everything to hopefully help out with float rounding errors
    pixel_ways_int = []
    for float_polygon in pixel_ways_float:
        int_polygon = []
        for point in float_polygon:
            int_polygon.append((int(math.floor(point[0])), int(math.floor(point[1]))))
        pixel_ways_int.append(int_polygon)

    return pixel_ways_int


def ways_to_pixel_coords(
        ways: List[List[int]],
        node_map: Dict[int, ET.Element],
        geo_bounds: Tuple[float,float,float,float],
        pixel_bounds: Tuple[int, int]) -> Tuple[List[Polygon], List[DiscretePoly]]:
    # turn each way (node list) into geo poly
    geo_ways = []
    for way in ways:
        geo_way = []
        for node_id in way:
            node = node_map[node_id]
            geo_way.append((float(node.attrib['lat']), float(node.attrib['lon'])))
        geo_ways.append(geo_way)

    return geo_ways, geo_ways_to_pixel_coords(geo_ways, geo_bounds, pixel_bounds)


def display(
        in_path: str, node_map: Dict[int, ET.Element],
        geo_bounds: Tuple[float,float,float,float],
        pixel_bounds: Tuple[int, int],
        graph: Dict[int, Set[int]],
        blocks: List[List[int]],
        pixel_blocks: List[List[int]],
        special_node_ref: int):
    # file crap
    title = '.'.join(os.path.basename(in_path).split('.')[:-1])
    out_fn = title + '-graph.html'
    out_path = os.path.join(os.path.dirname(in_path), out_fn)

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

    # turn each block (node list) into geo poly
    # geo_blocks = []
    # for block in blocks:
    #     geo_block = []
    #     for node_id in block:
    #         node = node_map[node_id]
    #         geo_block.append((float(node.attrib['lat']), float(node.attrib['lon'])))
    #     geo_blocks.append(geo_block)

    # extract special point coords
    special_node = node_map[special_node_ref]
    geo_special_point = (float(special_node.attrib['lat']), float(special_node.attrib['lon']))

    # convert
    # pixel_blocks = geo.convert_polys(geo_bounds, pixel_bounds, geo_blocks)
    pixel_lines = geo.convert_polys(geo_bounds, pixel_bounds, geo_lines)
    pixel_points = geo.convert_points(geo_bounds, pixel_bounds, geo_points)
    pixel_special_point = geo.convert_points(geo_bounds, pixel_bounds, [geo_special_point])[0]

    # render
    contents = '\n'.join([
        svg.header(pixel_bounds),
        svg.lines(pixel_lines),
        svg.circles(pixel_points),
        svg.polygons(pixel_blocks),
        # svg.circles([pixel_special_point], '#feb24c', 5),
        svg.footer(),

    ])
    print('Saving to "{}"'.format(out_path))
    with open(out_path, 'w') as f:
        f.write(contents)


def legit():
    intermediate_res_w = 800
    intermediate_res_h = 600
    fn = 'data/business-time.osm'
    graph_cache_fn = 'data/business-time-graph.pkl'

    node_map, ways, geo_bounds = osm.preproc(fn)

    # build and save graph
    # graph = build(node_map, ways)
    # with open(graph_cache_fn, 'wb') as f:
    #     print('Writing graph to "{}"'.format(graph_cache_fn))
    #     pickle.dump(graph, f)

    # ... or load it
    with open(graph_cache_fn, 'rb') as f:
        print('Reading graph from "{}"'.format(graph_cache_fn))
        graph = pickle.load(f)

    special_node = list(graph.keys())[300]
    pixel_bounds = (intermediate_res_w, intermediate_res_h)
    geo_blocks, blocks, pixel_blocks = find_blocks(graph, node_map, geo_bounds, pixel_bounds)

    # debug what was found
    # print('Blocks found: {}'.format(len(blocks)))

    # map buildings to blocks

    display(
        fn, node_map, geo_bounds, pixel_bounds, graph, blocks, pixel_blocks,
        special_node)


def toy():
    # 4 ------- 3
    # |         |
    # |         |
    # 2 ------- 1
    toygraph = {
        1: set([2, 3]),
        2: set([1, 4]),
        3: set([1, 4]),
        4: set([2, 3]),
    }
    print('Rings found: {}'.format(str(find_rings_at(toygraph, 1))))


def test_encompass_check():
    bigger = [
        (187,27),
        (183,27),
        (175,27),
        (159,27),
        (153,27),
        (148,27),
        (149,108),
        (183,108),
        (217,108),
        (217,27),
    ]
    smaller = [
        (148,27),
        (153,27),
        (159,27),
        (175,27),
        (183,27),
        (183,108),
        (149,108),
    ]

    print('Bigger contains smaller:', polygon_contains(bigger, smaller))

def main():
    # test graph construction and block extraction on actual data
    legit()

    # toy test for block detection
    # toy()

    # test encompassing logic
    # test_encompass_check()


if __name__ == '__main__':
    main()
