"""The runtime machinery for the XBlock workbench.

Code in this file is a mix of Runtime layer and Workbench layer.

"""


import importlib
import itertools
import logging
from collections import defaultdict
from datetime import datetime, timedelta

from unittest.mock import Mock
from web_fragments.fragment import Fragment
from xblock.core import XBlockAside
from xblock.exceptions import NoSuchDefinition, NoSuchUsage
from xblock.reference.user_service import UserService, XBlockUser
from xblock.runtime import IdGenerator, IdReader, KeyValueStore, KvsFieldData, NoSuchViewError, NullI18nService, Runtime

import django.utils.translation
from django.conf import settings
from django.contrib.auth import get_user_model
from django.template import loader as django_template_loader
from django.templatetags.static import static
from django.urls import reverse

from .models import XBlockState
from .util import make_safe_for_html

try:
    import simplejson as json
except ImportError:
    import json

log = logging.getLogger(__name__)
User = get_user_model()


class WorkbenchDjangoKeyValueStore(KeyValueStore):
    """A Django model backed `KeyValueStore` for the Workbench to use.

    If you use this key-value store, you *must* use `ScenarioIdManager` or
    another ID Manager that uses the scope_id convention:

      {scenario-slug}.{block_type}.d{def #}(.u{usage #})

    So an example: a-little-html.html.d0.u0

    We store all fields for a given (scope, scope_id, user_id) in one JSON blob,
    rather than having a single row for each field name. This is why there's
    some JSON packing/unpacking code.
    """
    # Workbench-special methods.
    def clear(self):
        """Clear all data from the store."""
        XBlockState.objects.all().delete()

    def prep_for_scenario_loading(self):
        """Reset any state that's necessary before we load scenarios."""
        XBlockState.prep_for_scenario_loading()

    @staticmethod
    def _to_json_str(data):
        """
        Serialize data as a JSON string
        """
        return json.dumps(data, indent=2, sort_keys=True)

    # KeyValueStore methods.
    def get(self, key):
        """Get state for a given `KeyValueStore.Key`."""
        record = XBlockState.get_for_key(key)
        return json.loads(record.state)[key.field_name]

    def set(self, key, value):
        """Set state for a given `KeyValueStore.Key` to `value`."""
        record = XBlockState.get_for_key(key)
        state_dict = json.loads(record.state)
        state_dict[key.field_name] = value

        record.state = self._to_json_str(state_dict)
        record.save()

    def delete(self, key):
        """Delete state for a given `KeyValueStore.Key`."""
        record = XBlockState.get_for_key(key)
        state_dict = json.loads(record.state)
        del state_dict[key.field_name]
        record.state = self._to_json_str(state_dict)
        record.save()

    def has(self, key):
        """Check if an entry exists for `KeyValueStore.Key`."""
        record = XBlockState.get_for_key(key)
        state_dict = json.loads(record.state)
        return key.field_name in state_dict


