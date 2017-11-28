"""
Working with OpenStreetMap XML files.
"""

# imports
import code
from collections import Counter
import xml.etree.ElementTree as ET


# playing

def main():
    # parse XML tree and get root
    fn = 'data/facing-east.osm'
    tree = ET.parse(fn)
    root = tree.getroot()

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

    # way(point) investigation
    # ---
    print('\nWaypoints\n{}\n'.format('-'*80))

    # Hmmm... OK, weird. What are nd? Nodes? How many tags do ways have? Let's
    # investigate...
    children = root.getchildren()
    ways = [child for child in children if child.tag == 'way']

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


if __name__ == '__main__':
    main()
