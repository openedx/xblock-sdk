"""Set up for XBlock SDK"""
import os
import os.path
from setuptools import setup


def find_package_data(pkg, data_paths):
    """Generic function to find package_data for `pkg` under `root`."""
    data = []
    for data_path in data_paths:
        package_dir = pkg.replace(".", "/")
        for dirname, _, files in os.walk(package_dir + "/" + data_path):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), package_dir))
    return {pkg: data}


def is_requirement(line):
    """
    Return True if the requirement line is a package requirement;
    that is, it is not blank, a comment, or editable.
    """
    # Remove whitespace at the start/end of the line
    line = line.strip()

    # Skip blank lines, comments, and editable installs
    return not (
        line == '' or
        line.startswith('-r') or
        line.startswith('#') or
        line.startswith('-e') or
        line.startswith('git+')
    )


def load_requirements(*requirements_paths):
    """
    Load all requirements from the specified requirements files.
    Returns a list of requirement strings.
    """
    requirements = set()
    for path in requirements_paths:
        requirements.update(
            line.strip() for line in open(path).readlines()
            if is_requirement(line)
        )
    return list(requirements)


package_data = {}  # pylint: disable=invalid-name
package_data.update(find_package_data("sample_xblocks.basic", ["public", "templates"]))
package_data.update(find_package_data("sample_xblocks.thumbs", ["static"]))
package_data.update(find_package_data("sample_xblocks.filethumbs", ["static"]))
package_data.update(find_package_data("workbench", ["static", "templates"]))

setup(
    name='xblock-sdk',
    version='0.1.2',
    description='XBlock SDK',
    packages=[
        'sample_xblocks',
        'sample_xblocks.basic',
        'sample_xblocks.thumbs',
        'sample_xblocks.filethumbs',
        'workbench',
    ],
    install_requires=load_requirements('requirements/base.txt'),
    tests_require=load_requirements('requirements/test.txt'),
    entry_points={
        'xblock.v1': [
            # Basic XBlocks
            'helloworld_demo = sample_xblocks.basic.content:HelloWorldBlock',
            'allscopes_demo = sample_xblocks.basic.content:AllScopesBlock',
            'html_demo = sample_xblocks.basic.content:HtmlBlock',
            'sequence_demo = sample_xblocks.basic.structure:Sequence',
            'vertical_demo = sample_xblocks.basic.structure:VerticalBlock',
            'sidebar_demo = sample_xblocks.basic.structure:SidebarBlock',
            'problem_demo = sample_xblocks.basic.problem:ProblemBlock',
            'textinput_demo = sample_xblocks.basic.problem:TextInputBlock',
            'equality_demo = sample_xblocks.basic.problem:EqualityCheckerBlock',
            'attempts_scoreboard_demo = sample_xblocks.basic.problem:AttemptsScoreboardBlock',
            'slider_demo = sample_xblocks.basic.slider:Slider',
            'view_counter_demo = sample_xblocks.basic.view_counter:ViewCounter',

            # Thumbs example
            'thumbs = sample_xblocks.thumbs:ThumbsBlock',
            'filethumbs = sample_xblocks.filethumbs:FileThumbsBlock',

            # Workbench specific
            'debugchild = workbench.blocks:DebuggingChildBlock',
        ],
        'xblock_asides.v1': [
            # ThumbsAside example. Asides aren't ready yet, so we'll disable
            # this for now.  When we get back to working on asides, we'll come
            # up with a more sophisticated mechanism to enable this for the
            # developers that want to see it.
            #   'thumbs_aside = sample_xblocks.thumbs:ThumbsAside',
        ]
    },
    package_data=package_data,
)