class ScenarioIdManager(IdReader, IdGenerator):
    """A scenario-aware ID manager.

    This will create IDs in the form of::

      {scenario-slug}.{block_type}.d{def #}(.u{usage #})(.{aside_type})

    So an example: a-little-html.html.d0.u0

    The definition numbering is local to the scenario + block_type, and usage
    numbering is local to the definition_id. This is to help ensure that IDs
    shift around as little as possible when you add new content/scenarios.

    """
    def __init__(self):
        self._block_types_to_id_seq = defaultdict(itertools.count)
        self._def_ids_to_id_seq = defaultdict(itertools.count)
        self._usages = {}
        self._definitions = {}
        self._aside_defs = {}
        self._aside_usages = {}
        self.scenario = ""
        super().__init__()

    def clear(self):
        """Remove all entries."""
        self._block_types_to_id_seq.clear()
        self._def_ids_to_id_seq.clear()
        self._usages.clear()
        self._definitions.clear()
        self._aside_defs.clear()
        self._aside_usages.clear()
        self.scenario = ""

    def create_usage(self, def_id):
        """Make a usage, storing its definition id."""
        id_seq = self._def_ids_to_id_seq[def_id]
        usage_id = f"{def_id}.u{next(id_seq)}"
        self._usages[usage_id] = def_id

        return usage_id

    def get_definition_id(self, usage_id):
        """Get a definition_id by its usage id."""
        try:
            return self._usages[usage_id]
        except KeyError as ex:
            raise NoSuchUsage(repr(usage_id)) from ex

    def create_definition(self, block_type, slug=None):
        """Make a definition_id, storing its block type."""
        prefix = f"{self.scenario}.{block_type}"
        if slug:
            prefix += "." + slug

        id_seq = self._block_types_to_id_seq[prefix]
        def_id = f"{prefix}.d{next(id_seq)}"
        self._definitions[def_id] = block_type

        return def_id

    def get_block_type(self, def_id):
        """Get a block_type by its definition id."""
        try:
            return self._definitions[def_id]
        except KeyError as ex:
            raise NoSuchDefinition(repr(def_id)) from ex

    def create_aside(self, definition_id, usage_id, aside_type):
        """Create asides"""
        aside_def_id = f"{definition_id}.{aside_type}"
        aside_usage_id = f"{usage_id}.{aside_type}"
        self._aside_defs[aside_def_id] = (definition_id, aside_type)
        self._aside_usages[aside_usage_id] = (usage_id, aside_type)
        return aside_def_id, aside_usage_id

    def get_aside_type_from_definition(self, aside_id):
        """
        Parse the type of the aside from an XBlockAside definition_id.

        Arguments:
            aside_id: An XBlockAside definition_id.
        """
        try:
            return self._aside_defs[aside_id][1]
        except KeyError as ex:
            raise NoSuchDefinition(aside_id) from ex

    def get_aside_type_from_usage(self, aside_id):
        """
        Parse the type of the aside from an XBlockAside aside_id.

        Arguments:
            aside_id: An XBlockAside aside_id.
        """
        try:
            return self._aside_usages[aside_id][1]
        except KeyError as ex:
            raise NoSuchUsage(aside_id) from ex

    def get_usage_id_from_aside(self, aside_id):
        """
        Extract the usage_id from the aside_id.

        Arguments:
            aside_id: An XBlockAside usage_id
        """
        try:
            return self._aside_usages[aside_id][0]
        except KeyError as ex:
            raise NoSuchUsage(aside_id) from ex

    def get_definition_id_from_aside(self, aside_id):
        """
        Extract the definition_id from an aside id.

        Arguments:
            aside_id: An XBlockAside definition_id
        """
        try:
            return self._aside_defs[aside_id][0]
        except KeyError as ex:
            raise NoSuchDefinition(aside_id) from ex

    # Workbench specific functionality
    def set_scenario(self, scenario):
        """Call this before loading a scenario so that this `ScenarioIdManager`
        knows what to prefix the IDs with. This helps isolate scenarios from
        each other so that changes in one will not affect ID numbers in another.
        """
        self.scenario = scenario

    def last_created_usage_id(self):
        """Sometimes you create a usage for testing and just want to grab it
        back. This gives an easy hook to do that.
        """
        return sorted(self._usages.keys())[-1] if self._usages else None


