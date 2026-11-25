"""Test Workbench Runtime"""


from unittest import TestCase, mock

import pytest
from opaque_keys.edx.asides import AsideDefinitionKeyV2, AsideUsageKeyV2
from opaque_keys.edx.keys import DefinitionKey, UsageKey
from opaque_keys.edx.locator import BlockUsageLocator, CourseLocator, DefinitionLocator
from xblock.exceptions import NoSuchDefinition, NoSuchUsage
from xblock.fields import Scope
from xblock.reference.user_service import UserService
from xblock.runtime import KeyValueStore, KvsFieldData

from django.conf import settings

from ..models import XBlockState
from ..runtime import ScenarioIdManager, WorkbenchDjangoKeyValueStore, WorkbenchRuntime


class TestScenarioIds(TestCase):
    """
    Test XBlock Scenario IDs
    """

    def setUp(self):
        # Test basic ID generation meets our expectations
        super().setUp()
        self.id_mgr = ScenarioIdManager()

    def test_definitions_are_keys(self):
        definition_id = self.id_mgr.create_definition("my_block")
        self.assertIsInstance(definition_id, DefinitionLocator)
        self.assertEqual(definition_id.block_type, "my_block")
        self.assertEqual(self.id_mgr.get_block_type(definition_id), "my_block")
        self.assertEqual(DefinitionKey.from_string(str(definition_id)), definition_id)

    def test_no_scenario_loaded(self):
        definition_id = self.id_mgr.create_definition("my_block")
        self.assertEqual(self.id_mgr.get_scenario(definition_id), "default")

    def test_should_increment(self):
        first = self.id_mgr.create_definition("my_block")
        second = self.id_mgr.create_definition("my_block")
        self.assertNotEqual(first, second)
        self.assertEqual(self.id_mgr.create_usage(first).block_id, "d0.u0")
        self.assertEqual(self.id_mgr.create_usage(second).block_id, "d1.u0")

    def test_definitions_are_stable(self):
        # Reloading the scenarios must give the same ids, so stored content-scoped state is found again.
        other_id_mgr = ScenarioIdManager()
        for id_mgr in (self.id_mgr, other_id_mgr):
            id_mgr.set_scenario("my_scenario")
        first_definition = self.id_mgr.create_definition("my_block")
        self.assertEqual(first_definition, other_id_mgr.create_definition("my_block"))

        # Clearing the manager (as a state reset does) and reloading gives the same ids again.
        self.id_mgr.clear()
        self.id_mgr.set_scenario("my_scenario")
        self.assertEqual(self.id_mgr.create_definition("my_block"), first_definition)

    def test_slug_support(self):
        plain = self.id_mgr.create_definition("my_block")
        slugged = self.id_mgr.create_definition("my_block", "my_slug")
        self.assertNotEqual(plain, slugged)
        self.assertEqual(self.id_mgr.create_usage(slugged).block_id, "my_slug.d0.u0")

    def test_scenario_support(self):
        default_definition = self.id_mgr.create_definition("my_block")

        # Now that we have a scenario, our definition numbering starts over again,
        # but the ids don't collide with the ones from other scenarios.
        self.id_mgr.set_scenario("my_scenario")
        scenario_definition = self.id_mgr.create_definition("my_block")
        self.assertNotEqual(scenario_definition, default_definition)
        self.assertEqual(self.id_mgr.get_scenario(scenario_definition), "my_scenario")
        self.assertEqual(self.id_mgr.create_usage(scenario_definition).block_id, "d0.u0")

        self.id_mgr.set_scenario("another_scenario")
        another_definition = self.id_mgr.create_definition("my_block")
        self.assertNotIn(another_definition, (default_definition, scenario_definition))
        self.assertEqual(self.id_mgr.get_scenario(another_definition), "another_scenario")

    def test_unknown_definition_scenario(self):
        self.assertIsNone(self.id_mgr.get_scenario(DefinitionLocator("my_block", "0" * 24)))

    def test_usages(self):
        # Now make sure our usages are attached to definitions
        self.assertIsNone(self.id_mgr.last_created_usage_id())
        self.id_mgr.set_scenario("my_scenario")
        definition_id = self.id_mgr.create_definition("my_block")

        usage_id = self.id_mgr.create_usage(definition_id)
        self.assertIsInstance(usage_id, UsageKey)
        self.assertEqual(
            str(usage_id), "block-v1:workbench+my_scenario+run+type@my_block+block@d0.u0"
        )
        self.assertEqual(usage_id.block_type, "my_block")
        self.assertEqual(usage_id.course_key, CourseLocator("workbench", "my_scenario", "run"))
        self.assertEqual(self.id_mgr.get_definition_id(usage_id), definition_id)

        second_usage_id = self.id_mgr.create_usage(definition_id)
        self.assertEqual(
            str(second_usage_id), "block-v1:workbench+my_scenario+run+type@my_block+block@d0.u1"
        )
        self.assertEqual(self.id_mgr.last_created_usage_id(), second_usage_id)

    def test_usages_with_slug(self):
        definition_id = self.id_mgr.create_definition("my_block", "my_slug")
        self.assertEqual(
            str(self.id_mgr.create_usage(definition_id)),
            "block-v1:workbench+default+run+type@my_block+block@my_slug.d0.u0",
        )

    def test_usage_round_trips_through_string(self):
        # Handler URLs carry the serialized usage key, which must map back to the same usage.
        definition_id = self.id_mgr.create_definition("my_block")
        usage_id = self.id_mgr.create_usage(definition_id)
        parsed_usage_id = UsageKey.from_string(str(usage_id))
        self.assertEqual(self.id_mgr.get_definition_id(parsed_usage_id), definition_id)

    def test_usage_for_unknown_definition(self):
        with pytest.raises(NoSuchDefinition):
            self.id_mgr.create_usage(DefinitionLocator("my_block", "0" * 24))

    def test_unknown_usage(self):
        unknown_usage_id = BlockUsageLocator(
            CourseLocator("workbench", "my_scenario", "run"), "my_block", "d0.u0"
        )
        with pytest.raises(NoSuchUsage):
            self.id_mgr.get_definition_id(unknown_usage_id)

    def test_asides(self):
        definition_id = self.id_mgr.create_definition("my_block")
        usage_id = self.id_mgr.create_usage(definition_id)

        aside_definition, aside_usage = self.id_mgr.create_aside(
            definition_id, usage_id, "my_aside"
        )
        self.assertIsInstance(aside_definition, AsideDefinitionKeyV2)
        self.assertIsInstance(aside_usage, AsideUsageKeyV2)
        self.assertEqual(self.id_mgr.get_scenario(aside_definition), "default")
        self.assertEqual(
            UsageKey.from_string(str(aside_usage)), aside_usage
        )

        self.assertEqual(
            self.id_mgr.get_aside_type_from_definition(aside_definition), "my_aside"
        )
        self.assertEqual(
            self.id_mgr.get_definition_id_from_aside(aside_definition), definition_id
        )
        self.assertEqual(self.id_mgr.get_aside_type_from_usage(aside_usage), "my_aside")
        self.assertEqual(self.id_mgr.get_usage_id_from_aside(aside_usage), usage_id)


