"""An XBlock to use as a child when you don't care what child to show.

This code is in the Workbench layer.

"""



from web_fragments.fragment import Fragment
from xblock.core import XBlock

from .util import make_safe_for_html


class DebuggingChildBlock(XBlock):
    """A simple gray box, to use as a child placeholder."""
    def fallback_view(self, view_name, context=None):  # pylint: disable=W0613
        """Provides a fallback view handler"""
        frag = Fragment(f"<div class='debug_child'>{make_safe_for_html(repr(self))}<br>{view_name}</div>")
        frag.add_css("""
            .debug_child {
                background-color: grey;
                width: 300px;
                height: 100px;
                margin: 10px;
                padding: 5px 10px;
                font-size: 75%;
            }
            """)
        return frag
