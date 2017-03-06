import xmltodict
import logging
from monumenten.dataset.models import Monument, Complex, Situering
from django.contrib.gis.geos import GEOSGeometry, GeometryCollection

log = logging.getLogger(__name__)

functional_errors = []


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

    for text_item in text_list:
        note = get_note(text_item)
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

    for tag_item in tags:
        if is_onderzoek(tag_item):
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
    complex_id = item['Id']
    try:
        return Complex.objects.get(external_id=complex_id)
    except Complex.DoesNotExist:
        if 'Type' in item and item['Type'] != 'Complex':
            functional_errors.append(
                'Unexpected Type {} for ParentObject : {}'.format(item['Type'],
                                                                  complex_id))
        if 'Punt' in item or 'Adres' in item:
            functional_errors.append(
                'Unexpected elements Punt and/or Adres for Complex:' +
                complex_id)
        return Complex.objects.create(
            external_id=complex_id,
            beschrijving=get_note(item, 'Tekst', 'Beschrijving', 'Afgerond'),
            monumentnummer=item.get('Monumentnummer', None),
            complex_naam=item.get('Naam', None),
            status=item.get('Status', None)
        )


def get_coordinates(point):
    if type(point) == list:
        return GEOSGeometry(point[0], srid=28992)
    return GEOSGeometry(point, srid=28992)


def convert_to_landelijk_id(id, id_code):
    """3630000092647 --> 0363200000092647
    Landelijke identificatiecode
Lijst
Een landelijke identificatiecode bestaat uit 16 cijfers.
De eerste 4 zijn gereserveerd voor de gemeentecode (0363).
De 2 cijfers daarna duiden een type BAG object aan:
10 = een pand, 20 = een nummeraanduiding
30 = een openbare ruimte
01 = een verblijfsobject
02 = een ligplaats
03 = een standplaats
De laatste 10 cijfers zijn gereserveerd voor het volgnummer
"""
    assert id.__len__() == 13
    return id.replace('363', '0363' + id_code, 1)


def update_create_adress(monument, adress):
    Situering.objects.create(
        external_id=adress['Id'],
        monument=monument,
        betreft='VerzendSleutel' in adress and convert_to_landelijk_id(
            adress['VerzendSleutel'], '20') or None,
        situering_nummeraanduiding='KoppelStatus' in adress and adress[
            'KoppelStatus'] or None,
        eerste_situering='KoppelEerste' in adress
                         and adress['KoppelEerste'] == 'true' and 'Ja' or 'Nee',
        huisnummer='Huisnummer' in adress and adress['Huisnummer'] or None,
        huisletter='Huisletter' in adress and adress['Huisletter'] or None,
        huisnummertoevoeging='Toevoeging' in adress and adress[
            'Toevoeging'] or None,
        postcode='Postcode' in adress and adress['Postcode'] or None,
        straat='Straat' in adress and adress['Straat'] or None
    )


def update_create_adresses(monument, adress):
    if type(adress) == list:
        for a in adress:
            update_create_adress(monument, a)
    else:
        update_create_adress(monument, adress)


def update_create_monument(item, created_complex):
    monument = Monument.objects.create(
        external_id=item['Id'],
        aanwijzingsdatum=item.get('AanwijzingsDatum', None),
        afbeelding='Afbeelding' in item and 'Id' in item['Afbeelding'] and
                   item['Afbeelding']['Id'] or None,
        architect=item.get('Architect', None),
        beschrijving=get_note(item, 'Tekst', 'Beschrijving', 'Afgerond'),
        complex=created_complex,
        coordinaten='Punt' in item and get_coordinates(item['Punt']) or None,
        functie=item.get('Functie', None),
        geometrie=get_geometry(item),
        in_onderzoek='Tag' in item and get_in_onderzoek(
            item['Tag']) and 'Ja' or 'Nee',
        monumentnummer=item.get('Monumentnummer', None),
        naam=item.get('Naam', None),
        opdrachtgever=item.get('Opdrachtgever', None),
        pand_sleutel='PandSleutel' in item and convert_to_landelijk_id(
            item['PandSleutel'], '10') or None,
        periode_start=item.get('PeriodeStart', None),
        periode_eind=item.get('PeriodeEind', None),
        redengevende_omschrijving=get_note(item, 'Tekst',
                                           'Redengevende omschrijving',
                                           'Vastgesteld'),
        status=item.get('Status', None),
        type=item.get('Type', None))
    'Adres' in item and update_create_adresses(monument, item['Adres'])
    return monument


def handle(_, item):
    log.info('Importing object with id: {}'.format(item['Id']))
    if 'Type' in item and item['Type'] == 'Complex':
        update_create_complex(item)
    else:
        if 'ParentObject' in item:
            created_complex = update_create_complex(item['ParentObject'])
            update_create_monument(item, created_complex)
        else:
            update_create_monument(item, None)
    return True


def import_file(filename):
    log.info('Clean database')
    Situering.objects.all().delete()
    Monument.objects.all().delete()
    Complex.objects.all().delete()

    log.info('Start import')
    Monument.objects.all().delete()
    with open(filename, "r", encoding='utf-16') as fd:
        xmltodict.parse(fd.read(), item_depth=2, item_callback=handle)
    log.info("Monument count: {}".format(Monument.objects.count()))
    log.info("Complex count: {}".format(Complex.objects.count()))
    log.info("Situering count: {}".format(Situering.objects.count()))

    for e in functional_errors:
        log.info(e)
    log.info('Import done')