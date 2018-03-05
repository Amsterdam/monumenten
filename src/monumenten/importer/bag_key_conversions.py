import logging

from django.db import connection

log = logging.getLogger(__name__)


def update_landelijk_id_nummeraanduiding():
    with connection.cursor() as cursor:
        cursor.execute("""
update dataset_situering s1
set betreft_nummeraanduiding = s2.landelijk_id
from (
select s.id, n.landelijk_id from dataset_situering s join bag_nummeraanduiding n on s.betreft_nummeraanduiding = n.id
) as s2
where s1.id = s2.id
        """)


def update_landelijk_id_pand():
    with connection.cursor() as cursor:
        cursor.execute("""UPDATE dataset_pandrelatie pr
                          SET pand_id = bag_pand.landelijk_id
                          FROM bag_pand
                          WHERE pr.pand_id = bag_pand.id """)
