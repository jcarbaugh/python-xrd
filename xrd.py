import logging
import json
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Iterable, List, Mapping, Optional, Union, cast
from xml.dom.minidom import (
    getDOMImplementation,
    parseString,
    Document,
    DOMImplementation,
    Node,
)

import isodate  # type: ignore

__version__ = "1.0.0"

XRD_NAMESPACE = "http://docs.oasis-open.org/ns/xri/xrd-1.0"

"""
XRD: http://docs.oasis-open.org/xri/xrd/v1.0/xrd-1.0.html
JRD: https://datatracker.ietf.org/doc/rfc6415/
"""

logger = logging.getLogger(__name__)


def ensure_iterable(v: Any) -> Iterable:
    if not isinstance(v, (list, tuple)):
        return (v,)
    return v


@dataclass
class Title:
    value: str
    lang: str = ""


@dataclass
class Link:
    rel: str = ""
    type: str = ""
    href: str = ""
    template: str = ""
    titles: List[Title] = field(default_factory=list)
    properties: dict[str, Optional[Union[str, List[str]]]] = field(default_factory=dict)


@dataclass
class XRD:
    xml_id: str = ""
    expires: Optional[datetime] = None
    subject: str = ""
    aliases: List[str] = field(default_factory=list)
    properties: dict[str, Optional[Union[str, Iterable[str]]]] = field(
        default_factory=dict
    )
    links: List[Link] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)

    def find_link(
        self, rels: Union[str, Iterable[str]], attr: Optional[str] = None
    ) -> Optional[Union[Link, str, Iterable, Mapping]]:
        """Find a link by relation.
        If a single relation is given, returns the first item that matches the relation.
        If multiple relations are given, returns the first item that matches any of the relations.
        """
        rels = ensure_iterable(rels)
        for link in self.links:
            if link.rel in rels:
                if attr:
                    return getattr(link, attr, None)
                return link
        return None

    def as_json(self) -> str:
        return render_json(self)

    def as_xml(self) -> Document:
        return render_xml(self)

    def validate(self):
        for link in self.links:
            if link.href and link.template:
                raise ValueError(
                    f"only one of href or template attributes may be specified on a link: {link}"
                )


def _get_text(root: Node) -> Optional[str]:
    text = ""
    for node in root.childNodes:
        if node.nodeType == Node.TEXT_NODE and node.nodeValue:
            text += node.nodeValue
        else:
            node_text = _get_text(node)
            if node_text:
                text += node_text
    return text.strip() or None


def _clean_dict(d: Mapping) -> dict:
    """Remove empty values from a dict."""
    return {key: value for key, value in d.items() if value}


# json parser/renderer


def parse_json(content: str) -> XRD:
    def expires_handler(key, val, obj):
        obj.expires = isodate.parse_datetime(val)

    def subject_handler(key, val, obj):
        obj.subject = val

    def alias_handler(key, val, obj):
        for alias in val:
            obj.aliases.append(alias)

    def property_handler(key, val, obj):
        for type_, value in val.items():
            if isinstance(value, (list, tuple)):
                value = value[-1]
            obj.properties[type_] = value

    def title_handler(key, val, obj):
        for lang, title in val.items():
            obj.titles.append(Title(title, lang=lang))

    def link_handler(key, val, obj):
        for link in val:
            l = Link()
            l.rel = link.get("rel", "")
            l.type = link.get("type", "")
            l.href = link.get("href", "")
            l.template = link.get("template", "")
            if "titles" in link:
                title_handler("titles", link["titles"], l)
            if "properties" in link:
                property_handler("properties", link["properties"], l)
            obj.links.append(l)

    handlers = {
        "expires": expires_handler,
        "subject": subject_handler,
        "aliases": alias_handler,
        "properties": property_handler,
        "links": link_handler,
        "title": title_handler,
    }

    def unknown_handler(key, val, obj):
        logger.info(f"Unknown property: {key} = {val}")

    doc = json.loads(content)

    xrd = XRD()
    xrd.attributes["xmlns"] = XRD_NAMESPACE

    for key, value in doc.items():
        handler = handlers.get(key, unknown_handler)
        handler(key, value, xrd)

    xrd.validate()

    return xrd


def render_json(xrd: XRD) -> str:

    xrd.validate()

    doc: dict = {
        "aliases": [],
        "links": [],
        "namespace": [],
        "properties": {},
        "title": [],
    }

    if xrd.expires:
        doc["expires"] = isodate.datetime_isoformat(xrd.expires)

    if xrd.subject:
        doc["subject"] = xrd.subject

    for alias in xrd.aliases:
        doc["aliases"].append(alias)

    for type_, val in xrd.properties.items():
        if isinstance(val, (list, tuple)):
            val = val[-1]
        doc["properties"][type_] = val

    for link in xrd.links:

        link_doc: dict = {
            "titles": {},
            "properties": {},
        }

        if link.rel:
            link_doc["rel"] = link.rel

        if link.type:
            link_doc["type"] = link.type

        if link.href:
            link_doc["href"] = link.href

        if link.template:
            link_doc["template"] = link.template

        for type_, val in link.properties.items():
            if isinstance(val, (list, tuple)):
                val = val[-1]
            link_doc["properties"][type_] = val

        for title in link.titles:
            lang = title.lang or "default"
            link_doc["titles"][lang] = title.value

        doc["links"].append(_clean_dict(link_doc))

    return json.dumps(_clean_dict(doc))


