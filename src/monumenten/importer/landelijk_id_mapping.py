import csv
import os

from monumenten.objectstore.objectstore_gob import download_dir, get_files

_mapping = dict()
_initialized = False


def resolve_file(path, code, extension='dat'):
    if not code:
        raise ValueError("No code specified")

    prefix = code + '_'
    matches = [os.path.join(path, f) for f in os.listdir(path) if f.startswith(prefix) and f.endswith(extension)]
    if not matches:
        raise ValueError("Could not find file starting with {} in {}".format(prefix, path))
    matches_with_mtime = [(os.path.getmtime(f), f) for f in matches]
    match = sorted(matches_with_mtime)[-1]
    return match[1]


def _read_landelijk_id_mapping(path, file_code):
    source = resolve_file(path, file_code)
    result = dict()
    with open(source) as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)  # skip header
        for row in reader:
            if len(row) >= 2:
                result[row[0]] = row[1]

    return result


def initialize():
    """
    Read mapping from amsterdam sleutel to landelijk_id for Pand and Nummeraanduiding into dictionary
    """
    global _initialized, _mapping
    if _initialized:
        return

    prefixes = ('PND', 'NUM')
    get_files(prefixes)

    path = download_dir + 'bag/BAG_LandelijkeSleutel'

    for code in prefixes:
        d = _read_landelijk_id_mapping(path, code)
        _mapping.update(d)

    _initialized = True


def initialize_test(data: dict):
    global _initialized, _mapping
    _mapping.update(data)
    _initialized = True


def get_landelijk_id(ams_sleutel: str):
    global _initialized, _mapping
    if not _initialized:
        raise ValueError("landelijk_id_mapping")
    return _mapping.get(ams_sleutel)
