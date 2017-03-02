from django.db import migrations
from django.contrib.sites.models import Site
from monumenten import settings

API_DOMAIN = 'API Domain'


def create_site(apps, *args, **kwargs):
    Site.objects.filter(name='API Domain').delete()

    Site.objects.update_or_create(
        domain=settings.DATAPUNT_API_URL,
        name=API_DOMAIN
    )

def delete_site(apps, *args, **kwargs):
    Site.objects.filter(name='API Domain').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('dataset', '0001_initial'), ('sites', '0002_alter_domain_unique'),
    ]

    operations = [

        migrations.RunPython(code=create_site, reverse_code=delete_site),

        migrations.RunSQL(
            f"""
                CREATE VIEW geo_monument_point AS
                SELECT
                  m.naam as display,
                  cast('monumenten/monument' as varchar(30)) as type,
                  site.domain || 'monumenten/monument/' || m.id || '/' AS uri,
                  m.coordinaten AS geometrie
                FROM
                  dataset_monument m , django_site site
                WHERE
                  m.coordinaten IS NOT NULL and site.name = '{API_DOMAIN}';
            """)
    ]
