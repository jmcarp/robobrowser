import mock
import unittest
from nose.tools import *

import re
import requests
import functools

from robobrowser import responses
from robobrowser.browser import RoboBrowser
from robobrowser.browser import RoboError
from tests.utils import ArgCatcher


def mock_responses(resps):
    """Decorator factory to make tests more DRY. Bundles responses.activate
    with a collection of response rules.

    :param list resps: List of response-formatted ArgCatcher arguments.

    """
    def wrapper(func):
        @responses.activate
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            for resp in resps:
                responses.add(*resp.args, **resp.kwargs)
            return func(*args, **kwargs)
        return wrapped
    return wrapper

mock_links = mock_responses(
    [
        ArgCatcher(
            responses.GET, 'http://robobrowser.com/links/',
            body=b'''
                <a href="/link1/">sheer heart attack</a>
                <a href="/link2/" class="song">night at the opera</a>
            '''
        ),
        ArgCatcher(responses.GET, 'http://robobrowser.com/link1/'),
        ArgCatcher(responses.GET, 'http://robobrowser.com/link2/'),
    ]
)

mock_forms = mock_responses(
    [
        ArgCatcher(
            responses.GET, 'http://robobrowser.com/get_form/',
            body=b'''
                <form id="bass" method="get" action="/get_form/">'
                    <input name="deacon" value="john" />
                </form>
                <form id="drums" method="post" action="/get_form/">'
                    <input name="deacon" value="john" />
                </form>
            '''
        ),
        ArgCatcher(
            responses.GET, 'http://robobrowser.com/post_form/',
            body=b'''
                <form id="bass" method="post" action="/submit/">'
                    <input name="deacon" value="john" />
                </form>
                <form id="drums" method="post" action="/submit/">'
                    <input name="deacon" value="john" />
                </form>
            '''
        ),
        ArgCatcher(
            responses.GET, 'http://robobrowser.com/noname/',
            body=b'''
                <form name="input" action="action" method="get">
                <input type="checkbox" name="vehicle" value="Bike">
                    I have a bike<br>
                <input type="checkbox" name="vehicle" value="Car">I have a car
                <br><br>
                <input type="submit" value="Submit">
                </form>
            '''
        ),
        ArgCatcher(
            responses.POST, 'http://robobrowser.com/submit/',
        ),
    ]
)

mock_urls = mock_responses(
    [
        ArgCatcher(responses.GET, 'http://robobrowser.com/page1/'),
        ArgCatcher(responses.GET, 'http://robobrowser.com/page2/'),
        ArgCatcher(responses.GET, 'http://robobrowser.com/page3/'),
        ArgCatcher(responses.GET, 'http://robobrowser.com/page4/'),
    ]
)


class TestHeaders(unittest.TestCase):

    def test_headers(self):
        headers = {
            'X-Song': 'Innuendo',
            'X-Writer': 'Freddie',
        }
        browser = RoboBrowser(headers=headers)
        browser.open('http://robobrowser.com/links/')
        for key, value in headers.items():
            assert_equal(browser.session.headers[key], value)

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
        assert_equal(len(links), 2)

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
            RoboError,
            self.browser.forward
        )

    def test_back_error(self):
        assert_raises(
            RoboError,
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