class WorkbenchRuntime(Runtime):
    """
    Access to the workbench runtime environment for XBlocks.

    A pre-configured instance of this class will be available to XBlocks as
    `self.runtime`.
    """
    anonymous_student_id = 'dummydummy000-fake-fake-dummydummy00'  # Needed for the LTI XBlock
    hostname = '127.0.0.1:8000'  # Arbitrary value, needed for the LTI XBlock

    def __init__(self, user_id=None):
        #  TODO: Add params for user, runtime, etc. to service initialization
        #  Move to stevedor
        services = {
            'field-data': KvsFieldData(WORKBENCH_KVS),
            'user': WorkBenchUserService(user_id),
            'i18n': WorkbenchI18NService(),
        }

        # Load additional services defined by Django settings
        # This is useful for instances of workbench used to develop
        # XBlocks that require services that may be too specific
        # to include in the default workbench configuration.
        for service_name, service_path in (settings.WORKBENCH.get('services', {})).items():
            service = self._load_service(service_path)
            if service is not None:
                services[service_name] = service

        super().__init__(ID_MANAGER, services=services)
        self.id_generator = ID_MANAGER
        self.user_id = user_id

    def get_user_role(self):
        """Provide a dummy user role."""
        return 'Student'

    @property
    def descriptor_runtime(self):
        """Provide a dummy course."""
        course = Mock(
            lti_passports=['test:test:secret'],
            display_name_with_default='Test Course',
            display_org_with_default='edX',
        )

        return Mock(modulestore=Mock(
            get_course=Mock(return_value=course)
        ))

    def get_real_user(self, _):
        """
        Return a dummy user with a Mock profile.

        Expected by the LTI Consumer XBlock.
        """
        u = User()
        u.profile = Mock()
        u.profile.name = 'John Doe'
        return u

    def _patch_xblock(self, block):
        """Add required attributes by some legacy XBlocks such as the LTI Consumer XBlock."""
        try:
            block.location = Mock(html_id=Mock(return_value='course-v1:edX+Demo+2020'))
            block.course_id = block.location.html_id()
            block.due = datetime.utcnow()
            block.graceperiod = timedelta(seconds=0)
            block.category = 'chapter'
        except AttributeError:
            log.exception('Unable to patch xblock, Attributes are protected.')

    def handle(self, block, handler_name, request, suffix=''):
        """Patch the XBlock with required fields."""
        self._patch_xblock(block)
        return super().handle(block, handler_name, request, suffix)

    def render(self, block, view_name, context=None):
        """Renders using parent class render() method"""
        self._patch_xblock(block)
        try:
            return super().render(block, view_name, context)
        except NoSuchViewError:
            return Fragment("<i>No such view: %s on %s</i>"
                            % (view_name, make_safe_for_html(repr(block))))

    # TODO: [rocha] runtime should not provide this, each xblock
    # should use whatever they want
    def render_template(self, template_name, **kwargs):
        """Loads the django template for `template_name`"""
        template = django_template_loader.get_template(template_name)
        return template.render(kwargs)

    def _wrap_ele(self, block, view, frag, extra_data=None):
        """
        Add javascript to the wrapped element
        """
        wrapped = super()._wrap_ele(block, view, frag, extra_data)
        wrapped.add_resource_url(
            self.resource_url('js/vendor/jquery.min.js'),
            'application/javascript',
            placement='head',
        )
        wrapped.add_javascript_url(self.resource_url("js/vendor/jquery-migrate.min.js"))
        wrapped.add_javascript_url(self.resource_url("js/vendor/jquery.cookie.js"))

        if frag.js_init_fn:
            wrapped.add_javascript_url(self.resource_url("js/runtime/%s.js" % frag.js_init_version))

        return wrapped

    def handler_url(self, block, handler_name, suffix='', query='', thirdparty=False):
        """Helper to get the correct url for the given handler"""
        # Be sure this really is a handler.
        func = getattr(block, handler_name, None)
        if not func:
            raise ValueError(f"{handler_name!r} is not a function name")
        if not getattr(func, "_is_xblock_handler", False):
            raise ValueError(f"{handler_name!r} is not a handler name")

        if thirdparty:
            url_base = "unauth_handler"
        elif isinstance(block, XBlockAside):
            url_base = "aside_handler"
        else:
            url_base = "handler"
        url = reverse(
            url_base,
            args=(block.scope_ids.usage_id, handler_name, suffix)
        )

        has_query = False
        if not thirdparty:
            url += f"?student={block.scope_ids.user_id}"
            has_query = True
        if query:
            url += "&" if has_query else "?"
            url += query
        return url

    def resource_url(self, resource):
        """The url of the resource"""
        return static("workbench/" + resource)

    def local_resource_url(self, block, uri):
        """The url of the local resource"""
        return reverse("package_resource", args=(block.scope_ids.block_type, uri))

    def publish(self, block, event_type, event_data):
        """Mocks a publish event by logging args"""
        log.info(
            "XBlock event %s for %s (usage_id=%s):",
            event_type,
            block.scope_ids.block_type,
            block.scope_ids.usage_id
        )
        log.info(event_data)

    def query(self, block):
        """Return a BlockSet query on block"""
        return _BlockSet(self, [block])

    def _load_service(self, service_path):  # pylint: disable=inconsistent-return-statements
        """Load and and initialize a service instance.

        `service_path` is a Python module path of the form
        "package.subpackage.module.class", where `class`
        is the class defining the service.

        Returns an instance of the service, or `None` if the
        service could not be initialized.
        """
        module_path, _, name = service_path.rpartition('.')
        try:
            cls = getattr(importlib.import_module(module_path), name)
            service_instance = cls()
            service_instance.runtime = self
            return service_instance
        except (ImportError, ValueError, AttributeError):
            log.info('Could not find service class defined at "%s"', service_path)
        except:  # pylint: disable=bare-except
            log.exception('Could not initialize service defined at "%s"', service_path)


