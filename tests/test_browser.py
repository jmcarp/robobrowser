import mock
import unittest
from nose.tools import *

import re
import requests

from robobrowser.browser import RoboBrowser
from robobrowser import exceptions

from tests.fixtures import mock_links, mock_urls, mock_forms


class TestHeaders(unittest.TestCase):

    @mock_links
    def test_headers(self):
        headers = {
            'X-Song': 'Innuendo',
            'X-Writer': 'Freddie',
        }
        browser = RoboBrowser(headers=headers)
        browser.open('http://robobrowser.com/links/')
        for key, value in headers.items():
            assert_equal(browser.session.headers[key], value)

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
    def test_get_link_by_text(self):
        link = self.browser.get_link('opera')
        assert_equal(link.get('href'), '/link2/')

    @mock_links
    def test_follow_link_tag(self):
        link = self.browser.get_link(text=re.compile('sheer'))
        self.browser.follow_link(link)
        assert_equal(self.browser.url, 'http://robobrowser.com/link1/')

    @mock_links
    def test_follow_link_text(self):
        self.browser.follow_link('heart attack')
        assert_equal(self.browser.url, 'http://robobrowser.com/link1/')

    @mock_links
    def test_follow_link_regex(self):
        self.browser.follow_link(re.compile(r'opera'))
        assert_equal(self.browser.url, 'http://robobrowser.com/link2/')

    @mock_links
    def test_follow_link_bs_args(self):
        self.browser.follow_link(class_=re.compile(r'song'))
        assert_equal(self.browser.url, 'http://robobrowser.com/link2/')

    @mock_links
    def test_follow_link_no_href(self):
        assert_raises(
            exceptions.RoboError,
            lambda: self.browser.follow_link(class_=re.compile(r'nohref'))
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


class TestTimeout(unittest.TestCase):

    @mock.patch('requests.Session.get')
    def test_no_timeout(self, mock_get):
        browser = RoboBrowser()
        browser.open('http://robobrowser.com/')
        mock_get.assert_called_once_with(
            'http://robobrowser.com/', timeout=None, verify=True
        )

    @mock.patch('requests.Session.get')
    def test_instance_timeout(self, mock_get):
        browser = RoboBrowser(timeout=5)
        browser.open('http://robobrowser.com/')
        mock_get.assert_called_once_with(
            'http://robobrowser.com/', timeout=5, verify=True
        )

    @mock.patch('requests.Session.get')
    def test_call_timeout(self, mock_get):
        browser = RoboBrowser(timeout=5)
        browser.open('http://robobrowser.com/', timeout=10)
        mock_get.assert_called_once_with(
            'http://robobrowser.com/', timeout=10, verify=True
        )


class TestVerify(unittest.TestCase):

    @mock.patch('requests.Session.get')
    def test_no_verify(self, mock_get):
        browser = RoboBrowser()
        browser.open('http://robobrowser.com/')
        mock_get.assert_called_once_with(
            'http://robobrowser.com/', verify=True, timeout=None
        )

    @mock.patch('requests.Session.get')
    def test_instance_verify(self, mock_get):
        browser = RoboBrowser(verify=True)
        browser.open('http://robobrowser.com/')
        mock_get.assert_called_once_with(
            'http://robobrowser.com/', verify=True, timeout=None
        )

    @mock.patch('requests.Session.get')
    def test_call_verify(self, mock_get):
        browser = RoboBrowser(verify=True)
        browser.open('http://robobrowser.com/', verify=False)
        mock_get.assert_called_once_with(
            'http://robobrowser.com/', verify=False, timeout=None
        )
