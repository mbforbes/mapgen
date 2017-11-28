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

    # Hmmm... OK, weird. What are nd? Nodes? How many tags do ways have? Let's
    # investigate...
    children = root.getchildren()
    ways = [child for child in children if child.tag == 'way']

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

    # Now, let's check out nodes.
    way_nd_children = Counter()
    for way in ways:
        nds = [child for child in way.getchildren() if child.tag == 'nd']
        for nd in nds:
            way_nd_children[len(nd.getchildren())] += 1
    print('children/nd of waypoint:', way_nd_children)
    # => children/nd of waypoint: Counter({0: 39546})
    # phew! also as expected. `nd`s are leaves. Why not call them `node`s...

    # (top-level) node investigation
    # ---

    # just to confirm that tags of top-level nodes are all leaves
    node_tag_children = Counter()
    nodes = [child for child in children if child.tag == 'node']
    for node in nodes:
        # already verified above that tags are the only children of nodes
        tags = node.getchildren()
        for tag in tags:
            node_tag_children[len(tag.getchildren())] += 1
    print('children/tag of node:', node_tag_children)
    # => children/tag of node: Counter({0: 5380})
    # phew! As expected. `tag`s of `node`s are leaves.

    # I don't think I'm going to investigate relations just yet, as I don't
    # think I'll be dealing with that level of semantics for a while (if ever).

    # play around
    code.interact(local=dict(globals(), **locals()))


if __name__ == '__main__':
    main()
