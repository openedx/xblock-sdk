"""Tests for the thumbs module"""


import pytest
from bok_choy.promise import EmptyPromise

from workbench import scenarios
from workbench.test.selenium_test import SeleniumTest


class ThreeThumbsTest(SeleniumTest):
    """Test the functionalities of the three thumbs test XBlock."""

    def setUp(self):
        super().setUp()

        scenarios.add_xml_scenario(
            "test_three_file_thumbs", "three file thumbs test",
            """<vertical_demo><filethumbs/><filethumbs/><filethumbs/></vertical_demo>"""
        )
        self.addCleanup(scenarios.remove_scenario, "test_three_file_thumbs")

        # Suzy opens the browser to visit the workbench
        self.browser.get(self.live_server_url)

        # She knows it's the site by the header
        header1 = self.browser.find_element_by_css_selector('h1')
        self.assertEqual(header1.text, 'XBlock scenarios')

    @pytest.mark.flaky(reruns=5, reruns_delay=2)
    def test_three_thumbs_initial_state(self):
        # She clicks on the three thumbs at once scenario
        link = self.browser.find_element_by_link_text('three file thumbs test')
        link.click()
        self.wait_for_page_load(link, timeout=10)

        # The header reflects the XBlock
        header1 = self.browser.find_element_by_css_selector('h1')
        self.assertEqual(header1.text, 'XBlock: three file thumbs test')

        # She sees that there are 3 sets of thumbs
        vertical_css = 'div.student_view > div.xblock-v1 > div.vertical'

        # The following will give a NoSuchElementException error
        # if it is not there
        vertical = self.browser.find_element_by_css_selector(vertical_css)

        # Make sure there are three thumbs blocks
        thumb_css = 'div.xblock-v1[data-block-type="filethumbs"]'
        thumbs = vertical.find_elements_by_css_selector(thumb_css)
        self.assertEqual(3, len(thumbs))

        # Make sure they all have 0 for upvote and downvote counts
        up_count_css = 'span.upvote span.count'
        down_count_css = 'span.downvote span.count'

        for thumb in thumbs:
            # pylint: disable=cell-var-from-loop
            up_count = thumb.find_element_by_css_selector(up_count_css)
            down_count = thumb.find_element_by_css_selector(down_count_css)
            initial_up = int(up_count.text)
            initial_down = int(down_count.text)

            # upvote
            thumb.find_element_by_css_selector('span.upvote').click()
            _ = EmptyPromise(
                lambda: int(thumb.find_element_by_css_selector(up_count_css).text) == initial_up + 1,
                "upvote action succeeded"
            ).fulfill()
            self.assertEqual(initial_down, int(thumb.find_element_by_css_selector(down_count_css).text))

            # downvote
            thumb.find_element_by_css_selector('span.downvote').click()
            _ = EmptyPromise(
                lambda: int(thumb.find_element_by_css_selector(down_count_css).text) == initial_down + 1,
                "downvote action succeeded"
            ).fulfill()
            self.assertEqual(initial_up + 1, int(thumb.find_element_by_css_selector(up_count_css).text))
