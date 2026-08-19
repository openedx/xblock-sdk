"""
XBlock persistent state storage.

We use a Django model to store state in all our various scopes in one table. We
make no effort to be smart about batch updates, so performance isn't great. We
mostly use Django because we already have it as a dependency and because Django
Admin gives us a lot of basic search/filtering for free.

"""


from xblock.fields import BlockScope, Scope

from django.db import models
from django.utils.timezone import now


def shorten_scope_name(scope_name):
    """
    Strip the "blockscope_" or "scope_" prefixes from scope names.
    """
    _prefix, rest = scope_name.split("_", 1)
    return rest


class XBlockState(models.Model):
    """State storage for XBlock.

    This class assumes your IDs were generated using `ScenarioIdManager`, and
    will break otherwise.
    """
    class Meta:
        """Class metadata"""
        verbose_name = "XBlock State"
        verbose_name_plural = "XBlock State"
        ordering = ['scope_id', 'scope', 'user_id']

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
    created = models.DateTimeField(default=now, db_index=True)
    state = models.TextField(default="{}")

    # pylint: disable=missing-format-attribute
    def __repr__(self):
        return "<XBlockState id={xb_state.id} " \
            "scope={xb_state.scope} " \
            "scope_id={xb_state.scope_id} " \
            "user_id={xb_state.user_id} " \
            "scenario={xb_state.scenario} " \
            "tag={xb_state.tag}>".format(xb_state=self)

    @classmethod
    def get_for_key(cls, key):
        """
        Get or create the model row for a given `KeyValueStore.Key` `key`.
        """
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

        record, _ = cls.objects.get_or_create(
            scope=block_scope_name,
            scope_id=key.block_scope_id,
            user_id=key.user_id,
            scenario=scenario,
            tag=tag,
        )
        return record

    @classmethod
    def prep_for_scenario_loading(cls):
        """
        This method should be executed once before loading scenarios.

        For the most part, when scenarios load, they just overwrite their
        previous entries. But adding children is an append operation, so we just
        delete all the children scoped entries in this method.

        Note that this should be called *once* before any scenario loading
        happens. It should *not* be called before each scenario.
        """
        cls.objects.filter(scope="children").delete()

    def __str__(self):
        return self.__repr__()
