import mock
import unittest
from nose.tools import *  # noqa

import re
import requests
from bs4 import BeautifulSoup

from robobrowser.browser import RoboBrowser
from robobrowser import exceptions

from tests.fixtures import mock_links, mock_urls, mock_forms


class TestHeaders(unittest.TestCase):

    @mock_links
    def test_user_agent(self):
        browser = RoboBrowser(user_agent='freddie')
        browser.open('http://robobrowser.com/links/')
        assert_true('User-Agent' in browser.session.headers)
        assert_equal(
            browser.session.headers['User-Agent'], 'freddie'
        )

    def test_default_headers(self):
        browser = RoboBrowser()
        assert_equal(browser.session.headers, requests.Session().headers)


class TestOpen(unittest.TestCase):

    def setUp(self):
        self.browser = RoboBrowser()

    @mock.patch('requests.Session.request')
    def test_open_default_method(self, mock_request):
        url = 'http://robobrowser.com'
        self.browser.open(url)
        assert_true(mock_request.called)
        args = mock_request.mock_calls[0][1]
        assert_equal(args, ('get', url))

    @mock.patch('requests.Session.request')
    def test_open_custom_method(self, mock_request):
        url = 'http://robobrowser.com'
        self.browser.open(url, method='post')
        assert_true(mock_request.called)
        args = mock_request.mock_calls[0][1]
        assert_equal(args, ('post', url))


class TestLinks(unittest.TestCase):

    @mock_links
    def setUp(self):
        self.browser = RoboBrowser()
        self.browser.open('http://robobrowser.com/links/')

    @mock_links
    def test_get_link(self):
        link = self.browser.get_link()
        assert_equal(link.get('href'), '/link1/')

    @mock_links
    def test_get_links(self):
        links = self.browser.get_links()
        assert_equal(len(links), 3)

    @mock_links
    def test_follow_link_tag(self):
        link = self.browser.get_link(text=re.compile('sheer'))
        self.browser.follow_link(link)
        assert_equal(self.browser.url, 'http://robobrowser.com/link1/')

    @mock_links
    def test_follow_link_no_href(self):
        link = BeautifulSoup('<a>nohref</a>').find('a')
        assert_raises(
            exceptions.RoboError,
            lambda: self.browser.follow_link(link)
        )


class TestForms(unittest.TestCase):

    def setUp(self):
        self.browser = RoboBrowser()

    @mock_forms
    def test_get_forms(self):
        self.browser.open('http://robobrowser.com/get_form/')
        forms = self.browser.get_forms()
        assert_equal(len(forms), 2)

    @mock_forms
    def test_get_form_by_id(self):
        self.browser.open('http://robobrowser.com/get_form/')
        form = self.browser.get_form('bass')
        assert_equal(form.parsed.get('id'), 'bass')

    @mock_forms
    def test_submit_form_get(self):
        self.browser.open('http://robobrowser.com/get_form/')
        form = self.browser.get_form()
        self.browser.submit_form(form)
        assert_equal(
            self.browser.url,
            'http://robobrowser.com/get_form/?deacon=john'
        )
        assert_true(self.browser.state.response.request.body is None)

    @mock_forms
    def test_submit_form_multi_submit(self):
        self.browser.open('http://robobrowser.com/multi_submit_form/')
        form = self.browser.get_form()
        submit = form.submit_fields['submit2']
        self.browser.submit_form(form, submit=submit)
        assert_equal(
            self.browser.url,
            'http://robobrowser.com/multi_submit_form/'
            '?deacon=john&submit2=value2'
        )

    @mock_forms
    def test_submit_form_post(self):
        self.browser.open('http://robobrowser.com/post_form/')
        form = self.browser.get_form()
        self.browser.submit_form(form)
        assert_equal(
            self.browser.url,
            'http://robobrowser.com/submit/'
        )
        assert_equal(
            self.browser.state.response.request.body,
            'deacon=john'
        )


class TestFormsInputNoName(unittest.TestCase):

    @mock_forms
    def setUp(self):
        self.browser = RoboBrowser()
        self.browser.open('http://robobrowser.com/noname/')

    @mock_forms
    def test_get_forms(self):
        forms = self.browser.get_forms()
        assert_equal(len(forms), 1)


class TestHistoryInternals(unittest.TestCase):

    def setUp(self):
        self.browser = RoboBrowser(history=True)

    @mock_urls
    def test_open_appends_to_history(self):
        assert_equal(len(self.browser._states), 0)
        assert_equal(self.browser._cursor, -1)
        self.browser.open('http://robobrowser.com/page1/')
        assert_equal(len(self.browser._states), 1)
        assert_equal(self.browser._cursor, 0)

    @mock_forms
    def test_submit_appends_to_history(self):
        self.browser.open('http://robobrowser.com/get_form/')
        form = self.browser.get_form()
        self.browser.submit_form(form)

        assert_equal(len(self.browser._states), 2)
        assert_equal(self.browser._cursor, 1)

    @mock_urls
    def test_open_clears_history_after_back(self):
        self.browser.open('http://robobrowser.com/page1/')
        self.browser.open('http://robobrowser.com/page2/')
        self.browser.back()
        self.browser.open('http://robobrowser.com/page3/')
        assert_equal(len(self.browser._states), 2)
        assert_equal(self.browser._cursor, 1)

    @mock_urls
    def test_state_deque_max_length(self):
        browser = RoboBrowser(history=5)
        for _ in range(5):
            browser.open('http://robobrowser.com/page1/')
        assert_equal(len(browser._states), 5)
        browser.open('http://robobrowser.com/page2/')
        assert_equal(len(browser._states), 5)

    @mock_urls
    def test_state_deque_no_history(self):
        browser = RoboBrowser(history=False)
        for _ in range(5):
            browser.open('http://robobrowser.com/page1/')
            assert_equal(len(browser._states), 1)
            assert_equal(browser._cursor, 0)


