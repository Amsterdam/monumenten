import xmltodict
import logging
from monumenten.dataset.models import Monument
from django.contrib.gis.geos import GEOSGeometry

log = logging.getLogger(__name__)


def get_attribute_from_parent(item, parent, parent_type, attribute):
    if parent not in item:
        return None
    if 'Type' in item[parent] and item[parent]['Type'] == parent_type:
        return item[parent][attribute]
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


def handle(_, item):
    log.info('Importing object with id: {}'.format(item['Id']))
    Monument.objects.update_or_create(
        defaults={
            'id': item['Id'],
            'aanwijzingsdatum': item.get('AanwijzingsDatum', None),
            'architect': item.get('Architect', None),
            'beschrijving': get_note(item, 'Tekst', 'Beschrijving', 'Afgerond'),
            'complex_id': get_attribute_from_parent(item, 'ParentObject', 'Complex', 'Id'),
            'complex_naam': get_attribute_from_parent(item, 'ParentObject', 'Complex', 'Naam'),
            'complex_nummer': get_attribute_from_parent(item, 'ParentObject', 'Complex', 'Monumentnummer'),
            'afbeelding': 'Afbeelding' in item and 'Id' in item['Afbeelding'] and item['Afbeelding']['Id'] or None,
            'functie': item.get('Functie', None),
            'in_onderzoek': 'Tag' in item and get_in_onderzoek(item['Tag']) and 'Ja' or 'Nee',
            'monumentnummer': item.get('Monumentnummer', None),
            'naam': item.get('Naam', None),
            'opdrachtgever': item.get('Opdrachtgever', None),
            'pand_sleutel': item.get('PandSleutel', 0),
            'periode_start': item.get('PeriodeStart', None),
            'periode_eind': item.get('PeriodeEind', None),
            'punt': 'Punt' in item and GEOSGeometry(item['Punt'], srid=28992) or None,
            'polygoon': 'Polygoon' in item and GEOSGeometry(item['Polygoon'], srid=28992) or None,
            'redengevende_omschrijving': get_note(item, 'Tekst', 'Redengevende omschrijving', 'Vastgesteld'),
            'status': item.get('Status', None),
            'type': item.get('Type', None),
        }, id=item['Id'])

    return True


def import_file(filename):
    Monument.objects.all().delete()
    with open(filename, "r", encoding='utf-16') as fd:
        xmltodict.parse(fd.read(), item_depth=2, item_callback=handle)
