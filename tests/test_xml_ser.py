import datetime

import pytest

from xrd import XRD, Link, Title, node_text


def test_xmlid():
    xrd = XRD("9876")
    doc = xrd.as_xml().documentElement
    assert doc.getAttribute("xml:id") == "9876"


def test_expires():
    xrd = XRD(
        expires=datetime.datetime(2023, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
    )
    doc = xrd.as_xml().documentElement
    elem = doc.getElementsByTagName("Expires")[0]
    assert node_text(elem) == "2023-01-01T00:00:00Z"


def test_subject():
    xrd = XRD(subject="acct:someone@example.com")
    doc = xrd.as_xml().documentElement
    elem = doc.getElementsByTagName("Subject")[0]
    assert node_text(elem) == "acct:someone@example.com"


def test_aliases():
    xrd = XRD(aliases=["acct:someone@example.com", "https://example.com/someone"])
    doc = xrd.as_xml().documentElement
    elems = doc.getElementsByTagName("Alias")
    assert node_text(elems[0]) == "acct:someone@example.com"
    assert node_text(elems[1]) == "https://example.com/someone"


def test_property():
    xrd = XRD(
        properties={"mimetype": "text/plain"},
    )
    doc = xrd.as_xml().documentElement
    elem = doc.getElementsByTagName("Property")[0]
    assert elem.getAttribute("type") == "mimetype"
    assert node_text(elem) == "text/plain"


def test_property_nil():
    xrd = XRD(
        properties={"mimetype": None},
    )
    doc = xrd.as_xml().documentElement
    assert doc.getAttribute("xmlns:xsi") == "http://www.w3.org/2001/XMLSchema-instance"

    elem = doc.getElementsByTagName("Property")[0]
    assert elem.getAttribute("type") == "mimetype"
    assert elem.getAttribute("xsi:nil").lower() == "true"
    assert node_text(elem) is None


def test_property_multiple():
    xrd = XRD(
        properties={"http://spec.example.net/version": ("1.0", "2.0")},
    )
    doc = xrd.as_xml().documentElement
    elems = doc.getElementsByTagName("Property")
    assert len(elems) == 2
    assert set(e.getAttribute("type") for e in elems) == {
        "http://spec.example.net/version"
    }
    assert sorted(node_text(e) for e in elems) == ["1.0", "2.0"]


def test_link():
    xrd = XRD(
        links=[Link(rel="author", href="https://example.com/me", type="text/html")]
    )
    doc = xrd.as_xml().documentElement
    link = doc.getElementsByTagName("Link")[0]
    assert link.getAttribute("rel") == "author"
    assert link.getAttribute("href") == "https://example.com/me"
    assert link.getAttribute("type") == "text/html"

    xrd = XRD(links=[Link(template="https://example.com/user/{id}")])
    doc = xrd.as_xml().documentElement
    link = doc.getElementsByTagName("Link")[0]
    assert link.getAttribute("template") == "https://example.com/user/{id}"


def test_link_validate():
    xrd = XRD(links=[Link(template="a", href="b")])
    with pytest.raises(ValueError):
        xrd.as_xml()


def test_link_title():
    xrd = XRD(links=[Link(titles=[Title("User Photo"), Title("Benutzerfoto", "de")])])
    doc = xrd.as_xml().documentElement
    link = doc.getElementsByTagName("Link")[0]
    titles = link.getElementsByTagName("Title")

    assert node_text(titles[0]) == "User Photo"
    assert titles[0].getAttribute("xml:lang") == ""

    assert node_text(titles[1]) == "Benutzerfoto"
    assert titles[1].getAttribute("xml:lang") == "de"


def test_link_property():
    xrd = XRD(
        links=[Link(properties={"http://spec.example.net/created/1.0": "1970-01-01"})]
    )
    doc = xrd.as_xml().documentElement
    link = doc.getElementsByTagName("Link")[0]
    elem = link.getElementsByTagName("Property")[0]
    assert elem.getAttribute("type") == "http://spec.example.net/created/1.0"
    assert node_text(elem) == "1970-01-01"


def test_link_property_nil():
    xrd = XRD(links=[Link(properties={"http://spec.example.net/created/1.0": None})])
    doc = xrd.as_xml().documentElement
    link = doc.getElementsByTagName("Link")[0]
    elem = link.getElementsByTagName("Property")[0]
    assert elem.getAttribute("type") == "http://spec.example.net/created/1.0"
    assert elem.getAttribute("xsi:nil").lower() == "true"
    assert node_text(elem) is None


def test_link_property_multiple():
    xrd = XRD(
        links=[Link(properties={"http://spec.example.net/version": ["1.0", "2.0"]})],
    )
    doc = xrd.as_xml().documentElement
    link = doc.getElementsByTagName("Link")[0]
    elems = link.getElementsByTagName("Property")
    assert len(elems) == 2
    assert set(e.getAttribute("type") for e in elems) == {
        "http://spec.example.net/version"
    }
    assert sorted(node_text(e) for e in elems) == ["1.0", "2.0"]


def test_xrd_attributes():
    xrd = XRD(attributes={"xmlns:foo": "http://example.com/foo"})
    doc = xrd.as_xml().documentElement
    assert doc.getAttribute("xmlns:foo") == "http://example.com/foo"
