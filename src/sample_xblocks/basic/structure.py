"""Structure-oriented XBlocks."""



from web_fragments.fragment import Fragment
from xblock.core import XBlock


class ExtraViewsMixin:
    '''
    This is a mixin which will redirect all functions ending with
    `_view` to `view()` if not implemented otherwise.

    This allows us to test other views in structural elements. For
    example, if we have a `<vertical_demo>` with a few blocks we are
    testing, we can test `student_view`, `studio_view` (if developing
    for edx-platform) and others.
    '''
    def __getattr__(self, key):
        if key.endswith('_view'):
            return self.view
        raise AttributeError(key)


class Sequence(XBlock, ExtraViewsMixin):
    """
    XBlock that models edx-platform style sequentials.

    WARNING: This is an experimental module, subject to future change or removal.
    """
    has_children = True

    def view(self, context=None):
        """Provide default student view."""
        frag = Fragment()
        child_frags = self.runtime.render_children(self, context=context)
        frag.add_resources(child_frags)

        frag.add_content(self.runtime.render_template("sequence.html", children=child_frags))

        frag.add_css_url('http://code.jquery.com/ui/1.9.2/themes/base/jquery-ui.css')
        frag.add_javascript_url('http://ajax.googleapis.com/ajax/libs/jqueryui/1.9.2/jquery-ui.min.js')

        # mess things up
        frag.add_javascript("""
            function Sequence(runtime, element) {
              $(element).children('.tabs').tabs();
            };
            """)
        frag.initialize_js('Sequence')
        return frag


class VerticalBlock(XBlock, ExtraViewsMixin):
    """A simple container."""
    has_children = True

    def view(self, context=None):
        """Provide default student view."""
        result = Fragment()
        child_frags = self.runtime.render_children(self, context=context)
        result.add_resources(child_frags)
        result.add_css("""
            .vertical {
                border: solid 1px #888; padding: 3px;
            }
            """)
        result.add_content(self.runtime.render_template("vertical.html", children=child_frags))
        return result


class SidebarBlock(XBlock, ExtraViewsMixin):
    """A slightly-different vertical."""
    has_children = True

    def view(self, context=None):
        """Provide default student view."""
        result = Fragment()
        child_frags = self.runtime.render_children(self, context=context)
        result.add_resources(child_frags)
        result.add_css("""
            .sidebar {
                border: solid 1px #888;
                padding: 10px;
                background: #ccc;
            }
            """)
        html = []
        html.append("<div class='sidebar'>")
        for child in child_frags:
            html.append(child.body_html())
        html.append("</div>")
        result.add_content("".join(html))
        return result
