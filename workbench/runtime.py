"""The runtime machinery for the XBlock workbench.

Code in this file is a mix of Runtime layer and Workbench layer.

"""
from collections import defaultdict, OrderedDict
import itertools
import logging

try:
    import simplejson as json
except ImportError:
    import json

from django.conf import settings
from django.core.urlresolvers import reverse
from django.templatetags.static import static
from django.template import loader as django_template_loader, \
    Context as DjangoContext

from xblock.fields import Scope
from xblock.field_data import SplitFieldData, OrderedLookupWithDefaultDictReadOnlyFieldData
from xblock.runtime import (
    KvsFieldData, KeyValueStore, Runtime, NoSuchViewError, IdReader, IdGenerator
)
from xblock.exceptions import NoSuchDefinition, NoSuchUsage
from xblock.fragment import Fragment

import xblock.reference.plugins

from .models import XBlockState
from .util import make_safe_for_html

log = logging.getLogger(__name__)


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


class WorkbenchSplitFieldData(SplitFieldData):
    """
    A split field data for splitting out Scope.configurations to read from workbench's django settings
    """
    def __init__(self):
        """
        All other scopes default to the WORKBENCH_DEFAULT_FIELD_DATA, except Scope.configuration

        This uses closures over module variables to maintain compat with reset_global_state
        """
        scope_mappings = {}
        for scope in itertools.chain(Scope.named_scopes(), (Scope.parent, Scope.children)):
            scope_mappings[scope] = WORKBENCH_DEFAULT_FIELD_DATA
        scope_mappings[Scope.configuration] = WORKBENCH_CONFIG_FIELD_DATA  # This is the one exception
        super(WorkbenchSplitFieldData, self).__init__(scope_mappings=scope_mappings)


class ScenarioIdManager(IdReader, IdGenerator):
    """A scenario-aware ID manager.

    This will create IDs in the form of::

      {scenario-slug}.{block_type}.d{def #}(.u{usage #})

    So an example: a-little-html.html.d0.u0

    The definition numbering is local to the scenario + block_type, and usage
    numbering is local to the definition_id. This is to help ensure that IDs
    shift around as little as possible when you add new content/scenarios.

    """
    def __init__(self):
        self._block_types_to_id_seq = defaultdict(itertools.count)
        self._def_ids_to_id_seq = defaultdict(itertools.count)
        self._usages = OrderedDict()
        self._definitions = OrderedDict()
        self.scenario = ""

    def clear(self):
        """Remove all entries."""
        self._block_types_to_id_seq.clear()
        self._def_ids_to_id_seq.clear()
        self._usages.clear()
        self._definitions.clear()
        self.scenario = ""

    def create_usage(self, def_id):
        """Make a usage, storing its definition id."""
        id_seq = self._def_ids_to_id_seq[def_id]
        usage_id = "{}.u{}".format(def_id, next(id_seq))
        self._usages[usage_id] = def_id

        return usage_id

    def get_definition_id(self, usage_id):
        """Get a definition_id by its usage id."""
        try:
            return self._usages[usage_id]
        except KeyError:
            raise NoSuchUsage(repr(usage_id))

    def create_definition(self, block_type, slug=None):
        """Make a definition_id, storing its block type."""
        prefix = "{}.{}".format(self.scenario, block_type)
        if slug:
            prefix += "." + slug

        id_seq = self._block_types_to_id_seq[prefix]
        def_id = "{}.d{}".format(prefix, next(id_seq))
        self._definitions[def_id] = block_type

        return def_id

    def get_block_type(self, def_id):
        """Get a block_type by its definition id."""
        try:
            return self._definitions[def_id]
        except KeyError:
            raise NoSuchDefinition(repr(def_id))

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
        return self._usages.keys()[-1] if self._usages else None


