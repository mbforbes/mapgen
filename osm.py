"""
Working with OpenStreetMap XML files.
"""

# imports
import code
import xml.etree.ElementTree as ET


# playing

def main():
    fn = 'data/facing-east.osm'
    tree = ET.parse(fn)
    code.interact(local=dict(globals(), **locals()))


if __name__ == '__main__':
    main()