class WorkbenchRuntimeTests(TestCase):
    """
    Tests for the WorkbenchRuntime.
    """

    def test_lti_consumer_xblock_requirements(self):
        """
        The LTI Consumer XBlock expects a lot of values from the LMS Runtime,
        this test ensures that those requirements fulfilled.
        """
        runtime = WorkbenchRuntime("test_user")
        assert runtime.get_real_user(
            object()
        ), "The LTI Consumer XBlock needs this method."
        assert runtime.hostname, "The LTI Consumer XBlock needs this property."
        assert (
            runtime.anonymous_student_id
        ), "The LTI Consumer XBlock needs this property."


class TestKVStore(TestCase):
    """
    Test the Workbench KVP Store
    """

    def setUp(self):
        super().setUp()
        self.kvs = WorkbenchDjangoKeyValueStore()
        self.key = KeyValueStore.Key(
            scope=Scope.content,
            user_id="rusty",
            block_scope_id=DefinitionLocator("my_block", "0" * 24),
            field_name="age",
        )
        self.usage_id = BlockUsageLocator(
            CourseLocator("workbench", "my_scenario", "run"), "my_block", "d0.u0"
        )

    @pytest.mark.django_db
    def test_storage(self):
        self.assertFalse(self.kvs.has(self.key))
        self.kvs.set(self.key, 7)
        self.assertTrue(self.kvs.has(self.key))
        self.assertEqual(self.kvs.get(self.key), 7)
        self.kvs.delete(self.key)
        self.assertFalse(self.kvs.has(self.key))

    @pytest.mark.django_db
    def test_definition_key_storage(self):
        id_mgr = ScenarioIdManager()
        id_mgr.set_scenario("my_scenario")
        key = self.key._replace(block_scope_id=id_mgr.create_definition("my_block"))

        with mock.patch("workbench.runtime.ID_MANAGER", id_mgr):
            self.kvs.set(key, 7)
            self.assertEqual(self.kvs.get(key), 7)

        record = XBlockState.objects.get(scope="definition", user_id="rusty")
        self.assertEqual(record.scope_id, str(key.block_scope_id))
        self.assertEqual(record.scenario, "my_scenario")
        self.assertEqual(record.tag, "my_block")

    @pytest.mark.django_db
    def test_usage_key_storage(self):
        key = KeyValueStore.Key(
            scope=Scope.user_state,
            user_id="rusty",
            block_scope_id=self.usage_id,
            field_name="age",
        )
        self.kvs.set(key, 7)
        self.assertEqual(self.kvs.get(key), 7)

        record = XBlockState.objects.get(scope="usage", user_id="rusty")
        self.assertEqual(record.scope_id, str(self.usage_id))
        self.assertEqual(record.scenario, "my_scenario")
        self.assertEqual(record.tag, "my_block")

    @pytest.mark.django_db
    def test_aside_usage_key_storage(self):
        key = KeyValueStore.Key(
            scope=Scope.user_state,
            user_id="rusty",
            block_scope_id=AsideUsageKeyV2(self.usage_id, "my_aside"),
            field_name="age",
        )
        self.kvs.set(key, 7)
        self.assertEqual(self.kvs.get(key), 7)

        record = XBlockState.objects.get(scope="usage", user_id="rusty")
        self.assertEqual(record.scenario, "my_scenario")
        self.assertEqual(record.tag, "my_block")

    @pytest.mark.django_db
    def test_children_and_parent_storage(self):
        child_id = self.usage_id.replace(block_id="d1.u0")
        children_key = KeyValueStore.Key(
            scope=Scope.children, user_id=None, block_scope_id=self.usage_id, field_name="children",
        )
        parent_key = KeyValueStore.Key(
            scope=Scope.parent, user_id=None, block_scope_id=child_id, field_name="parent",
        )

        self.kvs.set(children_key, [child_id])
        self.kvs.set(parent_key, self.usage_id)

        self.assertEqual(self.kvs.get(children_key), [child_id])
        self.assertEqual(self.kvs.get(parent_key), self.usage_id)


