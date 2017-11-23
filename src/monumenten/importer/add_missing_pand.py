import logging
import datetime
import time
import re
import grequests
import gevent
from requests import Session
from gevent.queue import JoinableQueue
from monumenten.dataset.models import Monument
# NOTE : The previous two lines should also be set in manage.py
# Other we get unpredictable recursion overflow errors
from gevent import monkey
monkey.patch_all(thread=False, select=False)

log = logging.getLogger(__name__)

STATS = dict(
    start=time.time(),
    correcties=0,
    onbekend=0,
    total=0,
    fixs=0,
    left=0,
)

# the amount of concurrent workers that do requests
# to the search api
WORKERS = 10

ACC = "https://acc.api.data.amsterdam.nl"

# We search against ACC to not pollute graphs in kibana
# https://api.data.amsterdam.nl/atlas/search/adres/?q=Kalverstraat%2028-H"
SEARCH_ADRES_URL = '{}/atlas/search/adres/'.format(ACC)

# https://acc.api.data.amsterdam.nl/bag/pand/?verblijfsobjecten__id=0363010000696759
SEARCH_PAND_URL = '{}/bag/pand/'.format(ACC)

SEARCHES_QUEUE = JoinableQueue(maxsize=500)


def add_missing_pand():
    """
    Do  a search with the address of monument where type is Pand betreft_pand is missing
    """
    status_job = gevent.spawn(fix_counter)
    missing_pand_monuments = list(Monument.objects.all().filter(betreft_pand__isnull=True, monumenttype='Pand'))

    count = len(missing_pand_monuments)
    if count == 0:
        return
    log.info('Start Finding and correct missing panden for {} monuments'.format(count))
    STATS['total'] = count
    jobs = [gevent.spawn(create_search_verblijfsobject_tasks, missing_pand_monuments)]
    for _ in range(WORKERS):
        jobs.append(
            gevent.spawn(async_get_verblijfsobject))
    with gevent.Timeout(3600, False):
        # wait untill all search tasks are done
        # but no longer than an hour
        gevent.joinall(jobs)

    # check if we did a good job doing corrections.
    # normally about ~60 invalid locations left of 10.000
    # assert invalid_locations.count() < 800

    status_job.kill()
    # log end result
    total_seconds = time.time() - STATS['start']
    log.info('\nCorrecties %d\nNot found %d\nTotal Duration %i m: %i\n',
             STATS['correcties'],
             STATS['onbekend'],
             total_seconds / 60.0, total_seconds % 60)


def create_search_verblijfsobject_tasks(missing_pand_monuments):
    for mpm in missing_pand_monuments:
        s = mpm.situeringen.all().filter(eerste_situering='J')
        if s and len(s) > 0:
            address = str(s[0]).lower()
            while SEARCHES_QUEUE.full():
                gevent.sleep(2)
            SEARCHES_QUEUE.put([mpm, address])
        else:
            log.error("Missing address for monument %s", mpm)


def async_get_verblijfsobject():
    while not SEARCHES_QUEUE.empty():
        args = SEARCHES_QUEUE.get()
        task = SearchAddressTask(*args)
        try:
            task.determine_verblijfsobject()
        except Exception as exp:
            # when tasks fails.. continue..
            log.error('\n\n\n')
            log.error(exp)
            log.error('\n\n\n')


class SearchAddressTask:
    def __init__(self, monument, query_string):
        self.monument = monument
        # originele input
        self.query_string = query_string
        self.session = Session()

    def get_response(self, parameters={}, url=SEARCH_ADRES_URL):
        async_r = grequests.get(url, params=parameters, session=self.session)
        gevent.spawn(async_r.send).join()
        # Do something with the result count?

        if not async_r.response:
            log.error("No response")
            return {}
        elif async_r.response.status_code == 404:
            log.error(parameters)
            return {}

        result_json = async_r.response.json()
        return result_json

    def determine_verblijfsobject(self):
        parameters = {'q': self.query_string}
        data = self.get_response(parameters)
        corrected = False
        if 'results' in data:
            results = data['results']
            if len(results) > 0:
                m = re.match(
                    r'https://(?:acc.)?api.data.amsterdam.nl/bag/verblijfsobject/(\d+)/',
                    results[0]['_links']['self']['href'])
                if m:
                    verblijfsobject_id = m.group(1)
                    corrected = self.determine_verblijfsobject_pand(verblijfsobject_id)
        if corrected:
            STATS['correcties'] += 1
        else:
            STATS['onbekend'] += 1
            log.error("Missing result for {}".format(self.query_string))

    def determine_verblijfsobject_pand(self, verblijfsobject_id):
        parameters = {'verblijfsobjecten__id': verblijfsobject_id}
        data = self.get_response(parameters, url=SEARCH_PAND_URL)
        if 'results' in data:
            results = data['results']
            if len(results) > 0:
                pand = results[0]['landelijk_id']
                if pand is not None:
                    self.monument.betreft_pand = pand
                    self.monument.save()
                    return True
        return False


def make_status_line():
    status_line = 'All %s fixed: %s  ?: %s  fix/s %s  left: %s \r'
    complete_status_line = status_line % (
        STATS['total'],
        STATS['correcties'],
        STATS['onbekend'],
        STATS['fixs'],
        STATS['left']
    )
    return complete_status_line


def fix_counter():
    """
    Get an indication of the request per second
    """
    interval = 3.0
    while True:
        start = STATS['correcties']
        gevent.sleep(interval)
        diff = STATS['correcties'] - start + 0.001
        speed = (diff // interval) + 1
        STATS['fixs'] = '%.2f' % speed
        seconds_left = abs((STATS['total'] + 1) - STATS['correcties']) // speed
        STATS['left'] = datetime.timedelta(seconds=seconds_left)
        log.info(make_status_line())
