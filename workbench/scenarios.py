"""Example scenarios to display in the workbench.

This code is in the Workbench layer.

"""
from collections import namedtuple

from django.conf import settings
from django.template.defaultfilters import slugify

from xblock.core import XBlock
from .runtime import WorkbenchRuntime, WORKBENCH_KVS

# Build the scenarios, which are named trees of usages.

Scenario = namedtuple("Scenario", "description usage_id xml")  # pylint: disable=C0103

SCENARIOS = {}


def add_xml_scenario(scname, description, xml):
    """
    Add a scenario defined in XML.
    """
    assert scname not in SCENARIOS, "Already have a %r scenario" % scname
    runtime = WorkbenchRuntime()

    # WorkbenchRuntime has an id_generator, but most runtimes won't
    # (because the generator will be contextual), so we
    # pass it explicitly to parse_xml_string.
    runtime.id_generator.set_scenario(slugify(description))
    usage_id = runtime.parse_xml_string(xml, runtime.id_generator)
    SCENARIOS[scname] = Scenario(description, usage_id, xml)


def remove_scenario(scname):
    """
    Remove a named scenario from the global list.
    """
    del SCENARIOS[scname]


def add_class_scenarios(class_name, cls):
    """
    Add scenarios from a class to the global collection of scenarios.
    """
    # Each XBlock class can provide scenarios to display in the workbench.
    if hasattr(cls, "workbench_scenarios"):
        for i, (desc, xml) in enumerate(cls.workbench_scenarios()):
            scname = "%s.%d" % (class_name, i)
            add_xml_scenario(scname, desc, xml)

def init_scenarios():
    """
    Create all the scenarios declared in all the XBlock classes.
    """
    wb_config = settings.WORKBENCH if hasattr(settings, "WORKBENCH") else {}

    # Clear any existing scenarios, since this is used repeatedly during testing.
    SCENARIOS.clear()
    if wb_config.get('reset_state_on_restart'):
        WORKBENCH_KVS.clear()
    else:
        WORKBENCH_KVS.prep_for_scenario_loading()

    # All the tag names we want to load scenarios for
    scenarios_to_load = frozenset(wb_config.get('SCENARIOS', []))

    # Get installed XBlock classes, and add their scenarios. By default, we'll
    # load all scenarios for all XBlock tags. That being said, if you're
    # embedding the workbench into a project for development purposes, you may
    # not care about the built-in examples or other random XBlocks installed on
    # your system. In that case, we allow you to specify a list of tags that
    # will get loaded in settings.WORKBENCH['SCENARIOS'].
    for tag_name, cls in sorted(XBlock.load_classes()):
        # If config says we should load this scenario, or no scenario config exists
        if (tag_name in scenarios_to_load) or (not scenarios_to_load):
            add_class_scenarios(tag_name, cls)
