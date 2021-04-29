"""An XBlock providing thumbs-up/thumbs-down voting.

This is a completely artifical test case for the filesystem field type. It
behaves just like the sample_xblocks/thumbs example, except it uses filesystem
fields.

Votes are stored in a JSON object in the file system, and up/down arrow PNGs
are constructed as files on-the-fly.

These uses are not great demonstrations of what you can do with a filesystem
field.  They should be used for storage of file-like data, usually with
varying file names.

This code is duplicative of much of the thumbs example.  If you are interested
in filesystem fields, examining the differences between this block and the
thumbs block will be instructive.

"""



import json
import logging

import pkg_resources
import png
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Boolean, Scope
from xblock.reference.plugins import Filesystem

log = logging.getLogger(__name__)

ARROW = [
    list(map(int, value))
    for value in [
        '11011',
        '10001',
        '00000',
        '11011',
        '11011',
        '11011',
        '10001',
    ]
]


@XBlock.needs('fs')
class FileThumbsBlock(XBlock):
    """
    An XBlock with thumbs-up/thumbs-down voting.

    Vote totals are stored for all students to see.  Each student is recorded
    as has-voted or not.

    This demonstrates multiple data scopes and ajax handlers.

    """

    upvotes = 0
    downvotes = 0
    voted = Boolean(help="Has this student voted?", default=False, scope=Scope.user_state)
    fs = Filesystem(help="File system", scope=Scope.user_state_summary)  # pylint: disable=invalid-name

    def student_view(self, context=None):  # pylint: disable=W0613
        """
        Create a fragment used to display the XBlock to a student.
        `context` is a dictionary used to configure the display (unused)

        Returns a `Fragment` object specifying the HTML, CSS, and JavaScript
        to display.
        """

        # Load the HTML fragment from within the package and fill in the template
        html_str = pkg_resources.resource_string(__name__,
                                                 "static/html/thumbs.html").decode('utf-8')
        frag = Fragment(str(html_str))

        if not self.fs.exists("thumbsvotes.json"):
            with self.fs.open('thumbsvotes.json', 'wb') as file_output:
                file_output.write(json.dumps({'up': 0, 'down': 0}).encode())
                file_output.close()

        votes = json.load(self.fs.open("thumbsvotes.json"))
        self.upvotes = votes['up']
        self.downvotes = votes['down']

        # Load the CSS and JavaScript fragments from within the package
        css_str = pkg_resources.resource_string(__name__,
                                                "static/css/thumbs.css").decode('utf-8')
        frag.add_css(str(css_str))

        js_str = pkg_resources.resource_string(__name__,
                                               "static/js/src/thumbs.js").decode('utf-8')
        frag.add_javascript(str(js_str))

        with self.fs.open('uparrow.png', 'wb') as file_output:
            png.Writer(len(ARROW[0]), len(ARROW), greyscale=True, bitdepth=1).write(file_output, ARROW)

        with self.fs.open('downarrow.png', 'wb') as file_output:
            png.Writer(len(ARROW[0]), len(ARROW), greyscale=True, bitdepth=1).write(file_output, ARROW[::-1])

        frag.initialize_js('FileThumbsBlock', {'up': self.upvotes,
                                               'down': self.downvotes,
                                               'voted': self.voted,
                                               'uparrow': self.fs.get_url('uparrow.png'),
                                               'downarrow': self.fs.get_url('downarrow.png')})
        return frag

    problem_view = student_view

    @XBlock.json_handler
    def vote(self, data, suffix=''):  # pylint: disable=unused-argument
        """
        Update the vote count in response to a user action.
        """
        # Here is where we would prevent a student from voting twice, but then
        # we couldn't click more than once in the demo!
        #
        #     if self.voted:
        #         log.error("cheater!")
        #         return

        votes = json.load(self.fs.open("thumbsvotes.json"))
        self.upvotes = votes['up']
        self.downvotes = votes['down']

        if data['voteType'] not in ('up', 'down'):
            log.error('error!')
            return None

        if data['voteType'] == 'up':
            self.upvotes += 1
        else:
            self.downvotes += 1

        with self.fs.open('thumbsvotes.json', 'wb') as file_output:
            file_output.write(
                json.dumps({'up': self.upvotes, 'down': self.downvotes}).encode()
            )

        self.voted = True

        return {'up': self.upvotes, 'down': self.downvotes}

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("filethumbs",
             """\
                <vertical_demo>
                    <filethumbs/>
                    <filethumbs/>
                    <filethumbs/>
                </vertical_demo>
             """)
        ]