class TestHistory(unittest.TestCase):

    @mock_urls
    def setUp(self):
        self.browser = RoboBrowser(history=True)
        self.browser.open('http://robobrowser.com/page1/')
        self.browser.open('http://robobrowser.com/page2/')
        self.browser.open('http://robobrowser.com/page3/')

    def test_back(self):
        self.browser.back()
        assert_equal(
            self.browser.url,
            'http://robobrowser.com/page2/'
        )

    def test_back_n(self):
        self.browser.back(n=2)
        assert_equal(
            self.browser.url,
            'http://robobrowser.com/page1/'
        )

    def test_forward(self):
        self.browser.back()
        self.browser.forward()
        assert_equal(
            self.browser.url,
            'http://robobrowser.com/page3/'
        )

    def test_forward_n(self):
        self.browser.back(n=2)
        self.browser.forward(n=2)
        assert_equal(
            self.browser.url,
            'http://robobrowser.com/page3/'
        )

    @mock_urls
    def test_open_clears_forward(self):
        self.browser.back(n=2)
        self.browser.open('http://robobrowser.com/page4/')
        assert_equal(
            self.browser._cursor,
            len(self.browser._states) - 1
        )
        assert_raises(
            exceptions.RoboError,
            self.browser.forward
        )

    def test_back_error(self):
        assert_raises(
            exceptions.RoboError,
            self.browser.back,
            5
        )


class TestCustomSession(unittest.TestCase):

    @mock_links
    def test_custom_headers(self):
        session = requests.Session()
        session.headers.update({
            'Content-Encoding': 'gzip',
        })
        browser = RoboBrowser(session=session)
        browser.open('http://robobrowser.com/links/')
        assert_equal(
            browser.response.request.headers.get('Content-Encoding'),
            'gzip'
        )

    @mock_links
    def test_custom_headers_override(self):
        session = requests.Session()
        session.headers.update({
            'Content-Encoding': 'gzip',
        })
        browser = RoboBrowser(session=session)
        browser.open(
            'http://robobrowser.com/links/',
            headers={'Content-Encoding': 'identity'}
        )
        assert_equal(
            browser.response.request.headers.get('Content-Encoding'),
            'identity'
        )


class TestTimeout(unittest.TestCase):

    @mock.patch('requests.Session.request')
    def test_no_timeout(self, mock_request):
        browser = RoboBrowser()
        browser.open('http://robobrowser.com/')
        assert_true(mock_request.called)
        kwargs = mock_request.mock_calls[0][2]
        assert_true(kwargs.get('timeout') is None)

    @mock.patch('requests.Session.request')
    def test_instance_timeout(self, mock_request):
        browser = RoboBrowser(timeout=5)
        browser.open('http://robobrowser.com/')
        assert_true(mock_request.called)
        kwargs = mock_request.mock_calls[0][2]
        assert_equal(kwargs.get('timeout'), 5)

    @mock.patch('requests.Session.request')
    def test_call_timeout(self, mock_request):
        browser = RoboBrowser(timeout=5)
        browser.open('http://robobrowser.com/', timeout=10)
        assert_true(mock_request.called)
        kwargs = mock_request.mock_calls[0][2]
        assert_equal(kwargs.get('timeout'), 10)


class TestAllowRedirects(unittest.TestCase):

    @mock.patch('requests.Session.request')
    def test_no_allow_redirects(self, mock_request):
        browser = RoboBrowser()
        browser.open('http://robobrowser.com/')
        assert_true(mock_request.called)
        kwargs = mock_request.mock_calls[0][2]
        assert_true(kwargs.get('allow_redirects') is True)

    @mock.patch('requests.Session.request')
    def test_instance_allow_redirects(self, mock_request):
        browser = RoboBrowser(allow_redirects=False)
        browser.open('http://robobrowser.com/')
        assert_true(mock_request.called)
        kwargs = mock_request.mock_calls[0][2]
        assert_true(kwargs.get('allow_redirects') is False)

    @mock.patch('requests.Session.request')
    def test_call_allow_redirects(self, mock_request):
        browser = RoboBrowser(allow_redirects=True)
        browser.open('http://robobrowser.com/', allow_redirects=False)
        assert_true(mock_request.called)
        kwargs = mock_request.mock_calls[0][2]
        assert_true(kwargs.get('allow_redirects') is False)
