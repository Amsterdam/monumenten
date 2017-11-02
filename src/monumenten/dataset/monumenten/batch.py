from monumenten.dataset.generic import index
from monumenten import settings
from monumenten.dataset import models
from monumenten.dataset.monumenten import documents


class DeleteMonumentenIndexTask(index.DeleteIndexTask):
    index = settings.ELASTIC_INDICES['MONUMENTEN']
    doc_types = [documents.Monument, documents.Complex]


class IndexMonumentenTask(index.ImportIndexTask):
    name = "index monumenten"
    index = settings.ELASTIC_INDICES['MONUMENTEN']

    queryset = models.Monument.objects.filter(
        display_naam__isnull=False).order_by('id')

    def convert(self, obj):
        return documents.from_monument(obj)


class IndexComplexenTask(index.ImportIndexTask):
    name = "index complexen"
    index = settings.ELASTIC_INDICES['MONUMENTEN']

    queryset = models.Complex.objects.filter(
        complexnaam__isnull=False).order_by('id')

    def convert(self, obj):
        return documents.from_complex(obj)