class WorkbenchRuntime(Runtime):
    """
    Access to the workbench runtime environment for XBlocks.

    A pre-configured instance of this class will be available to XBlocks as
    `self.runtime`.

    """

    def __init__(self, user_id=None):
        #  TODO: Add params for user, runtime, etc. to service initialization
        #  Move to stevedor
        super(WorkbenchRuntime, self).__init__(ID_MANAGER, WORKBENCH_SPLIT_FIELD_DATA,
                                               services={'fs': xblock.reference.plugins.FSService()})
        self.id_generator = ID_MANAGER
        self.user_id = user_id

    def render(self, block, view_name, context=None):
        try:
            return super(WorkbenchRuntime, self).render(block, view_name, context)
        except NoSuchViewError:
            return Fragment(u"<i>No such view: %s on %s</i>"
                            % (view_name, make_safe_for_html(repr(block))))

    # TODO: [rocha] runtime should not provide this, each xblock
    # should use whatever they want
    def render_template(self, template_name, **kwargs):
        """Loads the django template for `template_name`"""
        template = django_template_loader.get_template(template_name)
        return template.render(DjangoContext(kwargs))

    def wrap_child(self, block, view, frag, context):  # pylint: disable=W0613
        wrapped = Fragment()
        wrapped.add_javascript_url(self.resource_url("js/vendor/jquery.min.js"))
        wrapped.add_javascript_url(self.resource_url("js/vendor/jquery.cookie.js"))

        data = {}
        if frag.js_init_fn:
            wrapped.add_javascript_url(self.resource_url("js/runtime/%s.js" % frag.js_init_version))
            data['init'] = frag.js_init_fn
            data['runtime-version'] = frag.js_init_version
            data['usage'] = block.scope_ids.usage_id
            data['block-type'] = block.scope_ids.block_type

        if block.name:
            data['name'] = block.name

        json_init = ""
        # TODO/Note: We eventually want to remove: hasattr(frag, 'json_init_args')
        # However, I'd like to maintain backwards-compatibility with older XBlock
        # for at least a little while so as not to adversely effect developers.
        # pmitros/Jun 28, 2014.
        if hasattr(frag, 'json_init_args') and frag.json_init_args is not None:
            json_init = u'<script type="json/xblock-args" class="xblock_json_init_args">' + \
                u'{data}</script>'.format(data=json.dumps(frag.json_init_args))

        html = u"<div class='xblock'{properties}>{body}{js}</div>".format(
            properties="".join(" data-%s='%s'" % item for item in data.items()),
            body=frag.body_html(),
            js=json_init)

        wrapped.add_content(html)
        wrapped.add_frag_resources(frag)
        return wrapped

    def handler_url(self, block, handler_name, suffix='', query='', thirdparty=False):
        # Be sure this really is a handler.
        func = getattr(block, handler_name, None)
        if not func:
            raise ValueError("{!r} is not a function name".format(handler_name))
        if not getattr(func, "_is_xblock_handler", False):
            raise ValueError("{!r} is not a handler name".format(handler_name))

        url = reverse(
            "unauth_handler" if thirdparty else "handler",
            args=(block.scope_ids.usage_id, handler_name, suffix)
        )

        has_query = False
        if not thirdparty:
            url += "?student={student}".format(student=block.scope_ids.user_id)
            has_query = True
        if query:
            url += "&" if has_query else "?"
            url += query
        return url

    def resource_url(self, resource):
        return static("workbench/" + resource)

    def local_resource_url(self, block, uri):
        return reverse("package_resource", args=(block.scope_ids.block_type, uri))

    def publish(self, block, event_type, event_data):
        log.info(
            "XBlock event {event_type} for {block_type} (usage_id={usage_id}):"
            .format(
                event_type=event_type,
                block_type=block.scope_ids.block_type,
                usage_id=block.scope_ids.usage_id
            )
        )
        log.info(event_data)

    def query(self, block):
        return _BlockSet(self, [block])


class _BlockSet(object):
    def __init__(self, runtime, blocks):
        self.runtime = runtime
        self.blocks = blocks

    def __iter__(self):
        return iter(self.blocks)

    def parent(self):
        them = set()
        for block in self.blocks:
            if block.parent:
                parent = self.runtime.get_block(block.parent)
                them.add(parent)
        return _BlockSet(self.runtime, them)

    def children(self):
        them = set()
        for block in self.blocks:
            for child_id in getattr(block, "children", ()):
                child = self.runtime.get_block(child_id)
                them.add(child)
        return _BlockSet(self.runtime, them)

    def descendants(self):
        them = set()

        def recur(block):
            for child_id in getattr(block, "children", ()):
                child = self.runtime.get_block(child_id)
                them.add(child)
                recur(child)

        for block in self.blocks:
            recur(block)

        return _BlockSet(self.runtime, them)

    def tagged(self, tag):
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
        for block in self.blocks:
            if hasattr(block, attr_name):
                yield getattr(block, attr_name)

# Our global state (the "database").
WORKBENCH_KVS = WorkbenchDjangoKeyValueStore()

# Our global id manager
ID_MANAGER = ScenarioIdManager()

WORKBENCH_DEFAULT_FIELD_DATA = KvsFieldData(WORKBENCH_KVS)

# Our global configuration field_data
WORKBENCH_CONFIG_FIELD_DATA = OrderedLookupWithDefaultDictReadOnlyFieldData(settings.XBLOCK_CONFIGURATION)

WORKBENCH_SPLIT_FIELD_DATA = WorkbenchSplitFieldData()


def reset_global_state():
    """
    Reset any global state in the workbench.

    This allows us to write properly isolated tests.

    """
    from .scenarios import init_scenarios       # avoid circularity.

    WORKBENCH_KVS.clear()
    ID_MANAGER.clear()
    init_scenarios()
