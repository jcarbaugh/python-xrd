import datetime
import json
from xrd import XRD, Link, Title

import pytest


def test_expires():
    xrd = XRD(
        expires=datetime.datetime(2023, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
    )
    data = json.loads(xrd.as_json())
    assert data["expires"] == "2023-01-01T00:00:00Z"


def test_subject():
    xrd = XRD(subject="acct:someone@example.com")
    data = json.loads(xrd.as_json())
    assert data["subject"] == "acct:someone@example.com"


def test_aliases():
    xrd = XRD(aliases=["acct:someone@example.com", "https://example.com/someone"])
    data = json.loads(xrd.as_json())
    assert data["aliases"][0] == "acct:someone@example.com"
    assert data["aliases"][1] == "https://example.com/someone"


def test_property():
    xrd = XRD(
        properties={"mimetype": "text/plain"},
    )
    data = json.loads(xrd.as_json())
    assert "mimetype" in data["properties"]
    assert data["properties"]["mimetype"] == "text/plain"


def test_property_nil():
    xrd = XRD(
        properties={"mimetype": None},
    )
    data = json.loads(xrd.as_json())
    assert "mimetype" in data["properties"]
    assert data["properties"]["mimetype"] == None


def test_property_multiple():
    xrd = XRD(
        properties={"http://spec.example.net/version": ["1.0", "2.0"]},
    )
    data = json.loads(xrd.as_json())
    assert "http://spec.example.net/version" in data["properties"]
    assert data["properties"]["http://spec.example.net/version"] == "2.0"


def test_link():
    xrd = XRD(
        links=[Link(rel="author", href="https://example.com/me", type="text/html")]
    )
    data = json.loads(xrd.as_json())
    link = data["links"][0]
    assert link["rel"] == "author"
    assert link["href"] == "https://example.com/me"
    assert link["type"] == "text/html"

    xrd = XRD(links=[Link(template="https://example.com/user/{id}")])
    data = json.loads(xrd.as_json())
    link = data["links"][0]
    assert link["template"] == "https://example.com/user/{id}"


def test_link_validate():
    xrd = XRD(links=[Link(template="a", href="b")])
    with pytest.raises(ValueError):
        xrd.as_json()


def test_link_title():
    xrd = XRD(links=[Link(titles=[Title("User Photo"), Title("Benutzerfoto", "de")])])
    data = json.loads(xrd.as_json())
    link = data["links"][0]
    assert link["titles"]["default"] == "User Photo"
    assert link["titles"]["de"] == "Benutzerfoto"


def test_link_property():
    xrd = XRD(
        links=[Link(properties={"http://spec.example.net/created/1.0": "1970-01-01"})]
    )
    data = json.loads(xrd.as_json())
    link = data["links"][0]
    assert "http://spec.example.net/created/1.0" in link["properties"]
    assert link["properties"]["http://spec.example.net/created/1.0"] == "1970-01-01"


def test_link_property_nil():
    xrd = XRD(links=[Link(properties={"http://spec.example.net/created/1.0": None})])
    data = json.loads(xrd.as_json())
    link = data["links"][0]
    assert "http://spec.example.net/created/1.0" in link["properties"]
    assert link["properties"]["http://spec.example.net/created/1.0"] == None


def test_link_property_multiple():
    xrd = XRD(
        links=[Link(properties={"http://spec.example.net/version": ["1.0", "2.0"]})],
    )
    data = json.loads(xrd.as_json())
    link = data["links"][0]
    assert "http://spec.example.net/version" in link["properties"]
    assert link["properties"]["http://spec.example.net/version"] == "2.0"
