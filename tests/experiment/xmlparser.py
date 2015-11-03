from uiautomator import device as d
import xml.etree.ElementTree as ET

output = d.dump()
root = ET.fromstring(output)

#print root.attrib


for child in root.iter('node'):
    print "1"
    print child.tag, child.attrib
