import sys

py3 = sys.version_info[0] == 3

if py3:
    import urllib.parse as urlparse
else:
    import urlparse

def netloc_to_host_port(netloc):
    if netloc:
        if ':' in netloc:
            host, port = netloc.split(':')
            return (host, int(port))
        else:
            port = None
            return (netloc, port)
    else:
        raise AssertionError('Should not be here')

def uri(parts):
    uri = parts.path or '/'
    if parts.params:
        uri += ';' + parts.params
    if parts.query:
        uri += '?' + parts.query
    return uri

# XXX figure out if this is still needed and give it a better api
def parse_url(url):
    parsed_url = urlparse.urlparse(url)
    _uri = uri(parsed_url)
    return parsed_url, _uri
