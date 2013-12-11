import zlib
from xml.etree import ElementTree

def get_xml(filename):
    contents = open(filename, "rb").read()
    xml = zlib.decompress(contents[4:])
    return xml

def get_element_tree(filename):
    return ElementTree.fromstring(get_xml(filename))
