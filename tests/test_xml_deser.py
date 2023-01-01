import datetime
from xrd import XRD, parse_xml

import pytest


def test_xmlid():
    content = """<?xml version="1.0" ?>
    <XRD xml:id="1234" xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0" />
    """
    xrd = parse_xml(content)
    assert xrd.xml_id == "1234"


def test_expires():
    content = """<?xml version="1.0" ?>
    <XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
        <Expires>2023-01-01T00:00:00Z</Expires>
    </XRD>
    """
    xrd = parse_xml(content)
    assert xrd.expires == datetime.datetime(
        2023, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
    )


def test_subject():
    content = """<?xml version="1.0" ?>
    <XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
        <Subject>acct:someone@example.com</Subject>
    </XRD>
    """
    xrd = parse_xml(content)
    assert xrd.subject == "acct:someone@example.com"


def test_alias():
    content = """<?xml version="1.0" ?>
    <XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
        <Alias>acct:someone@example.com</Alias>
        <Alias>https://example.com/someone</Alias>
    </XRD>
    """
    xrd = parse_xml(content)
    assert xrd.aliases == ["acct:someone@example.com", "https://example.com/someone"]


def test_property():
    content = """<?xml version="1.0" ?>
    <XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
        <Property type="mimetype">text/plain</Property>
    </XRD>
    """
    xrd = parse_xml(content)
    assert "mimetype" in xrd.properties
    assert xrd.properties["mimetype"] == "text/plain"


def test_property_nil():
    content = """<?xml version="1.0" ?>
    <XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <Property type="nothing" xsi:nil="true" />
    </XRD>
    """
    xrd = parse_xml(content)
    # assert "nothing" in xrd.properties
    # assert xrd.properties["mimetype"] is None


def test_property_multiple():
    content = """<?xml version="1.0" ?>
    <XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
        <Property type="http://spec.example.net/version">1.0</Property>
        <Property type="http://spec.example.net/version">2.0</Property>
    </XRD>
    """
    xrd = parse_xml(content)
    assert "http://spec.example.net/version" in xrd.properties
    assert xrd.properties["http://spec.example.net/version"] == ["1.0", "2.0"]


def test_link():

    content = """<?xml version="1.0" ?>
    <XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
        <Link rel="author" href="https://example.com/me" type="text/html" />
    </XRD>
    """
    xrd = parse_xml(content)
    link = xrd.links[0]
    assert link.rel == "author"
    assert link.href == "https://example.com/me"
    assert link.type == "text/html"

    content = """<?xml version="1.0" ?>
    <XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
        <Link template="https://example.com/user/{id}" />
    </XRD>
    """
    xrd = parse_xml(content)
    link = xrd.links[0]
    assert link.template == "https://example.com/user/{id}"


def test_link_validate():
    content = """<?xml version="1.0" ?>
    <XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
        <Link template="a" href="b" />
    </XRD>
    """
    with pytest.raises(ValueError):
        parse_xml(content)


def test_link_title():
    content = """<?xml version="1.0" ?>
    <XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
        <Link>
            <Title>User Photo</Title>
            <Title xml:lang="de">Benutzerfoto</Title>
        </Link>
    </XRD>
    """
    xrd = parse_xml(content)
    link = xrd.links[0]
    assert link.titles[0].value == "User Photo"
    assert link.titles[0].lang == ""
    assert link.titles[1].value == "Benutzerfoto"
    assert link.titles[1].lang == "de"


def test_link_property():
    content = """<?xml version="1.0" ?>
    <XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
        <Link>
            <Property type="http://spec.example.net/created/1.0">1970-01-01</Property>
        </Link>
    </XRD>
    """
    xrd = parse_xml(content)
    link = xrd.links[0]
    assert "http://spec.example.net/created/1.0" in link.properties
    assert link.properties["http://spec.example.net/created/1.0"] == "1970-01-01"


def test_link_property_nil():
    content = """<?xml version="1.0" ?>
    <XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <Link>
            <Property type="http://spec.example.net/created/1.0" xsi:nil="true" />
        </Link>
    </XRD>
    """
    xrd = parse_xml(content)
    link = xrd.links[0]
    assert "http://spec.example.net/created/1.0" in link.properties
    assert link.properties["http://spec.example.net/created/1.0"] == None


def test_link_property_multiple():
    content = """<?xml version="1.0" ?>
    <XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <Link>
            <Property type="http://spec.example.net/version">1.0</Property>
            <Property type="http://spec.example.net/version">2.0</Property>
        </Link>
    </XRD>
    """
    xrd = parse_xml(content)
    link = xrd.links[0]
    assert "http://spec.example.net/version" in link.properties
    assert link.properties["http://spec.example.net/version"] == ["1.0", "2.0"]


def test_unknown_element():
    content = """<?xml version="1.0" ?>
    <XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <Pineapple />
    </XRD>
    """
    parse_xml(content)


def test_xrd_attributes():
    content = """<?xml version="1.0" ?>
    <XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0"
        xmlns:foo="http://example.com/foo">
    </XRD>
    """
    xrd = parse_xml(content)
    assert "xmlns:foo" in xrd.attributes
    assert xrd.attributes["xmlns:foo"] == "http://example.com/foo"