# xml parser/renderer


def parse_xml(content: str) -> XRD:

    import isodate

    def expires_handler(node, obj):
        obj.expires = isodate.parse_datetime(_get_text(node))

    def subject_handler(node, obj):
        obj.subject = _get_text(node)

    def alias_handler(node, obj):
        obj.aliases.append(_get_text(node))

    def property_handler(node, obj):
        key = node.getAttribute("type")
        if key in obj.properties:
            if not isinstance(obj.properties[key], list):
                obj.properties[key] = [obj.properties[key]]
            obj.properties[key].append(_get_text(node))
        else:
            obj.properties[key] = _get_text(node)

    def title_handler(node, obj):
        obj.titles.append(Title(_get_text(node), node.getAttribute("xml:lang")))

    def link_handler(node, obj):
        l = Link()
        l.rel = node.getAttribute("rel")
        l.type = node.getAttribute("type")
        l.href = node.getAttribute("href")
        l.template = node.getAttribute("template")
        obj.links.append(l)

    handlers = {
        "Expires": expires_handler,
        "Subject": subject_handler,
        "Alias": alias_handler,
        "Property": property_handler,
        "Link": link_handler,
        "Title": title_handler,
    }

    def unknown_handler(node, obj):
        logger.info(f"Unknown node: {node.tagName}")

    def handle_node(node, obj):
        handler = handlers.get(node.nodeName, unknown_handler)
        if handler and node.nodeType == node.ELEMENT_NODE:
            handler(node, obj)

    doc = parseString(content)
    root = doc.documentElement

    xrd = XRD(root.getAttribute("xml:id"))

    for name, value in root.attributes.items():
        if name != "xml:id":
            xrd.attributes[name] = value

    for node in root.childNodes:
        handle_node(node, xrd)
        if node.nodeName == "Link":
            link = xrd.links[-1]
            for child in node.childNodes:
                handle_node(child, link)

    xrd.validate()

    return xrd


def render_xml(xrd: XRD) -> Document:

    xrd.validate()

    dom = cast(DOMImplementation, getDOMImplementation())
    doc = dom.createDocument(XRD_NAMESPACE, "XRD", None)
    root = doc.documentElement
    root.setAttribute("xmlns", XRD_NAMESPACE)

    if xrd.xml_id:
        root.setAttribute("xml:id", xrd.xml_id)

    for name, value in xrd.attributes.items():
        root.setAttribute(name, value)

    if xrd.expires:
        node = doc.createElement("Expires")
        node.appendChild(doc.createTextNode(isodate.datetime_isoformat(xrd.expires)))
        root.appendChild(node)

    if xrd.subject:
        node = doc.createElement("Subject")
        node.appendChild(doc.createTextNode(xrd.subject))
        root.appendChild(node)

    for alias in xrd.aliases:
        node = doc.createElement("Alias")
        node.appendChild(doc.createTextNode(alias))
        root.appendChild(node)

    uses_nil = False
    for type_, vals in xrd.properties.items():
        vals = ensure_iterable(vals)
        for val in vals:
            node = doc.createElement("Property")
            node.setAttribute("type", type_)
            if val is None:
                node.setAttribute("xsi:nil", "true")
                uses_nil = True
            else:
                node.appendChild(doc.createTextNode(str(val)))
            root.appendChild(node)

    if uses_nil:
        root.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")

    for link in xrd.links:

        link_node = doc.createElement("Link")

        if link.rel:
            link_node.setAttribute("rel", link.rel)

        if link.type:
            link_node.setAttribute("type", link.type)

        if link.href:
            link_node.setAttribute("href", link.href)

        if link.template:
            link_node.setAttribute("template", link.template)

        for title in link.titles:
            node = doc.createElement("Title")
            node.appendChild(doc.createTextNode(title.value))
            if title.lang:
                node.setAttribute("xml:lang", title.lang)
            link_node.appendChild(node)

        for type_, vals in link.properties.items():
            vals = ensure_iterable(vals)
            for val in vals:
                node = doc.createElement("Property")
                node.setAttribute("type", type_)
                if val is None:
                    node.setAttribute("xsi:nil", "true")
                else:
                    node.appendChild(doc.createTextNode(str(val)))
                link_node.appendChild(node)

        root.appendChild(link_node)

    return doc
