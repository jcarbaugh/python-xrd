from xrd import XRD, Link, Property, _get_text
import unittest

class TestDeserialization(unittest.TestCase):

    def setUp(self):
        self.xrd = XRD.parse("""<?xml version="1.0" ?>
            <XRD xml:id="1234" xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
            	<Property type="mimetype">text/plain</Property>
            	<Property type="none"></Property>
            	<Link template="http://google.com/{uri}">
            		<Title xml:lang="en_us">this is my rel</Title>
            	</Link>
            </XRD>
            """)
    
    def testxmlid(self):
        self.assertEqual(self.xrd.xml_id, "1234")
    
    def testproperty(self):
        prop = self.xrd.properties[0]
        self.assertEqual(prop.type, "mimetype")
        self.assertEqual(prop.value, "text/plain")
    
    def testnilproperty(self):
        prop = self.xrd.properties[1]
        self.assertEqual(prop.type, "none")
        self.assertTrue(prop.value is None)
    
    def testlink(self):
        link = self.xrd.links[0]
        self.assertEqual(link.template, "http://google.com/{uri}")


class TestSerialization(unittest.TestCase):
    
    def setUp(self):
        self.xrd = XRD('9876')
        self.xrd.properties.append(Property('mimetype', 'text/plain'))
        self.xrd.properties.append(Property('none'))
        self.xrd.links.append(Link(template="http://google.com/{uri}"))
        self.doc = self.xrd.to_xml().documentElement
    
    def testxmlid(self):
        self.assertEqual(self.doc.getAttribute('xml:id'), '9876')
    
    def testproperty(self):
        prop = self.doc.getElementsByTagName('Property')[0]
        self.assertEqual(prop.getAttribute('type'), 'mimetype')
        self.assertEqual(_get_text(prop), 'text/plain')
    
    def testnilproperty(self):
        prop = self.doc.getElementsByTagName('Property')[1]
        self.assertEqual(prop.getAttribute('type'), 'none')
        self.assertEqual(prop.getAttribute('xsi:nil'), 'true')
        self.assertTrue(_get_text(prop) is None)
    
    def testlink(self):
        link = self.doc.getElementsByTagName('Link')[0]
        self.assertEqual(link.getAttribute('template'), "http://google.com/{uri}")


if __name__ == '__main__':
    unittest.main()