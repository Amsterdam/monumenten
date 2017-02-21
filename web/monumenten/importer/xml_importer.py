import xmltodict
from monumenten.dataset.models import Monument


def handle(_, item):
    Monument.objects.update_or_create(id=item['Id'])
    return True


def import_file(filename):
    with open(filename, "r", encoding='utf-16') as fd:
        xmltodict.parse(fd.read(), item_depth=2, item_callback=handle)
