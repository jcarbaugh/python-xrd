Compatible with XRD 1.0 (execpt XRD Signature and XRDS)
http://docs.oasis-open.org/xrd/xrd/v1.0/xrd-1.0.html

Outstanding issues:

- support ds:Signature
- support XRDS
- parsing of Expires date stamp from XML
- more tests are needed

Basic usage::

    from xrd import XRD, Link

    lnk = Link(rel='http://spec.example.net/photo/1.0',
               type='image/jpeg',
               href='http://photos.example.com/gpburdell.jpg')
    lnk.titles.append(('User Photo', 'en'))
    lnk.titles.append(('Benutzerfoto', 'de'))
    lnk.properties.append(('http://spec.example.net/created/1.0', '1970-01-01'))

    xrd = XRD(subject=http://example.com/gpburdell)
    xrd.properties.append('http://spec.example.net/type/person')
    xrd.links.append(lnk)

    xrd.to_xml()
        