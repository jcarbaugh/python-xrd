from xrd import XRD, Link, Property, Title, _get_text
import unittest

class TestProperty(unittest.TestCase):
    
    def testequals(self):
        
        # same type and value
        p1 = Property('http://example.com/p1', '1234')
        p2 = Property('http://example.com/p1', '1234')
        self.assertTrue(p1 == p2)

        # same type, no value
        p1 = Property('http://example.com/p1')
        p2 = Property('http://example.com/p1')
        self.assertTrue(p1 == p2)
        
    def testnotequals(self):
        
        # same value, different type
        p1 = Property('http://example.com/p1', '1234')
        p2 = Property('http://example.com/p2', '1234')
        self.assertTrue(p1 != p2)
        
        # same type, different value
        p1 = Property('http://example.com/p1', '1234')
        p2 = Property('http://example.com/p1', '9876')
        self.assertTrue(p1 != p2)
        
        # same type, one value missing
        p1 = Property('http://example.com/p1')
        p2 = Property('http://example.com/p1', '12345')
        self.assertTrue(p1 != p2)
        
        # different type, no value
        p1 = Property('http://example.com/p1')
        p2 = Property('http://example.com/p2')
        self.assertTrue(p1 != p2)


class TestTitle(unittest.TestCase):
    
    def testequals(self):
        
        # same title and xmllang
        t1 = Title('myfeed', xml_lang='en-US')
        t2 = Title('myfeed', xml_lang='en-US')
        self.assertTrue(t1 == t2)

        # same title, no xmllang
        t1 = Title('myfeed')
        t2 = Title('myfeed')
        self.assertTrue(t1 == t2)
        
    def testnotequals(self):

        # same title, different xmllang
        t1 = Property('myfeed', 'en-US')
        t2 = Property('myfeed', 'en-GB')
        self.assertTrue(t1 != t2)
        
        # same xmllang, different title
        t1 = Property('myfeed', 'en-US')
        t2 = Property('yourfeed', 'en-US')
        self.assertTrue(t1 != t2)
        
        # same title, one missing xmllang
        t1 = Property('myfeed')
        t2 = Property('myfeed', 'en-GB')
        self.assertTrue(t1 != t2)
        
        # different title, no xml lang
        t1 = Property('myfeed')
        t2 = Property('yourfeed')
        self.assertTrue(t1 != t2)


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