class _BlockSet:
    """
    Provide a collection of blocks
    """
    def __init__(self, runtime, blocks):
        self.runtime = runtime
        self.blocks = blocks

    def __iter__(self):
        """
        Iterate over all blocks
        """
        return iter(self.blocks)

    def parent(self):
        """
        Create a `BlockSet` of all blocks' parents
        """
        them = set()
        for block in self.blocks:
            if block.parent:
                parent = self.runtime.get_block(block.parent)
                them.add(parent)
        return _BlockSet(self.runtime, them)

    def children(self):
        """
        Create a `BlockSet` of all blocks' children
        """
        them = set()
        for block in self.blocks:
            for child_id in getattr(block, "children", ()):
                child = self.runtime.get_block(child_id)
                them.add(child)
        return _BlockSet(self.runtime, them)

    def descendants(self):
        """
        Create a `BlockSet` of all blocks and their children
        """
        them = set()

        def recur(block):
            """
            Descend into block children, recursively
            """
            for child_id in getattr(block, "children", ()):
                child = self.runtime.get_block(child_id)
                them.add(child)
                recur(child)

        for block in self.blocks:
            recur(block)

        return _BlockSet(self.runtime, them)

    def tagged(self, tag):
        """
        Create a `BlockSet` of all blocks matching the corresponding tag
        """
        # Allow this method to access _class_tags for each block
        # pylint: disable=W0212
        them = set()
        for block in self.blocks:
            if block.name == tag:
                them.add(block)
            if block.tags and tag in block.tags:
                them.add(block)
            elif tag in block._class_tags:
                them.add(block)
        return _BlockSet(self.runtime, them)

    def attr(self, attr_name):
        """
        Yield attributes from child blocks
        """
        for block in self.blocks:
            if hasattr(block, attr_name):
                yield getattr(block, attr_name)


# Our global state (the "database").
WORKBENCH_KVS = WorkbenchDjangoKeyValueStore()

# Our global id manager
ID_MANAGER = ScenarioIdManager()


class WorkBenchUserService(UserService):
    """
    An implementation of xblock.reference.user_service.UserService
    """

    def __init__(self, uid):
        """
        Initialize user
        """
        user = XBlockUser(
            is_current_user=True,
            emails=["user@example.com"],
            full_name=f"XBlock User ({uid})",
        )
        user.opt_attrs['xblock-workbench.user_id'] = uid
        super().__init__(user=user)

    def get_current_user(self):
        """
        Returns user created by init
        """
        return self._user


class WorkbenchI18NService(NullI18nService):
    """Version of the I18N service for the workbench.

    Like the version in edx-platform, this simply
    exposes functions defined in Django's translation
    module.
    """

    def __getattr__(self, name):
        return getattr(django.utils.translation, name)
