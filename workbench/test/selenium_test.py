"""Helpers for Selenium tests."""

from django.test import LiveServerTestCase
from bok_choy.web_app_test import WebAppTest

from nose.plugins.attrib import attr

from workbench.runtime import reset_global_state


@attr('selenium')
class SeleniumTest(WebAppTest, LiveServerTestCase):
    """Base test class that provides setUpClass and tearDownClass
    methods necessary for selenium testing."""

    def setUp(self):
        super(SeleniumTest, self).setUp()

        # Clear the in-memory key value store, the usage store, and whatever
        # else needs to be cleared and re-initialized.
        reset_global_state()
