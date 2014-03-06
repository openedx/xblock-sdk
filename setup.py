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

package_data = {}
package_data.update(find_package_data("sample_xblocks.basic", ["public", "templates"]))
package_data.update(find_package_data("sample_xblocks.thumbs", ["static"]))
package_data.update(find_package_data("workbench", ["static", "templates"]))

setup(
    name='xblock-sdk',
    version='0.1a0',
    description='XBlock SDK',
    packages=[
        'sample_xblocks',
        'sample_xblocks.basic',
        'sample_xblocks.thumbs',
        'workbench',
    ],
    install_requires=[
        # 'XBlock',  # Can put this once XBlock is on PyPI
        'Django >= 1.4, < 1.5',
        'lxml',
        'requests',
        'webob',
        'WSGIProxy',
        'simplejson',
        'lazy',
        'django_nose',
        'mock',
        'coverage',
        'pylint == 0.28',
        'selenium',
        'rednose',
        'pep8',
        'diff-cover >= 0.2.1',
    ],
    entry_points={
        'xblock.v1': [
            # Basic XBlocks
            'helloworld_demo = sample_xblocks.basic.content:HelloWorldBlock',
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

            # Workbench specific
            'debugchild = workbench.blocks:DebuggingChildBlock',
        ]
    },
    package_data=package_data,
)
