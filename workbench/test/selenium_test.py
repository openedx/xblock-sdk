"""
Helpers for Selenium tests.
"""



import pytest
from bok_choy.web_app_test import WebAppTest
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.support.ui import WebDriverWait

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from workbench.runtime_util import reset_global_state


@pytest.mark.selenium
class SeleniumTest(WebAppTest, StaticLiveServerTestCase):
    """
    Base test class that provides setUpClass and tearDownClass
    methods necessary for selenium testing.
    """

    def setUp(self):
        super().setUp()

        # Clear the in-memory key value store, the usage store, and whatever
        # else needs to be cleared and re-initialized.
        reset_global_state()

    def wait_for_page_load(self, old_element, timeout=30):
        """
        Uses Selenium's built-in "staleness" hook to wait until the page has
        loaded. For use when clicking a link to ensure that the new page
        has loaded before selecting elements. I think that this could be used
        to check that elements have been made stale via ajax as well, but it
        is not being used for that in any of the tests here.
        """
        return WebDriverWait(self.browser, timeout).until(staleness_of(old_element))
