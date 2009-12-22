from xml.dom.minidom import getDOMImplementation, parseString, Node
import datetime

__author__ = "Jeremy Carbaugh (jcarbaugh@gmail.com)"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2009 Jeremy Carbaugh"
__license__ = "BSD"

XRD_NAMESPACE = "http://docs.oasis-open.org/ns/xri/xrd-1.0"

def _get_text(root):
    text = ''
    for node in root.childNodes:
        if node.nodeType == Node.TEXT_NODE and node.nodeValue:
            text += node.nodeValue
        else:
            text += _get_text(node)
    return text.strip() or None

def _parse_xml(content):
    
    def expires_handler(node, obj):
        #obj.expires = _get_text(node)
        pass
    
    def subject_handler(node, obj):
        obj.subject = _get_text(node)
    
    def alias_handler(node, obj):
        obj.aliases.append(_get_text(node))
    
    def property_handler(node, obj):
        obj.properties.append(Property(node.getAttribute('type'), _get_text(node)))

    def title_handler(node, obj):
        obj.titles.append(Title(_get_text(node), node.getAttribute('xml:lang')))
    
    def link_handler(node, obj):
        l = Link()
        l.rel = node.getAttribute('rel')
        l.type = node.getAttribute('type')
        l.href = node.getAttribute('href')
        l.template = node.getAttribute('template')
        obj.links.append(l)
    
    handlers = {
        'Expires': expires_handler,
        'Subject': subject_handler,
        'Alias': alias_handler,
        'Property': property_handler,
        'Link': link_handler,
        'Title': title_handler,
    }
    
    def handle_node(node, obj):
        handler = handlers.get(node.nodeName, None)
        if handler:
            handler(node, obj)
    
    doc = parseString(content)
    root = doc.documentElement
    
    xrd = XRD(root.getAttribute('xml:id'))
    
    for node in root.childNodes:
        handle_node(node, xrd)
        if node.nodeName == 'Link':
            link = xrd.links[-1]
            for child in node.childNodes:
                handle_node(child, link)
    
    return xrd
    

def _render_xml(xrd):
    
    doc = getDOMImplementation().createDocument(XRD_NAMESPACE, "XRD", None)
    root = doc.documentElement
    root.setAttribute('xmlns', XRD_NAMESPACE)
    
    if xrd.xml_id:
        root.setAttribute('xml:id', xrd.xml_id)
    
    if xrd.expires:
        node = doc.createElement('Expires')
        node.appendChild(doc.createTextNode(xrd.expires.isoformat()))
        root.appendChild(node)
    
    if xrd.subject:
        node = doc.createElement('Subject')
        node.appendChild(doc.createTextNode(xrd.subject))
        root.appendChild(node)
    
    for alias in xrd.aliases:
        node = doc.createElement('Alias')
        node.appendChild(doc.createTextNode(alias))
        root.appendChild(node)
    
    for prop in xrd.properties:
        node = doc.createElement('Property')
        node.setAttribute('type', prop.type)
        if prop.value:
            node.appendChild(doc.createTextNode(unicode(prop.value)))
        else:
            node.setAttribute('xsi:nil', 'true')
        root.appendChild(node)
    
    for link in xrd.links:
        
        if link.href and link.template:
            raise ValueError('only one of href or template attributes may be specified')
        
        link_node = doc.createElement('Link')
        
        if link.rel:
            link_node.setAttribute('rel', link.rel)
        
        if link.type:
            link_node.setAttribute('type', link.type)
        
        if link.href:
            link_node.setAttribute('href', link.href)
            
        if link.template:
            link_node.setAttribute('template', link.template)
        
        for title in link.titles:
            node = doc.createElement('Title')
            node.appendChild(doc.createTextNode(unicode(title)))
            if title.xml_lang:
                node.setAttribute('xml:lang', title.xml_lang)
            link_node.appendChild(node)
            
        root.appendChild(link_node)
    
    return doc

#
# special XRD types
#

class Title(object):
    def __init__(self, value, xml_lang=None):
        self.value = value
        self.xml_lang = xml_lang
    def __eq__(self, value):
        return str(self) == value
    def __str__(self):
        if self.xml_lang:
            return u"%s:%s" % (self.xml_lang, self.value)
        return self.value
        
class Property(object):
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value
    def __eq__(self, value):
        return str(self) == value
    def __str__(self):
        if self.value:
            return u"%s:%s" % (self.type, self.value)
        return self.type
        
#
# special list types
#

class ListLikeObject(list):
    def __setitem__(self, key, value):
        value = self.item(value)
        super(ListLikeObject, self).__setitem__(key, value)
    def append(self, value):
        value = self.item(value)
        super(ListLikeObject, self).append(value)
    def extend(self, values):
        values = (self.item(value) for value in values)
        super(ListLikeObject, self).extend(values)

class TypeList(ListLikeObject):
    def item(self, value):
        if isinstance(value, basestring):
            return Type(value)
        return value

class TitleList(ListLikeObject):
    def item(self, value):
        if isinstance(value, basestring):
            return Title(value)
        return value

class LinkList(ListLikeObject):
    def item(self, value):
        if not isinstance(value, Link):
            raise ValueError('value must be an instance of Link')
        return value

#
# Link object
#

class Link(object):
    
    def __init__(self, rel=None, type_=None, href=None, template=None):
        self.rel = rel
        self.type = type_
        self.href = href
        self.template = template
        self._titles = TitleList()
        self._properties = []
    
    def __str__(self):
        return ", ".join(self._rels)
    
    def get_titles(self):
        return self._titles
    titles = property(get_titles)
    
    def get_properties(self):
        return self._properties
    properties = property(get_properties)

#
# main XRD class
#
    
class XRD(object):
    
    def __init__(self, xml_id=None, subject=None):
        self.xml_id = xml_id
        self.subject = subject
        self._expires = None
        self._aliases = []
        self._properties = []
        self._links = LinkList()
        self._signatures = []
    
    @classmethod
    def parse(cls, xrd):
        return _parse_xml(xrd)
    
    def to_xml(self):
        return _render_xml(self)
    
    def get_expires(self):
        return self._expires
    def set_expires(self, expires):
        if not isinstance(expires, datetime.datetime):
            raise ValueError('expires must be a datetime object')
        self._expires = expires
    expires = property(get_expires, set_expires)
    
    def get_aliases(self):
        return self._aliases
    aliases = property(get_aliases)
    
    def get_properties(self):
        return self._properties
    properties = property(get_properties)
    
    def get_links(self):
        return self._links
    links = property(get_links)
    
    def get_signatures(self):
        return self._signatures
    signatures = property(get_links)
    