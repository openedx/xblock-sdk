"""Test that all scenarios render successfully."""
from django.test import TestCase, Client

import lxml.html
from nose_parameterized import parameterized

from xblock.core import XBlock


def get_links():
    response = Client().get("/")
    assert response.status_code == 200
    html = lxml.html.fromstring(response.content)
    a_tags = list(html.xpath('//a'))

    params = []
    for a_tag in a_tags:
        params.append((a_tag.text, a_tag.get('href')))

    return params


class ScenarioTests(TestCase):
    def test_all_scenarios(self):
        """Load the home page, get every URL, make a test from it."""
        link = get_links()

        # Load the scenarios from the classes.
        scenarios = []
        for _, cls in XBlock.load_classes():
            if hasattr(cls, "workbench_scenarios"):
                for _, xml in cls.workbench_scenarios():
                    scenarios.append(xml)

        # We should have an <a> tag for each scenario.
        self.assertEqual(len(link), len(scenarios))

        # We should have at least one scenario with a vertical tag, since we use
        # empty verticals as our canary in the coal mine that something has gone
        # horribly wrong with loading the scenarios.
        assert any("<vertical_demo>" in xml for xml in scenarios)

        # Since we are claiming in try_scenario that no vertical is empty, let's
        # eliminate the possibility that a scenario has an actual empty vertical.
        assert all("<vertical_demo></vertical_demo>" not in xml for xml in scenarios)
        assert all("<vertical_demo/>" not in xml for xml in scenarios)

    @parameterized.expand(get_links)
    def test_scenario(self, name, url):
        """Check that a scenario renders without error.

        `name`: the name of the scenario, used in error messages.
        `url`: the URL to the scenario to test.
        """
        # This is a very shallow test.  We don't know enough about each scenario to
        # know what each should do.  So we load the scenario to see that the
        # workbench could successfully serve it.
        response = self.client.get(url, follow=True)
        assert response.status_code == 200, name

        # Be sure we got the whole scenario.  Again, we can't know what to expect
        # here, but at the very least, if there are verticals, they should not be
        # empty.  That would be a sign that some data wasn't loaded properly while
        # rendering the scenario.
        html = lxml.html.fromstring(response.content)
        for vertical_tag in html.xpath('//div[@class="vertical"]'):
            # No vertical tag should be empty.
            assert list(vertical_tag), "Empty <vertical> shouldn't happen!"
