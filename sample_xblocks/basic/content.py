# -*- coding: utf-8 -*-
"""Content-oriented XBlocks."""

from string import Template  # pylint: disable=W0402

from lxml import etree

from xblock.core import XBlock, String, Scope
from xblock.fragment import Fragment


class HelloWorldBlock(XBlock):
    """A simple block: just show some fixed content."""

    def fallback_view(self, view_name, context=None):  # pylint: disable=W0613
        """Provide a fallback view handler"""
        return Fragment(u"Hello, World!")

    @staticmethod
    def workbench_scenarios():
        return [
            ("Hello World", "<helloworld_demo/>")
        ]


class AllScopesBlock(XBlock):
    """Block that has a string field for every scope.

    Help strings are cribbed from the XBlock repo.
    """
    content_field = String(
        scope=Scope.content,
        default=u"This is content!",
        help=(
            u"The content scope is used to save data for all users, for one "
            u"particular block, across all runs of a course. An example might "
            u"be an XBlock that wishes to tabulate user \"upvotes\", or HTML "
            u"content to display literally on the page (this example being the "
            u"reason this scope is named `content`)."
        )
    )
    settings_field = String(
        scope=Scope.settings,
        default=u"This is settings!",
        help=(
            u"The settings scope is used to save data for all users, for one "
            u"particular block, for one specific run of a course. This is like "
            u"the `content` scope, but scoped to one run of a course. An "
            u"example might be a due date for a problem."
        )
    )
    user_state_field = String(
        scope=Scope.user_state,
        default=u"This is user_state!",
        help=(
            u"The user_state scope is used to save data for one user, for one "
            u"block, for one run of a course. An example might be how many "
            u"points a user scored on one specific problem."
        )
    )
    preferences_field = String(
        scope=Scope.preferences,
        default=u"This is preferences!",
        help=(
            u"The preferences scope is used to save data for one user, for all "
            u"instances of one specific TYPE of block, across the entire "
            u"platform. An example might be that a user can set their preferred "
            u"default speed for the video player. This default would apply to "
            u"all instances of the video player, across the whole platform, but "
            u"only for that student."
        )
    )
    user_info_field = String(
        scope=Scope.user_info,
        default=u"This is user_info!",
        help=(
            u"The user_info scope is used to save data for one user, across "
            u"the entire platform. An example might be a user's time zone or "
            u"language preference."
        )
    )
    user_state_summary_field = String(
        scope=Scope.user_state_summary,
        default=u"This is user_state_summary!",
        help=(
            u"The user_state_summary scope is used to save data aggregated "
            u"across many users of a single block. For example, a block might "
            u"store a histogram of the points scored by all users attempting a "
            u"problem. For the purposes of the workbench, this is stored in "
            u"the same JSON record as settings_field."
        )
    )

    def fallback_view(self, view_name, context=None):  # pylint: disable=W0613
        """Display all fields, their values, and some helpful info text."""
        entry_template = u"""
            <tr>
                <td>{field_name}</td>
                <td>{value}</td>
                <td>{help}</td>
            </tr>
        """
        # Go through all the named fields declared for this block, but exclude
        # things that users can't directly manipulate by editing state in the
        # database (name, parent, tags).
        entries = [
            entry_template.format(
                field_name=field_name,
                value=getattr(self, field_name),
                help=field.help
            )
            for field_name, field in self.fields.items()
            if field_name not in ["name", "parent", "tags"]
        ]

        frag = Fragment(
            u"""
                <table style="vertical-align:top;">
                    <tr>
                        <th>Name</th>
                        <th>Value</th>
                        <th>About</th>
                    </tr>
                    {}
                </table>

            """.format(u"\n".join(entries)))
        frag.add_css("""
            table { border-collapse:collapse; }
            table, th, td { border: 1px solid black; }
            td { vertical-align:top; }
            """)

        return frag

    @staticmethod
    def workbench_scenarios():
        """Return very basic display of fields and help."""
        return [
            ("All Scopes", "<allscopes_demo/>")
        ]


class HtmlBlock(XBlock):
    """Render content as HTML.

    The content can have $PLACEHOLDERS, which will be substituted with values
    from the context.

    """

    content = String(help="The HTML to display", scope=Scope.content, default=u"<b>DEFAULT</b>")

    def fallback_view(self, view_name, context=None):
        """Provide a fallback view handler"""
        context = context or {}
        return Fragment(Template(self.content).substitute(**context))

    @classmethod
    def parse_xml(cls, node, runtime, keys, id_generator):
        """
        Parse the XML for an HTML block.

        The entire subtree under `node` is re-serialized, and set as the
        content of the XBlock.

        """
        block = runtime.construct_xblock_from_class(cls, keys)

        block.content = unicode(node.text or u"")
        for child in node:
            block.content += etree.tostring(child, encoding='unicode')

        return block

    def add_xml_to_node(self, node):
        """
        Set attributes and children on `node` to represent ourselves as XML.

        We parse our HTML content, and graft those nodes onto `node`.

        """
        xml = "<html_demo>" + self.content + "</html_demo>"
        html_node = etree.fromstring(xml)

        node.tag = html_node.tag
        node.text = html_node.text
        for child in html_node:
            node.append(child)

    @staticmethod
    def workbench_scenarios():
        return [
            ("A little HTML", """
                <vertical_demo>
                <html_demo>
                <h2>Gettysburg Address</h2>

                <p>Four score and seven years ago our fathers brought forth on
                this <a href='http://en.wikipedia.org/wiki/Continent'>continent</a>
                a new nation, conceived in liberty, and dedicated to
                the proposition that all men are created equal.</p>

                <p>Now we are engaged in a great <a href='http://en.wikipedia.org/wiki/Civil_war'>civil war</a>,
                testing whether that nation, or any nation so conceived and so
                dedicated, can long endure. We are met on a great battle-field of
                that war. We have come to dedicate a portion of that field, as a
                final resting place for those who here gave their lives that that
                nation might live. It is altogether fitting and proper that we
                should do this.</p>

                <p>But, in a larger sense, we can not dedicate, we can not
                consecrate, we can not hallow this ground. The brave men, living
                and dead, who struggled here, have consecrated it, far above our
                poor power to add or detract. The world will little note, nor long
                remember what we say here, but it can never forget what they did
                here. It is for us the living, rather, to be dedicated here to the
                unfinished work which they who fought here have thus far so nobly
                advanced. It is rather for us to be here dedicated to the great
                task remaining before us &#8212; that from these honored dead we
                take increased devotion to that cause for which they gave the last
                full measure of devotion &#8212; that we here highly resolve that
                these dead shall not have died in vain &#8212; that this nation,
                under God, shall have a new birth of freedom &#8212; and that
                government of the people, by the people, for the people, shall not
                perish from the earth.</p>
                </html_demo>
                </vertical_demo>
             """),
        ]
