from xml.dom.minidom import parseString

from xrd import XRD, Link, is_empty, node_text, strip_dict


def test_xrd_find_link():

    link = Link("http://webfinger.net/rel/avatar", href="http://example.com/avatar.png")
    xrd = XRD(links=[link])

    assert xrd.find_link("http://webfinger.net/rel/profile-page") is None
    assert xrd.find_link("http://webfinger.net/rel/avatar") == link


def test_xrd_find_link_multiple_rels():

    rel_avatar = "http://webfinger.net/rel/avatar"
    rel_profile = "http://webfinger.net/rel/profile-page"

    link_avatar = Link(rel_avatar, href="http://example.com/avatar.png")
    link_profile = Link(rel_profile, href="http://example.com/me")

    xrd = XRD(links=[link_avatar, link_profile])

    assert xrd.find_link((rel_avatar, rel_profile)) == link_avatar


def test_xrd_find_attr():

    link = Link(
        "http://webfinger.net/rel/avatar",
        href="http://example.com/avatar.png",
        template="http://example.com/avatar/?user={uri}",
    )
    xrd = XRD(links=[link])

    assert xrd.find_link("http://webfinger.net/rel/avatar") is link
    assert (
        xrd.find_link("http://webfinger.net/rel/avatar", attr="template")
        is "http://example.com/avatar/?user={uri}"
    )
    assert xrd.find_link("http://webfinger.net/rel/avatar", attr="nope") is None


def test_complex_links():
    """Regression tests for Issue#2

    See: https://github.com/jcarbaugh/python-xrd/issues/2
    """

    xrd = XRD("9876", properties={"mimetype": "text/plain"})

    # This tests Issue #2
    lnk = Link(
        rel="http://spec.example.net/photo/1.0",
        type="image/jpeg",
        href="http://photos.example.com/gpburdell.jpg",
        properties={"http://spec.example.net/created/1.0": "1970-01-01"},
    )
    xrd.links.append(lnk)

    assert xrd.as_xml()


def testnode_text():
    content = """<?xml version="1.0" ?>
    <XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
        <Property type="http://spec.example.net/version">1.0</Property>
    </XRD>
    """
    doc = parseString(content)
    root = doc.documentElement
    elem = root.getElementsByTagName("Property")[0]
    assert node_text(elem) == "1.0"


def test_node_text_nested():
    content = """<?xml version="1.0" ?>
    <XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
        <Property type="http://spec.example.net/version">
            <Inner>1.0</Inner>
        </Property>
    </XRD>
    """
    doc = parseString(content)
    root = doc.documentElement
    elem = root.getElementsByTagName("Property")[0]
    assert node_text(elem) == "1.0"


def test_is_empty():

    assert is_empty(None)
    assert is_empty("")
    assert is_empty(dict())
    assert is_empty(list())
    assert is_empty(set())
    assert is_empty(tuple())

    assert not is_empty(".")
    assert not is_empty(0)
    assert not is_empty(1)
    assert not is_empty({"a": None})  # dict with an empty value is not empty
    assert not is_empty([None])  # list with an empty value is not empty
    assert not is_empty([1, 2])
    assert not is_empty({1, 2})
    assert not is_empty((1, 2))


def test_strip_dict():

    assert strip_dict({}) == {}

    assert strip_dict({"a": None}) == {}
    assert strip_dict({"a": ""}) == {}
    assert strip_dict({"a": dict()}) == {}
    assert strip_dict({"a": list()}) == {}
    assert strip_dict({"a": set()}) == {}
    assert strip_dict({"a": tuple()}) == {}

    assert strip_dict({"a": "."}) == {"a": "."}
    assert strip_dict({"a": 0}) == {"a": 0}
    assert strip_dict({"a": 1}) == {"a": 1}


def test_parse_xrd_classmethod():
    content = """<?xml version="1.0" ?>
    <XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0" />
    """
    assert XRD.parse_xrd(content)
