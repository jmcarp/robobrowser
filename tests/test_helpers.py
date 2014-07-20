import unittest
from nose.tools import *

from bs4 import BeautifulSoup

from robobrowser import helpers


class TestEnsureSoup(unittest.TestCase):
    
    def setUp(self):
        self.html = '<form></form>'
        self.tag = BeautifulSoup(self.html).find()
        self.htmls = [
            '<form></form>',
            '<input />',
        ]
        self.tags = [
            BeautifulSoup(html).find()
            for html in self.htmls
        ]

    def test_handle_string(self):
        ensured = helpers.ensure_soup(self.html)
        assert_equal(ensured, self.tag)
    
    def test_handle_soup(self):
        ensured = helpers.ensure_soup(BeautifulSoup(self.html))
        assert_equal(ensured, self.tag)

    def test_handle_tag(self):
        ensured = helpers.ensure_soup(BeautifulSoup(self.html).find())
        assert_equal(ensured, self.tag)

    def test_handle_string_list(self):
        ensured = helpers.ensure_soup(self.htmls)
        assert_equal(ensured, self.tags)

    def test_handle_soup_list(self):
        ensured = helpers.ensure_soup([
            BeautifulSoup(html)
            for html in self.htmls
        ])
        assert_equal(ensured, self.tags)

    def test_handle_tag_list(self):
        ensured = helpers.ensure_soup([
            BeautifulSoup(html).find()
            for html in self.htmls
        ])
        assert_equal(ensured, self.tags)

