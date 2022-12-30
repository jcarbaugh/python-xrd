import datetime

import isodate  # type: ignore
import pytest

from xrd import parse_json


def test_expires():
    jrd = """{"expires": "2023-01-01T00:00:00Z"}"""
    xrd = parse_json(jrd)
    assert xrd.expires == datetime.datetime(
        2023, 1, 1, 0, 0, 0, tzinfo=isodate.tzinfo.Utc()
    )


def test_subject():
    jrd = """{"subject": "acct:someone@example.com"}"""
    xrd = parse_json(jrd)
    assert xrd.subject == "acct:someone@example.com"


def test_aliases():
    jrd = """{"aliases": ["acct:someone@example.com", "https://example.com/someone"]}"""
    xrd = parse_json(jrd)
    assert xrd.aliases[0] == "acct:someone@example.com"
    assert xrd.aliases[1] == "https://example.com/someone"


def test_property():
    jrd = """{"properties": {"mimetype": "text/plain"}}"""
    xrd = parse_json(jrd)
    assert "mimetype" in xrd.properties
    assert xrd.properties["mimetype"] == "text/plain"


def test_property_nil():
    jrd = """{"properties": {"mimetype": null}}"""
    xrd = parse_json(jrd)
    assert "mimetype" in xrd.properties
    assert xrd.properties["mimetype"] == None


def test_property_multiple():
    jrd = """{"properties": {"http://spec.example.net/version": ["1.0", "2.0"]}}"""
    xrd = parse_json(jrd)
    assert "http://spec.example.net/version" in xrd.properties
    assert xrd.properties["http://spec.example.net/version"] == "2.0"


def test_link():

    jrd = """{"links": [{"rel": "author", "href": "https://example.com/me", "type": "text/html"}]}"""
    xrd = parse_json(jrd)
    link = xrd.links[0]
    assert link.rel == "author"
    assert link.href == "https://example.com/me"
    assert link.type == "text/html"

    jrd = """{"links": [{"template": "https://example.com/user/{id}"}]}"""
    xrd = parse_json(jrd)
    link = xrd.links[0]
    assert link.template == "https://example.com/user/{id}"


def test_link_validate():
    jrd = """{"links": [{"template": "a", "href": "b"}]}"""
    with pytest.raises(ValueError):
        parse_json(jrd)


def test_link_title():
    jrd = """{"links": [{"titles": {"default": "User Photo", "de": "Benutzerfoto"}}]}"""
    xrd = parse_json(jrd)
    link = xrd.links[0]
    assert link.titles[0].value == "User Photo"
    assert link.titles[0].lang == "default"
    assert link.titles[1].value == "Benutzerfoto"
    assert link.titles[1].lang == "de"


def test_link_property():
    jrd = """{"links": [{"properties": {"http://spec.example.net/created/1.0": "1970-01-01"}}]}"""
    xrd = parse_json(jrd)
    link = xrd.links[0]
    assert "http://spec.example.net/created/1.0" in link.properties
    assert link.properties["http://spec.example.net/created/1.0"] == "1970-01-01"


def test_link_property_nil():
    jrd = (
        """{"links": [{"properties": {"http://spec.example.net/created/1.0": null}}]}"""
    )
    xrd = parse_json(jrd)
    link = xrd.links[0]
    assert "http://spec.example.net/created/1.0" in link.properties
    assert link.properties["http://spec.example.net/created/1.0"] == None


def test_link_property_multiple():
    jrd = """{"links": [{"properties": {"http://spec.example.net/version": ["1.0", "2.0"]}}]}"""
    xrd = parse_json(jrd)
    link = xrd.links[0]
    assert "http://spec.example.net/version" in link.properties
    assert link.properties["http://spec.example.net/version"] == "2.0"


def test_unkown_attribute():
    jrd = """{"pineapple": null}"""
    parse_json(jrd)
