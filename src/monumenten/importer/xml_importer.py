import logging
import time

import xmltodict
from django.contrib.gis.geos import GEOSGeometry, GeometryCollection, MultiPoint

from monumenten.dataset.models import Monument, Complex, Situering, PandRelatie

log = logging.getLogger(__name__)

functional_errors = []


def match(dict1, attribute, value):
    return attribute in dict1 and dict1[attribute] == value


def match2(dict1, attribute1, attribute2, value):
    return attribute1 in dict1 and attribute2 in dict1[attribute1] and dict1[attribute1][attribute2] == value


def get_note_text(item, text_type, text_status):
    """
    Get Tekst from item with type and status.
    Also return for this Tekst item if value is public.
    This is the case if there is a Tag with Waarde 'tonen'
    There can be multiple Tekst items with the same type and status
    In that case  return the first item with a tag 'tonen'
    """
    text_list = item.get("Tekst")
    if not text_list:
        return None, False

    if type(text_list) != list:
        text_list = [text_list]

    note = None
    public = False
    for text_item in text_list:
        if (match(text_item, 'Type', text_type) and
                match(text_item, 'Status', text_status) and
                'Notitie' in text_item):
            note = text_item['Notitie']
            if match2(text_item, 'Tag', 'Waarde', "tonen"):
                public = True
                break
    return note, public


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
        polygon = item['Polygoon']
        if type(polygon) == list:
            functional_errors.append(
                'Object has more than one Polygon:  {}'.format(item['Id']))
            polygon = polygon[0]
        gm = GEOSGeometry(polygon)
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


def update_create_complex(item, monument_id=None):
    if type(item) == list:
        functional_errors.append(
            'Object has more than one ParentObject:  {}'.format(monument_id))
        item = item[0]
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

        bc, bcp = get_note_text(item, 'Beschrijving', 'Afgerond')

        return Complex.objects.create(
            id=complex_id,
            external_id=complex_id,
            beschrijving_complex=bc,
            beschrijving_complex_publiek=bcp,
            monumentnummer_complex=item.get('Monumentnummer', None),
            complexnaam=item.get('Naam', None),
            complexstatus=item.get('Status', None)
        )


def get_coordinates(point, id1):
    if type(point) == list:
        functional_errors.append(
            'Object has more than 1 coordinate:' + id1)
        return GEOSGeometry(point[0], srid=28992)
    point = GEOSGeometry(point, srid=28992)
    if type(point) == MultiPoint:
        functional_errors.append(
            'Object has a Multipoint coordinate:' + id1)
        return point[0]
    return point


def get_functie(functie, id1):
    if type(functie) == list:
        functional_errors.append(
            'Multiple tag "functie" for Object id: {}'.format(id1))
        return get_functie(functie[0], id1)
    functie = functie.lstrip('_')  # Remove optional underscore at start
    return functie


def get_koppel_status(koppel_status):
    if koppel_status == 'Conversie':
        return 'Actueel'
    return koppel_status


# Global variable for batch creation
batch_size = 50
monuments_batch = []
pandrelatie_batch = []
situeringen_batch = []


def update_create_adress(monument, adress):
    verzend_sleutel = adress.get('VerzendSleutel')
    if verzend_sleutel:
        len1 = verzend_sleutel.__len__()
        assert len1 == 13 or len1 == 15 or len1 == 16
        if len1 == 13:
            log.warning(f'Invalid landelijk id for address {verzend_sleutel}')
            landelijk_id = None
        elif len1 == 15:
            landelijk_id = '0' + verzend_sleutel
        else:
            landelijk_id = verzend_sleutel
    else:
        landelijk_id = None

    situering = Situering(
        external_id=adress['Id'],
        monument=monument,
        betreft_nummeraanduiding=landelijk_id,
        situering_nummeraanduiding='KoppelStatus' in adress and get_koppel_status(
            adress[
                'KoppelStatus']) or None,
        eerste_situering='KoppelEerste' in adress and
                         adress['KoppelEerste'] == 'true' and 'J' or 'N',
        huisnummer='Huisnummer' in adress and adress['Huisnummer'] or None,
        huisletter='Huisletter' in adress and adress['Huisletter'] or None,
        huisnummertoevoeging='Toevoeging' in adress and adress[
            'Toevoeging'] or None,
        postcode='Postcode' in adress and adress['Postcode'] or None,
        straat='Straat' in adress and adress['Straat'] or None
    )
    global situeringen_batch
    situeringen_batch.append(situering)
    return situering


def update_create_adresses(monument, adress):
    main = None
    if type(adress) == list:
        for a in adress:
            situering = update_create_adress(monument, a)
            if main is None or situering.eerste_situering == 'J':
                main = situering

    else:
        main = update_create_adress(monument, adress)
    if main.eerste_situering == 'N':
        msg = "Did not find an address labeled 'KoppelEerste = true' for Monument: {}".format(
            monument.external_id)
        functional_errors.append(msg)
    return main


def format_address(a):
    straat = a.straat and a.straat or ''
    huisnummer = a.huisnummer and ' ' + a.huisnummer or ''
    huisletter = a.huisletter and ' ' + a.huisletter or ''
    huisnummertoevoeging = a.huisnummertoevoeging and ' ' + a.huisnummertoevoeging or ''
    address = straat + huisnummer + huisletter + huisnummertoevoeging
    if a.situering_nummeraanduiding and a.situering_nummeraanduiding != 'Actueel':
        if a.situering_nummeraanduiding == 'Actueel/Via':
            address = 'Betreden via ' + address
        elif a.situering_nummeraanduiding == 'Actueel/Tegenover':
            address = 'Gelegen tegenover ' + address
        elif a.situering_nummeraanduiding == 'Actueel/Bij':
            address = 'Gelegen bij ' + address
    return address


