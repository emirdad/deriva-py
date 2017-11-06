import io
import re
import sys

from . import urlquote
from .utils.hash_utils import compute_hashes

if sys.version_info > (3,):
    from urllib.parse import urlsplit, urlunsplit
else:
    from urlparse import urlsplit, urlunsplit


class VersionedCatalogError(Exception):
        """Exception raised for errors in the input.

        Attributes:
            expression -- input expression in which the error occurred
            message -- explanation of the error
        """

        def __init__(self, message):
            self.message = message


#def checksum_str(text, hashalg='sha256'):
#        """
#        """
#        fd = io.BytesIO(text).encode())
#
#        # Get back a dictionary of hash codes....
#       hashcodes = compute_hashes(fd, [hashalg])
#       return hashcodes[hashalg][0]


def parse_catalog_uri(uri):
    """
    Parse a URL to an ermrest catalog, defaulting the version to the current version if not provided

    :param uri: catalog URL

    """
    urlparts = urlsplit(uri, scheme='https')

    scheme = urlparts.scheme
    host = urlparts.netloc
    query = urlparts.query
    fragment = urlparts.fragment

    if not urlparts.path.startswith('/ermrest/catalog'):
        raise VersionedCatalogError('Catalog URL must start with ermrest/catalog')

    # Look in the path and pull out id, version number if it exists, and ermrest path....
    catparts = re.match(r'(/ermrest/catalog/(?P<id>\d+)(@(?P<version>[^/]+))?)?(?P<path>.*)', urlparts.path)

    cid, version, path = catparts.group('id', 'version', 'path')
    if host is None:
        raise VersionedCatalogError('ERMRest host name required')
    if cid is None:
        raise VersionedCatalogError('Catalog ID number required')
    if not str(cid).isdigit():
        raise VersionedCatalogError('Catalog ID must be an integer: {0}'.format(cid))
   # should check snapshot ID here....

    return {'scheme': scheme, 'host': host, 'query': query, 'fragment': fragment,
            'id': cid, 'version': version, 'path': path}


def current_catalog_version(catalog):
    return catalog.get('/').json()['version']


def path_version(path):
    vc = parse_catalog_uri(path)
    return vc['version']


def versioned_path(path, version=None):
    """
    Add or remover snapshot ids from a ERMRest path.

    :param path:
    :param version: Version number to use for the path.  If None, remove the version number if it exists.
    :return: versioned path
    """
    vc = parse_catalog_uri(path)

    if len(vc['path']) > 0 and vc['path'][0] != '/':
        vc['path'] = '/' + vc['path']

    if version is None:
        vpath = 'ermrest/catalog/{0}{1}'.format(vc['id'], vc['path'])
    else:
        vpath = 'ermrest/catalog/{0}@{1}{2}'.format(vc['id'],version,vc['path'])

    url = urlunsplit([vc['scheme'], vc['host'], vpath, vc['query'], vc['fragment']])
    return url