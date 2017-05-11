import logging

from monumenten.dataset.models import Monument, Complex, Situering

log = logging.getLogger(__name__)


def assert_count(minimal, actual, message):
    if actual < minimal:
        raise Exception("Import failed. {} minimal {}, actual {}".format(message, minimal, actual))


def check_import():
    log.info('Checking import')
    log.info('Checking database count')

    assert_count(9000, Monument.objects.count(), 'monument count')
    assert_count(90, Complex.objects.count(), 'monument count')
    assert_count(50000, Situering.objects.count(), 'monument count')

    log.info('Check done')
