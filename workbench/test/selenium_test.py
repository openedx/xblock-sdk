"""Helpers for Selenium tests."""

from bok_choy.browser import browser
from bok_choy.web_app_test import WebAppTest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from nose.plugins.attrib import attr
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.support.ui import WebDriverWait

from workbench.runtime_util import reset_global_state


@attr('selenium')
class SeleniumTest(WebAppTest, StaticLiveServerTestCase):
    """Base test class that provides setUpClass and tearDownClass
    methods necessary for selenium testing."""

    def setUp(self):
        # super(SeleniumTest, self).setUp()
        super(WebAppTest, self).setUp()

        # Set up the browser
        # This will start the browser
        # If using SauceLabs, tag the job with test info
        tags = [self.id()]
        self.browser = browser(tags, self.proxy)

        # Needle uses these attributes for taking the screenshots
        self.driver = self.get_web_driver()
        # self.driver.set_window_position(0, 0)
        # self.set_viewport_size(self.viewport_width, self.viewport_height)

        # Cleanups are executed in LIFO order.
        # This ensures that the screenshot is taken and the driver logs are saved
        # BEFORE the browser quits.
        self.addCleanup(self.quit_browser)
        self.addCleanup(self._save_artifacts)

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
