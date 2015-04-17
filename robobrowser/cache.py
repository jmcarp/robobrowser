"""
Caching utilities for robotic browsers. Credit to
https://github.com/Lukasa/httpcache
"""

import logging
import datetime
from requests.adapters import HTTPAdapter

from robobrowser.compat import OrderedDict, iteritems

logger = logging.getLogger(__name__)

# Modified from https://github.com/Lukasa/httpcache/blob/master/httpcache/cache.py
# RoboBrowser should only cache GET requests; HEAD and OPTIONS not exposed
CACHE_VERBS = ['GET']
CACHE_CODES = [200, 203, 300, 301, 410]

class RoboCache(object):

    def __init__(self, max_age=None, max_count=None):
        self.data = OrderedDict()
        self.max_age = max_age
        self.max_count = max_count

    def _reduce_age(self, now):
        """Reduce size of cache by date.

        :param datetime.datetime now: Current time

        """
        if self.max_age:
            keys = [
                key for key, value in iteritems(self.data)
                if now - value['date'] > self.max_age
            ]
            for key in keys:
                del self.data[key]

    def _reduce_count(self):
        """Reduce size of cache by count.

        """
        if self.max_count:
            while len(self.data) > self.max_count:
                self.data.popitem(last=False)

    def store(self, response):
        """Store response in cache, skipping if code is forbidden.

        :param requests.Response response: HTTP response

        """
        if response.status_code not in CACHE_CODES:
            return
        now = datetime.datetime.now()
        self.data[response.url] = {
            'date': now,
            'response': response,
        }
        logger.info('Stored response in cache')
        self._reduce_age(now)
        self._reduce_count()

    def retrieve(self, request):
        """Look up request in cache, skipping if verb is forbidden.

        :param requests.Request request: HTTP request

        """
        if request.method not in CACHE_VERBS:
            return
        try:
            response = self.data[request.url]['response']
            logger.info('Retrieved response from cache')
            return response
        except KeyError:
            return None

    def clear(self):
        "Clear cache."
        self.data = OrderedDict()

class RoboHTTPAdapter(HTTPAdapter):

    def __init__(self, max_age=None, max_count=None, **kwargs):
        super(RoboHTTPAdapter, self).__init__(**kwargs)
        self.cache = RoboCache(max_age=max_age, max_count=max_count)

    def send(self, request, **kwargs):
        cached_resp = self.cache.retrieve(request)
        if cached_resp is not None:
            return cached_resp
        else:
            return super(RoboHTTPAdapter, self).send(request, **kwargs)

    def build_response(self, request, response):
        resp = super(RoboHTTPAdapter, self).build_response(request, response)
        self.cache.store(resp)
        return resp
