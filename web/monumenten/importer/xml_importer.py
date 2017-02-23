import xmltodict
import logging
from monumenten.dataset.models import Monument, Complex
from django.contrib.gis.geos import GEOSGeometry, GeometryCollection

log = logging.getLogger(__name__)


def get_complex_id(parent):
    if 'Type' in parent and parent['Type'] == 'Complex':
        complex = Complex.objects.get(id=parent['Id'])
        return complex
    return None


def match(dict, attribute, value):
    return attribute in dict and dict[attribute] == value and True or False


def get_note(item, text_list, text_type, text_status):
    if text_list not in item:
        return None
    return get_note_text(item[text_list], text_type, text_status)


def get_note_text(text_list, text_type, text_status):
    def get_note(text):
        if match(text, 'Type', text_type) and match(text, 'Status', text_status) and 'Notitie' in text:
            return text['Notitie']
        return None

    if type(text_list) != list:
        return get_note(text_list)

    for text in text_list:
        note = get_note(text)
        if note is not None:
            return note
    return None


def get_in_onderzoek(tags):
    def is_onderzoek(tag):
        if 'Type' in tag and tag['Type'] == 'InOnderzoek':
            return True
        return False

    if type(tags) != list:
        return is_onderzoek(tags)

    for tag in tags:
        if is_onderzoek(tag):
            return True
    return False


def get_geometry(item):
    if 'Polygoon' in item:
        gm = GEOSGeometry(item['Polygoon'])
        if gm.geom_type == 'GeometryCollection':
            return gm
        geometry = GeometryCollection(gm)
    elif 'Punt' in item and type(item['Punt']) == list:
        geometry = GeometryCollection()
        for p in item['Punt']:
            geometry.append(GEOSGeometry(p))
    else:
        geometry = None
    return geometry


def update_create_complex(item):
    Complex.objects.update_or_create(
        defaults={
            'id': item['Id'],
            'beschrijving': get_note(item, 'Tekst', 'Beschrijving', 'Afgerond'),
            'monumentnummer': item.get('Monumentnummer', None),
            'naam': item.get('Naam', None),
            'status': item.get('Status', None),
        }, id=item['Id'])


def get_coordinates(point):
    if type(point) == list:
        return GEOSGeometry(point[0], srid=28992)
    return GEOSGeometry(point, srid=28992)


def update_create_monument(item):
    Monument.objects.update_or_create(
        defaults={
            'id': item['Id'],
            'aanwijzingsdatum': item.get('AanwijzingsDatum', None),
            'afbeelding': 'Afbeelding' in item and 'Id' in item['Afbeelding'] and item['Afbeelding']['Id'] or None,
            'architect': item.get('Architect', None),
            'beschrijving': get_note(item, 'Tekst', 'Beschrijving', 'Afgerond'),
            'complex': 'ParentObject' in item and get_complex_id(item['ParentObject']) or None,
            'coordinaten': 'Punt' in item and get_coordinates(item['Punt']) or None,
            'functie': item.get('Functie', None),
            'geometrie': get_geometry(item),
            'in_onderzoek': 'Tag' in item and get_in_onderzoek(item['Tag']) and 'Ja' or 'Nee',
            'monumentnummer': item.get('Monumentnummer', None),
            'naam': item.get('Naam', None),
            'opdrachtgever': item.get('Opdrachtgever', None),
            'pand_sleutel': item.get('PandSleutel', 0),
            'periode_start': item.get('PeriodeStart', None),
            'periode_eind': item.get('PeriodeEind', None),
            'redengevende_omschrijving': get_note(item, 'Tekst', 'Redengevende omschrijving', 'Vastgesteld'),
            'status': item.get('Status', None),
            'type': item.get('Type', None),
        }, id=item['Id'])


def handle(_, item):
    log.info('Importing object with id: {}'.format(item['Id']))
    if 'Type' in item and item['Type'] == 'Complex':
        update_create_complex(item)
    else:
        'ParentObject' in item and update_create_complex(item['ParentObject'])
        update_create_monument(item)
    return True


def import_file(filename):
    log.info('Start import')
    Monument.objects.all().delete()
    with open(filename, "r", encoding='utf-16') as fd:
        xmltodict.parse(fd.read(), item_depth=2, item_callback=handle)
    log.info('Import done')
