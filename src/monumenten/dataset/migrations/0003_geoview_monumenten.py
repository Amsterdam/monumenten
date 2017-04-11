from django.db import migrations


from monumenten import settings

API_DOMAIN = 'API Domain'


class Migration(migrations.Migration):

    dependencies = [
        ('dataset', '0001_initial')
    ]

    operations = [
        migrations.RunSQL(
            f"""
                CREATE VIEW geo_monument_point AS
                SELECT
                  m.display_naam as display,
                  cast('monumenten/monument' as varchar(30)) as type,
                  '{settings.DATAPUNT_API_URL}' || 'monumenten/monumenten/' || m.id || '/' AS uri,
                  m.monumentcoordinaten AS geometrie
                FROM
                  dataset_monument m;
            """)
    ]
