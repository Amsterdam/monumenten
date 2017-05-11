import logging

from django.db import connection

log = logging.getLogger(__name__)


def refresh_geo_monument_point():
    with connection.cursor() as cursor:
        cursor.execute("""
REFRESH MATERIALIZED VIEW geo_monument_point;
        """)



