import logging
import os
import re
from functools import lru_cache

from swiftclient.client import Connection

log = logging.getLogger(__name__)

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("swiftclient").setLevel(logging.WARNING)

os_connect = {
    'auth_version': '2.0',
    'authurl': 'https://identity.stack.cloudvps.com/v2.0',
    'user': 'bag_brk',
    'key': os.getenv('BAG_OBJECTSTORE_PASSWORD', 'insecure'),
    'tenant_name': 'BGE000081_BAG',
    'os_options': {
        'tenant_id': '4f2f4b6342444c84b3580584587cfd18',
        'region_name': 'NL',
    }
}

container = 'Diva'
import_folder = 'Zip_bestanden'
download_dir = '/tmp/bag/'
file_pattern = 'BAG_L_SLEUTEL'

# 20190819_BAG_L_SLEUTEL.zip

@lru_cache(maxsize=None)
def get_conn():
    assert os.getenv('BAG_OBJECTSTORE_PASSWORD')
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


def split_prefix(lst):
    """
    splits of all but the last
    """
    return '_'.join(lst.split('_')[:-1])


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


def find_sleutel_file():
    filenames = []
    p = re.compile(r'Zip_bestanden/\d{8}_BAG_L_SLEUTEL.zip')
    for filename in fetch_import_file_names():
        if p.match(filename):
            filenames.append(filename)

    filenames.sort(reverse=True)
    return filenames[0] if filenames else None