def update_create_monument(item, created_complex):
    global monuments_batch
    global pandrelatie_batch
    global situeringen_batch
    global batch_size

    bm, bmp = get_note_text(item, 'Beschrijving', 'Afgerond')

    rom, romp = get_note_text(item,
                              'Redengevende omschrijving',
                              'Vastgesteld')

    monument = Monument(
        id=item['Id'],
        external_id=item['Id'],
        monument_aanwijzingsdatum=item.get('AanwijzingsDatum', None),
        afbeelding='Afbeelding' in item and 'Id' in item['Afbeelding'] and
                   item['Afbeelding']['Id'] or None,
        architect_ontwerp_monument=item.get('Architect', None),
        beschrijving_monument=bm,
        beschrijving_monument_publiek=bmp,
        complex=created_complex,
        monumentcoordinaten='Punt' in item and get_coordinates(
            item['Punt'], item['Id']) or None,
        oorspronkelijke_functie_monument='Functie' in item and get_functie(
            item['Functie'], item['Id']) or None,
        monumentgeometrie=get_geometry(item),
        in_onderzoek='Tag' in item and get_in_onderzoek(
            item['Tag']) and 'J' or 'N',
        monumentnummer=item.get('Monumentnummer', None),
        monumentnaam=item.get('Naam', None),
        display_naam=item.get('Naam', None),
        opdrachtgever_bouw_monument=item.get('Opdrachtgever', None),
        bouwjaar_start_bouwperiode_monument=item.get('PeriodeStart', None),
        bouwjaar_eind_bouwperiode_monument=item.get('PeriodeEind', None),
        redengevende_omschrijving_monument=rom,
        redengevende_omschrijving_monument_publiek=romp,
        monumentstatus=item.get('Status', None),
        monumenttype=item.get('Type', None),
        heeft_als_grondslag_beperking=item.get('WkpbInschrijfnummer', None))

    if 'Adres' in item:
        main_address = update_create_adresses(monument, item['Adres'])
        if monument.display_naam is None:
            monument.display_naam = format_address(main_address)

    if 'PandSleutel' in item:
        pandsleutels = item['PandSleutel']
        if type(item['PandSleutel']) != list:
            pandsleutels = [pandsleutels]

        for pandsleutel in pandsleutels:
            add_pandrelatie(pandsleutel, monument, pandrelatie_batch)

    monuments_batch.append(monument)
    if len(monuments_batch) > batch_size:
        Monument.objects.bulk_create(monuments_batch)
        monuments_batch = []
        if len(situeringen_batch) > 0:
            Situering.objects.bulk_create(situeringen_batch)
            situeringen_batch = []
        if len(pandrelatie_batch) > 0:
            PandRelatie.objects.bulk_create(pandrelatie_batch)
            pandrelatie_batch = []
    return monument


def add_pandrelatie(id1, monument, relaties):
    """
    Create a new pandrelatie bases on a Monument and a PandId
    :param id1: The pandId
    :param monument: The monument the pand is related to
    :param relaties: The batch of pand<>Monument relations
    :return: None
    """

    len1 = id1.__len__()
    assert len1 == 13 or len1 == 15 or len1 == 16
    if len1 == 13:
        log.warning(f'Invalid landelijk id for pandsleutel {id1}')
        return
    elif len1 == 15:
        landelijk_id = '0' + id1
    else:
        landelijk_id = id1
    relaties.append(
        PandRelatie(
            monument=monument,
            pand_id=landelijk_id
        )
    )


def handle(_, item):
    log.info('Importing object with id: {}'.format(item['Id']))
    if 'Type' in item and item['Type'] == 'Complex':
        update_create_complex(item)
    else:
        if 'ParentObject' in item:
            created_complex = update_create_complex(item['ParentObject'],
                                                    item['Id'])
            update_create_monument(item, created_complex)
        else:
            update_create_monument(item, None)
    return True


def import_file(filename):
    start = time.time()
    log.info('Clean database')
    Situering.objects.all().delete()
    Monument.objects.all().delete()
    PandRelatie.objects.all().delete()
    Complex.objects.all().delete()

    log.info('Start import')
    with open(filename, "r", encoding='utf-16') as fd:
        xmltodict.parse(fd.read(), item_depth=2, item_callback=handle)

    global monuments_batch
    global pandrelatie_batch
    if len(monuments_batch) > 0:
        Monument.objects.bulk_create(monuments_batch)
        monuments_batch = []
        if len(pandrelatie_batch) > 0:
            PandRelatie.objects.bulk_create(pandrelatie_batch)
            pandrelatie_batch = []

    global situeringen_batch
    if len(situeringen_batch) > 0:
        Situering.objects.bulk_create(situeringen_batch)
        situeringen_batch = []

    log.info("Monument count: {}".format(Monument.objects.count()))
    log.info("Complex count: {}".format(Complex.objects.count()))
    log.info("Situering count: {}".format(Situering.objects.count()))

    for e in functional_errors:
        log.info(e)

    total_seconds = time.time() - start
    log.info('Import done in {:.2f} seconds'.format(total_seconds))
