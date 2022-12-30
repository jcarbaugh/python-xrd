import json

from xrd import XRD, parse_xml

"""
Taken from examples in RFC 6415 https://datatracker.ietf.org/doc/rfc6415/
"""

XML_DOC = """<?xml version='1.0' encoding='UTF-8'?>
<XRD xmlns='http://docs.oasis-open.org/ns/xri/xrd-1.0'
        xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>

    <Subject>http://blog.example.com/article/id/314</Subject>
    <Expires>2010-01-30T09:30:00Z</Expires>

    <Alias>http://blog.example.com/cool_new_thing</Alias>
    <Alias>http://blog.example.com/steve/article/7</Alias>

    <Property type='http://blgx.example.net/ns/version'>1.2</Property>
    <Property type='http://blgx.example.net/ns/version'>1.3</Property>
    <Property type='http://blgx.example.net/ns/ext' xsi:nil='true' />

    <Link rel='author' type='text/html'
        href='http://blog.example.com/author/steve'>
    <Title>About the Author</Title>
    <Title xml:lang='en-us'>Author Information</Title>
    <Property type='http://example.com/role'>editor</Property>
    </Link>

    <Link rel='author' href='http://example.com/author/john'>
    <Title>The other guy</Title>
    <Title>The other author</Title>
    </Link>
    <Link rel='copyright'
        template='http://example.com/copyright?id={uri}' />
</XRD>"""

JRD_DOC = """{
    "subject":"http://blog.example.com/article/id/314",
    "expires":"2010-01-30T09:30:00Z",

    "aliases":[
    "http://blog.example.com/cool_new_thing",
    "http://blog.example.com/steve/article/7"],

    "properties":{
    "http://blgx.example.net/ns/version":"1.3",
    "http://blgx.example.net/ns/ext":null
    },

    "links":[
    {
        "rel":"author",
        "type":"text/html",
        "href":"http://blog.example.com/author/steve",
        "titles":{
        "default":"About the Author",
        "en-us":"Author Information"
        },
        "properties":{
        "http://example.com/role":"editor"
        }
    },
    {
        "rel":"author",
        "href":"http://example.com/author/john",
        "titles":{
        "default":"The other author"
        }
    },
    {
        "rel":"copyright",
        "template":"http://example.com/copyright?id={uri}"
    }
    ]
}"""


def test_xml_to_jrd_conversion():
    xrd = parse_xml(XML_DOC)
    parsed_data = json.loads(xrd.as_json())
    example_data = json.loads(JRD_DOC)
    assert parsed_data == example_data
