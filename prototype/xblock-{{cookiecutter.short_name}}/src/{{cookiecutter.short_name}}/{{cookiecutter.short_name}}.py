"""TO-DO: Write a description of what this XBlock is."""

import json
from pathlib import Path

from django.conf import settings
from web_fragments.fragment import Fragment
from webob import Response
from xblock.core import XBlock
from xblock.fields import Integer, Scope, String
from xblock.utils.resources import ResourceLoader

resource_loader = ResourceLoader(__name__)


class {{cookiecutter.class_name}}(XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    # This is used by the studio to label the block. It doesn't appear for the
    # student unless you choose to render it.
    display_name = String(default="{{cookiecutter.class_name}}")
    # TO-DO: delete count and code, and define your own fields.
    count = Integer(
        default=0,
        scope=Scope.user_state,
        help="A simple counter, to show something happening",
    )
    code = String(
        default="beep", scope=Scope.settings, help="code word to check for on update"
    )

    def resource_string(self, path: str | Path) -> str:
        """Handy helper for getting resources from our kit."""
        return resource_loader.load_unicode(path)

    def student_view(self, context=None):
        """
        The primary view of the {{cookiecutter.class_name}}, shown to students
        when viewing courses.
        """
        return self.render_view("student")

    def render_view(self, view_name: str, normalize=False):
        """
        Render a view for the user. Loads the specifically needed js based
        on the view name.
        """
        html = resource_loader.load_unicode(f"static/html/{view_name}.html")
        frag = Fragment(html)
        if normalize:
            frag.add_css(resource_loader.load_unicode("static/css/studio.css"))
        frag.add_javascript(self.resource_string("static/js/src/{{cookiecutter.short_name|lower}}.js"))
        frag.initialize_js(
            "{{cookiecutter.class_name}}",
            {
                "url": self.runtime.local_resource_url(self, f"public/{view_name}.js"),
                "data": {
                    "count": self.count,
                    "code": self.code,
                    "display_name": self.display_name,
                },
                "config": {
                    "mfe_config_api": f"{settings.LMS_ROOT_URL}/api/mfe_config/v1?mfe=learning",
                },
            },
        )
        return frag

    def studio_view(self, context=None):
        """
        The primary view of the {{cookiecutter.class_name}}, shown to students
        when viewing courses.
        """
        return self.render_view("studio", normalize=True)

    # TO-DO: change this handler to perform your own actions.  You may need more
    # than one handler, or you may not need any handlers at all.
    @XBlock.json_handler
    def increment(self, data, suffix=""):
        """
        An example handler, which increments the data.
        """
        if data.get("code") != self.code:
            return Response(
                json.dumps({"error": "Code does not match!"}),
                status=400,
                content_type="application/json",
                charset="utf8",
            )

        self.count += 1
        return {"count": self.count}

    # Used to save settings from the studio.
    @XBlock.json_handler
    def studio_save(self, data, suffix=""):
        """
        Save the data for the block.
        """
        self.display_name = data.get("display_name", self.display_name)
        self.code = data.get("code", self.code)
        return {}

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            (
                "{{cookiecutter.class_name}}",
                """<{{cookiecutter.short_name|lower}}/>
                """,
            ),
            (
                "Multiple {{cookiecutter.class_name}}",
                """<vertical_demo>
                   <{{cookiecutter.short_name|lower}}/>
                   <{{cookiecutter.short_name|lower}}/>
                   <{{cookiecutter.short_name|lower}}/>
                </vertical_demo>
                """,
            ),
        ]