class StubService:
    """Empty service to test loading additional services."""


class ExceptionService:
    """Stub service that raises an exception on init."""

    def __init__(self):
        raise Exception("Kaboom!")


class TestServices(TestCase):
    """
    Test XBlock runtime services
    """

    def setUp(self):
        super().setUp()
        self.xblock = mock.Mock()

    def test_default_services(self):
        runtime = WorkbenchRuntime("test_user")
        self._assert_default_services(runtime)

    @mock.patch.dict(
        settings.WORKBENCH["services"],
        {"stub": "workbench.test.test_runtime.StubService"},
    )
    def test_settings_adds_services(self):
        runtime = WorkbenchRuntime("test_user")

        # Default services should still be available
        self._assert_default_services(runtime)

        # An additional service should be provided
        self._assert_service(runtime, "stub", StubService)

        # Check that the service has the runtime attribute set
        service = runtime.service(self.xblock, "stub")
        self.assertIs(service.runtime, runtime)

    @mock.patch.dict(
        settings.WORKBENCH["services"],
        {"not_found": "workbench.test.test_runtime.NotFoundService"},
    )
    def test_could_not_find_service(self):
        runtime = WorkbenchRuntime("test_user")

        # Default services should still be available
        self._assert_default_services(runtime)

        # The additional service should NOT be available
        self.assertIs(runtime.service(self.xblock, "not_found"), None)

    @mock.patch.dict(
        settings.WORKBENCH["services"],
        {"exception": "workbench.test.test_runtime.ExceptionService"},
    )
    def test_runtime_service_initialization_failed(self):
        runtime = WorkbenchRuntime("test_user")

        # Default services should still be available
        self._assert_default_services(runtime)

        # The additional service should NOT be available
        self.assertIs(runtime.service(self.xblock, "exception"), None)

    def _assert_default_services(self, runtime):
        """Check that the default services are available."""
        self._assert_service(runtime, "field-data", KvsFieldData)
        self._assert_service(runtime, "user", UserService)

    def _assert_service(self, runtime, service_name, service_class):
        """Check that a service is loaded."""
        service_instance = runtime.service(self.xblock, service_name)
        self.assertIsInstance(service_instance, service_class)
