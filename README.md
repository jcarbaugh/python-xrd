# XRD for Python

Extensible Resource Descriptor is a generic format for describing and discovering resources.

python-xrd supports serialization and deserialization of both:

- XML as defined in [XRD 1.0](http://docs.oasis-open.org/xri/xrd/v1.0/xrd-1.0.html), _execpt XRD Signature and XRDS_.
- JSON (JRD) as defined in [RFC 6415](https://www.rfc-editor.org/rfc/rfc6415.html#page-12)

## Basic Usage

```python
from xrd import XRD, Link, Title

xrd = XRD(
    subject="http://example.com/someone",
    properties={"http://spec.example.net/type/person": None},
    links=[
        Link(
            rel="http://spec.example.net/photo/1.0",
            type="image/jpeg",
            href="http://photos.example.com/someone.jpg",
            titles=[Title("User Photo", lang="en"), Title("Benutzerfoto", lang="de")],
            properties={"http://spec.example.net/created/1.0": "1970-01-01"}],
        )
    ],
)
xrd.as_xml()
```

## Tests

### Test Completeness

It's important to ensure test cases were covered for all combinations of
XML/JSON and ser/deser, so completeness is tracked in this chart.
There are additional tests, but these are the ones that need to be the same for all.

| Test                       | XML Ser | XML Deser | JSON Ser | JSON Deser |
| -------------------------- | :-----: | :-------: | :------: | :--------: |
| xml:id                     |    ✓    |     ✓     |   n/a    |    n/a     |
| xml attributes             |    ✓    |     ✓     |   n/a    |    n/a     |
| expires                    |    ✓    |     ✓     |    ✓     |     ✓      |
| subject                    |    ✓    |     ✓     |    ✓     |     ✓      |
| alias                      |    ✓    |     ✓     |    ✓     |     ✓      |
| property                   |    ✓    |     ✓     |    ✓     |     ✓      |
| property / nil             |    ✓    |     ✓     |    ✓     |     ✓      |
| property / multi \*        |    ✓    |     ✓     |    ✓     |     ✓      |
| link                       |    ✓    |     ✓     |    ✓     |     ✓      |
| link / validate            |    ✓    |     ✓     |    ✓     |     ✓      |
| link / title               |    ✓    |     ✓     |    ✓     |     ✓      |
| link / property            |    ✓    |     ✓     |    ✓     |     ✓      |
| link / property / nil      |    ✓    |     ✓     |    ✓     |     ✓      |
| link / property / multi \* |    ✓    |     ✓     |    ✓     |     ✓      |
| XRDS                       |    ✕    |     ✕     |   n/a    |    n/a     |
| signature \*\*             |    ✕    |     ✕     |   n/a    |    n/a     |

\* JRD does not support multiple properties of the same type, per the spec.
When serializing to JSON only the last value will be used if there are
multiple properties of the same type.

\*\* [XRD Signature](http://docs.oasis-open.org/xri/xrd/v1.0/xrd-1.0.html#signature) is not supported
