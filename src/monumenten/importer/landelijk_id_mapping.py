import csv
import os
import time
import zipfile

from dateutil import parser

from monumenten.objectstore.objectstore_bag import find_sleutel_file, copy_file_from_objectstore, download_dir

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


def unzip_files(zipsource, directory, mtime):
    """
    Unzip single files to the right target directory
    """
    # Extract files to the expected location
    for fullname in zipsource.namelist():
        zipsource.extract(fullname, directory)
        path = f"{directory}/{fullname}"
        os.utime(path, (mtime, mtime))


def initialize():
    """
    Read mapping from amsterdam sleutel to landelijk_id for Pand and Nummeraanduiding into dictionary
    """
    global _initialized, _mapping
    if _initialized:
        return
    sleutelzipfile = find_sleutel_file()
    if not sleutelzipfile:
        raise ValueError("sleutelfile not found")
    copy_file_from_objectstore(sleutelzipfile)

    zipsource = zipfile.ZipFile(download_dir + sleutelzipfile, 'r')
    zip_date = sleutelzipfile.split('/')[-1].split('_')[0]
    zip_date = parser.parse(zip_date)
    zip_seconds = time.mktime(zip_date.timetuple())
    unzip_files(zipsource, download_dir, zip_seconds)

    path = download_dir + 'Alle_Producten/BAG/BAG_LandelijkeSleutel/ASCII/'
    for code in ('PND', 'NUM'):
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
