import logging
import os
import re
from collections import defaultdict
from functools import lru_cache

from swiftclient.client import Connection

log = logging.getLogger(__name__)

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("swiftclient").setLevel(logging.WARNING)

os_connect = {
    'auth_version': '2.0',
    'authurl': 'https://identity.stack.cloudvps.com/v2.0',
    'user': 'GOB_user',
    'key': os.getenv('GOB_OBJECTSTORE_PASSWORD', 'insecure'),
    'tenant_name': 'BGE000081_GOB',
    'os_options': {
        'tenant_id': '2ede4a78773e453db73f52500ef748e5',
        'region_name': 'NL',
    }
}

container = 'productie'   # Always use production for monumenten
import_folder = 'bag/BAG_LandelijkeSleutel'
download_dir = '/tmp/gob/'


@lru_cache(maxsize=None)
def get_conn():
    assert os.getenv('GOB_OBJECTSTORE_PASSWORD')
    return Connection(**os_connect)


def get_full_container_list(container_name, **kwargs):
    """
    Return a listing of filenames in container `container_name`
    :param container_name:
    :param connect
    :param kwargs:
    :return:
    """
    limit = 10000
    kwargs['limit'] = limit
    seed = []
    _, page = get_conn().get_container(container_name, **kwargs)
    seed.extend(page)

    while len(page) == limit:
        # keep getting pages..
        kwargs['marker'] = seed[-1]['name']
        _, page = get_conn().get_container(container_name, **kwargs)
        seed.extend(page)
    return seed


def copy_file_from_objectstore(file_name):
    os.makedirs(download_dir + import_folder, exist_ok=True)
    destination = download_dir + file_name
    log.info("Download file {} to {}".format(file_name, destination))
    with open(destination, 'wb') as f:
        f.write(get_conn().get_object(container, file_name)[1])
    return destination


def fetch_import_file_names():
    files = []
    for file_object in get_full_container_list(container,
                                               prefix=import_folder):
        if file_object['content_type'] != 'application/directory':
            log.info("Found file {}".format(file_object['name']))
            files.append(file_object['name'])
    return files


def get_files(patterns: list):
    filenames = defaultdict(list)
    pattern = '|'.join(patterns)
    p = re.compile(rf'bag/BAG_LandelijkeSleutel/({pattern})_\d{{8}}.dat')
    for filename in fetch_import_file_names():
        m = p.match(filename)
        if m:
            prefix = m.group(1)
            filenames[prefix].append(filename)

    for values in filenames.values():
        values.sort(reverse=True)
        copy_file_from_objectstore(values[0])
