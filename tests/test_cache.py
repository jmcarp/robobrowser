import unittest
from nose.tools import *

import datetime

from robobrowser.browser import RoboBrowser
from robobrowser.cache import RoboCache
from tests.utils import KwargSetter


class TestAdapter(unittest.TestCase):

    def test_cache_on(self):
        self.browser = RoboBrowser(cache=True)
        self.browser.open('http://httpbin.org/')
        resp1 = self.browser.state.response
        self.browser.open('http://httpbin.org/')
        resp2 = self.browser.state.response
        assert_true(resp1 is resp2)

    def test_cache_off(self):
        self.browser = RoboBrowser(cache=False)
        self.browser.open('http://httpbin.org/')
        resp1 = self.browser.state.response
        self.browser.open('http://httpbin.org/')
        resp2 = self.browser.state.response
        assert_true(resp1 is not resp2)


class TestCache(unittest.TestCase):

    def setUp(self):
        self.cache = RoboCache()

    def test_store(self):
        url = 'http://robobrowser.com/'
        response = KwargSetter(url=url, status_code=200)
        now = datetime.datetime.now()
        self.cache.store(response)
        assert_true(url in self.cache.data)
        assert_equal(self.cache.data[url]['response'], response)
        date_diff = self.cache.data[url]['date'] - now
        assert_true(date_diff < datetime.timedelta(seconds=0.1))

    def test_store_invalid_verb(self):
        url = 'http://robobrowser.com/'
        response = KwargSetter(url=url, status_code=400)
        self.cache.store(response)
        assert_false(url in self.cache.data)

    def test_retrieve_not_stored(self):
        request = KwargSetter(url='http://robobrowser.com/', method='GET')
        retrieved = self.cache.retrieve(request)
        assert_equal(retrieved, None)

    def test_retrieve_stored(self):
        request = KwargSetter(url='http://robobrowser.com/', method='GET')
        response = KwargSetter(url='http://robobrowser.com/', status_code=200)
        self.cache.store(response)
        retrieved = self.cache.retrieve(request)
        assert_equal(retrieved, response)

    def test_retrieve_invalid_code(self):
        request = KwargSetter(url='http://robobrowser.com/', method='GET')
        response = KwargSetter(url='http://robobrowser.com/', status_code=400)
        self.cache.store(response)
        retrieved = self.cache.retrieve(request)
        assert_equal(retrieved, None)

    def test_reduce_age(self):
        for idx in range(5):
            response = KwargSetter(url=idx, status_code=200)
            self.cache.store(response)
            # time.sleep(0.1)
        assert_equal(len(self.cache.data), 5)
        now = datetime.datetime.now()
        self.cache.max_age = now - self.cache.data[2]['date']
        self.cache._reduce_age(now)
        assert_equal(len(self.cache.data), 3)
        # Cast keys to list for 3.3 compatibility
        assert_equal(list(self.cache.data.keys()), [2, 3, 4])

    def test_reduce_count(self):
        for idx in range(5):
            response = KwargSetter(url=idx, status_code=200)
            self.cache.store(response)
        assert_equal(len(self.cache.data), 5)
        self.cache.max_count = 3
        self.cache._reduce_count()
        assert_equal(len(self.cache.data), 3)
        # Cast keys to list for 3.3 compatibility
        assert_equal(list(self.cache.data.keys()), [2, 3, 4])
