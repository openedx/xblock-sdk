"""
XBlock persistent state storage.

We use a Django model to store state in all our various scopes in one table. We
make no effort to be smart about batch updates, so performance isn't great. We
mostly use Django because we already have it as a dependency and because Django
Admin gives us a lot of basic search/filtering for free.

"""
try:
    import simplejson as json
except ImportError:
    import json

from django.db import models
from django.utils.timezone import now

from xblock.fields import BlockScope, Scope


def shorten_scope_name(scope_name):
    """Strip the "blockscope_" or "scope_" prefixes from scope names."""
    _prefix, rest = scope_name.split("_", 1)
    return rest


class XBlockState(models.Model):
    """State storage for XBlock.

    This class assumes your IDs were generated using `ScenarioIdManager`, and
    will break otherwise.

    """
    BLOCK_SCOPE_NAMES = [
        (shorten_scope_name(sentinel.attr_name), shorten_scope_name(sentinel.attr_name))
        for sentinel in BlockScope.scopes() + [Scope.parent, Scope.children]
    ]

    # Either the block scope or the special scopes "children" or "parent"
    scope = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        db_index=True,
        choices=BLOCK_SCOPE_NAMES
    )
    scope_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True,
        verbose_name="Scope ID",
    )
    user_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True,
        verbose_name="User ID",
    )
    scenario = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True,
    )
    tag = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        db_index=True,
    )
    field = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True
    )
    value = models.TextField(default='')
    created = models.DateTimeField(default=now, db_index=True)
    modified = models.DateTimeField(default=now, db_index=True)

    @classmethod
    def _db_fields_for_key(cls, key):
        """Return a dictionary with the database fields to search for the given `key`."""
        if key.scope in [Scope.parent, Scope.children]:
            block_scope_full_name = key.scope.attr_name
        else:
            block_scope_full_name = key.scope.block.attr_name
        block_scope_name = shorten_scope_name(block_scope_full_name)
        scope_id = key.block_scope_id

        # A block_scope_name of "type" is special -- this means that it's a
        # preferences scoped var that is global to the XBlock class (and not to
        # any particular scenario, definition, or usage). As such, it doesn't
        # abide by the {scenario}.{tag}.{def}.{usage} convention as our other
        # keys do, and is always simply {tag}
        #
        # A block_scope_name of "all" means user_info -- data that is
        # specific to a user, but crosses all scenarios and blocks (e.g.
        # user timezone, language). In this case, we also set our scenario to
        # be None.
        if block_scope_name in ["type", "all"]:
            scenario = None
            tag = scope_id
        else:
            scenario, tag, _ = scope_id.split(".", 2)

        return {
            'scope': block_scope_name,
            'scope_id': key.block_scope_id,
            'user_id': key.user_id,
            'scenario': scenario,
            'tag': tag,
            'field': key.field_name
        }

    @classmethod
    def get_for_key(cls, key):
        """Get the model row for a given `KeyValueStore.Key` `key`."""
        db_fields = cls._db_fields_for_key(key)

        # It's possible for multiple records to be created for the same
        # key when running workbench under gunicorn and MySQL with repeatable-read.
        # If this happens, we return the most recently modified record.
        records = cls.objects.filter(**db_fields)[:1]
        return None if len(records) == 0 else records[0]

    @classmethod
    def create_for_key(cls, key):
        """Create a row for the given `KeyValueStore.Key` `key`."""
        db_fields = cls._db_fields_for_key(key)
        return cls.objects.create(**db_fields)

    @classmethod
    def prep_for_scenario_loading(cls):
        """This method should be executed once before loading scenarios.

        For the most part, when scenarios load, they just overwrite their
        previous entries. But adding children is an append operation, so we just
        delete all the children scoped entries in this method.

        Note that this should be called *once* before any scenario loading
        happens. It should *not* be called before each scenario.
        """
        cls.objects.filter(scope="children").delete()

    def get_value(self):
        """Return the deserialized value of this key."""
        return json.loads(self.value)

    def set_value(self, value):
        """Serialize the `value` (must be JSON-serializable) and save it."""
        self.value = json.dumps(value, indent=2, sort_keys=True)
        self.modified = now()
        self.save()

    class Meta:  # pylint:disable=C0111
        verbose_name = "XBlock State"
        verbose_name_plural = "XBlock State"
        ordering = ['scope_id', 'scope', 'user_id', '-modified']
