"""Example scenarios to display in the workbench.

This code is in the Workbench layer.

"""


import logging
from collections import namedtuple

from xblock.core import XBlock

from django.conf import settings
from django.template.defaultfilters import slugify

from .runtime import WORKBENCH_KVS, WorkbenchRuntime

log = logging.getLogger(__name__)

# Build the scenarios, which are named trees of usages.

Scenario = namedtuple("Scenario", "description usage_id xml")

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


def add_class_scenarios(class_name, cls, fail_silently=True):
    """
    Add scenarios from a class to the global collection of scenarios.
    """
    # Each XBlock class can provide scenarios to display in the workbench.
    if hasattr(cls, "workbench_scenarios"):
        for i, (desc, xml) in enumerate(cls.workbench_scenarios()):
            scname = "%s.%d" % (class_name, i)
            try:
                add_xml_scenario(scname, desc, xml)
            except Exception:  # pylint:disable=broad-except
                # don't allow a single bad scenario to block the whole workbench
                if fail_silently:
                    log.warning("Cannot load %s", desc, exc_info=True)
                else:
                    raise


def init_scenarios():
    """
    Create all the scenarios declared in all the XBlock classes.
    """
    # Clear any existing scenarios, since this is used repeatedly during testing.
    SCENARIOS.clear()
    if settings.WORKBENCH['reset_state_on_restart']:
        WORKBENCH_KVS.clear()
    else:
        WORKBENCH_KVS.prep_for_scenario_loading()

    # Get all the XBlock classes, and add their scenarios.
    for class_name, cls in sorted(XBlock.load_classes(fail_silently=False)):
        add_class_scenarios(class_name, cls, fail_silently=False)


def get_scenarios():
    """
    Return SCENARIOS, initializing it if required.
    """
    if not SCENARIOS and not get_scenarios.initialized:
        init_scenarios()
        get_scenarios.initialized = True
    return SCENARIOS


get_scenarios.initialized = False
