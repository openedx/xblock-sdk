"""Test Workbench Runtime"""



from unittest import TestCase

from unittest import mock
import pytest
from xblock.fields import Scope
from xblock.reference.user_service import UserService
from xblock.runtime import KeyValueStore, KvsFieldData

from django.conf import settings

from ..runtime import ScenarioIdManager, WorkbenchDjangoKeyValueStore, WorkbenchRuntime


class TestScenarioIds(TestCase):
    """
    Test XBlock Scenario IDs
    """

    def setUp(self):
        # Test basic ID generation meets our expectations
        super().setUp()
        self.id_mgr = ScenarioIdManager()

    def test_no_scenario_loaded(self):
        self.assertEqual(self.id_mgr.create_definition("my_block"), ".my_block.d0")

    def test_should_increment(self):
        self.assertEqual(self.id_mgr.create_definition("my_block"), ".my_block.d0")
        self.assertEqual(self.id_mgr.create_definition("my_block"), ".my_block.d1")

    def test_slug_support(self):
        self.assertEqual(
            self.id_mgr.create_definition("my_block", "my_slug"),
            ".my_block.my_slug.d0"
        )
        self.assertEqual(
            self.id_mgr.create_definition("my_block", "my_slug"),
            ".my_block.my_slug.d1"
        )

    def test_scenario_support(self):
        self.test_should_increment()

        # Now that we have a scenario, our definition numbering starts over again.
        self.id_mgr.set_scenario("my_scenario")
        self.assertEqual(self.id_mgr.create_definition("my_block"), "my_scenario.my_block.d0")
        self.assertEqual(self.id_mgr.create_definition("my_block"), "my_scenario.my_block.d1")

        self.id_mgr.set_scenario("another_scenario")
        self.assertEqual(self.id_mgr.create_definition("my_block"), "another_scenario.my_block.d0")

    def test_usages(self):
        # Now make sure our usages are attached to definitions
        self.assertIsNone(self.id_mgr.last_created_usage_id())
        self.assertEqual(
            self.id_mgr.create_usage("my_scenario.my_block.d0"),
            "my_scenario.my_block.d0.u0"
        )
        self.assertEqual(
            self.id_mgr.create_usage("my_scenario.my_block.d0"),
            "my_scenario.my_block.d0.u1"
        )
        self.assertEqual(self.id_mgr.last_created_usage_id(), "my_scenario.my_block.d0.u1")

    def test_asides(self):
        definition_id = self.id_mgr.create_definition('my_block')
        usage_id = self.id_mgr.create_usage(definition_id)

        aside_definition, aside_usage = self.id_mgr.create_aside(definition_id, usage_id, 'my_aside')

        self.assertEqual(self.id_mgr.get_aside_type_from_definition(aside_definition), 'my_aside')
        self.assertEqual(self.id_mgr.get_definition_id_from_aside(aside_definition), definition_id)
        self.assertEqual(self.id_mgr.get_aside_type_from_usage(aside_usage), 'my_aside')
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
        runtime = WorkbenchRuntime('test_user')
        assert runtime.get_real_user(object()), 'The LTI Consumer XBlock needs this method.'
        assert runtime.hostname, 'The LTI Consumer XBlock needs this property.'
        assert runtime.anonymous_student_id, 'The LTI Consumer XBlock needs this property.'


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
            block_scope_id="my_scenario.my_block.d0",
            field_name="age"
        )

    @pytest.mark.django_db
    def test_storage(self):
        self.assertFalse(self.kvs.has(self.key))
        self.kvs.set(self.key, 7)
        self.assertTrue(self.kvs.has(self.key))
        self.assertEqual(self.kvs.get(self.key), 7)
        self.kvs.delete(self.key)
        self.assertFalse(self.kvs.has(self.key))


class StubService:
    """Empty service to test loading additional services. """


class ExceptionService:
    """Stub service that raises an exception on init. """
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
        runtime = WorkbenchRuntime('test_user')
        self._assert_default_services(runtime)

    @mock.patch.dict(settings.WORKBENCH['services'], {
        'stub': 'workbench.test.test_runtime.StubService'
    })
    def test_settings_adds_services(self):
        runtime = WorkbenchRuntime('test_user')

        # Default services should still be available
        self._assert_default_services(runtime)

        # An additional service should be provided
        self._assert_service(runtime, 'stub', StubService)

        # Check that the service has the runtime attribute set
        service = runtime.service(self.xblock, 'stub')
        self.assertIs(service.runtime, runtime)

    @mock.patch.dict(settings.WORKBENCH['services'], {
        'not_found': 'workbench.test.test_runtime.NotFoundService'
    })
    def test_could_not_find_service(self):
        runtime = WorkbenchRuntime('test_user')

        # Default services should still be available
        self._assert_default_services(runtime)

        # The additional service should NOT be available
        self.assertIs(runtime.service(self.xblock, 'not_found'), None)

    @mock.patch.dict(settings.WORKBENCH['services'], {
        'exception': 'workbench.test.test_runtime.ExceptionService'
    })
    def test_runtime_service_initialization_failed(self):
        runtime = WorkbenchRuntime('test_user')

        # Default services should still be available
        self._assert_default_services(runtime)

        # The additional service should NOT be available
        self.assertIs(runtime.service(self.xblock, 'exception'), None)

    def _assert_default_services(self, runtime):
        """Check that the default services are available. """
        self._assert_service(runtime, 'field-data', KvsFieldData)
        self._assert_service(runtime, 'user', UserService)

    def _assert_service(self, runtime, service_name, service_class):
        """Check that a service is loaded. """
        service_instance = runtime.service(self.xblock, service_name)
        self.assertIsInstance(service_instance, service_class)
