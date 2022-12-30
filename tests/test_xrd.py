from xml.dom.minidom import parseString

from xrd import XRD, Link, _get_text


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


def test_get_text():
    content = """<?xml version="1.0" ?>
    <XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
        <Property type="http://spec.example.net/version">1.0</Property>
    </XRD>
    """
    doc = parseString(content)
    root = doc.documentElement
    elem = root.getElementsByTagName("Property")[0]
    assert _get_text(elem) == "1.0"


def test_get_text_nested():
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
    assert _get_text(elem) == "1.0"
