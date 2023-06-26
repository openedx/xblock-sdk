"""Set up for XBlock SDK"""

import os
import os.path
import re

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
    Return True if the requirement line is a package requirement.

    Returns:
        bool: True if the line is not blank, a comment,
        a URL, or an included file
    """
    # UPDATED VIA SEMGREP - if you need to remove/modify this method remove this line and add a comment specifying why

    return line and line.strip() and not line.startswith(('-r', '#', '-e', 'git+', '-c'))


def load_requirements(*requirements_paths):
    """
    Load all requirements from the specified requirements files.

    Requirements will include any constraints from files specified
    with -c in the requirements files.
    Returns a list of requirement strings.
    """
    # UPDATED VIA SEMGREP - if you need to remove/modify this method remove this line and add a comment specifying why.

    requirements = {}
    constraint_files = set()

    # groups "my-package-name<=x.y.z,..." into ("my-package-name", "<=x.y.z,...")
    requirement_line_regex = re.compile(r"([a-zA-Z0-9-_.]+)([<>=][^#\s]+)?")

    def add_version_constraint_or_raise(current_line, current_requirements, add_if_not_present):
        regex_match = requirement_line_regex.match(current_line)
        if regex_match:
            package = regex_match.group(1)
            version_constraints = regex_match.group(2)
            existing_version_constraints = current_requirements.get(package, None)
            # it's fine to add constraints to an unconstrained package, but raise an error if there are already
            # constraints in place
            if existing_version_constraints and existing_version_constraints != version_constraints:
                raise BaseException(f'Multiple constraint definitions found for {package}:'
                                    f' "{existing_version_constraints}" and "{version_constraints}".'
                                    f'Combine constraints into one location with {package}'
                                    f'{existing_version_constraints},{version_constraints}.')
            if add_if_not_present or package in current_requirements:
                current_requirements[package] = version_constraints

    # process .in files and store the path to any constraint files that are pulled in
    for path in requirements_paths:
        with open(path) as reqs:
            for line in reqs:
                if is_requirement(line):
                    add_version_constraint_or_raise(line, requirements, True)
                if line and line.startswith('-c') and not line.startswith('-c http'):
                    constraint_files.add(os.path.dirname(path) + '/' + line.split('#')[0].replace('-c', '').strip())

    # process constraint files and add any new constraints found to existing requirements
    for constraint_file in constraint_files:
        with open(constraint_file) as reader:
            for line in reader:
                if is_requirement(line):
                    add_version_constraint_or_raise(line, requirements, False)

    # process back into list of pkg><=constraints strings
    constrained_requirements = [f'{pkg}{version or ""}' for (pkg, version) in sorted(requirements.items())]
    return constrained_requirements


def get_version(*file_paths):
    """
    Extract the version string from the file at the given relative path fragments.
    """
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    with open(filename, encoding='utf-8') as opened_file:
        version_file = opened_file.read()
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                                  version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


VERSION = get_version("workbench", "__init__.py")
package_data = {}  # pylint: disable=invalid-name
package_data.update(find_package_data("sample_xblocks.basic", ["public", "templates"]))
package_data.update(find_package_data("sample_xblocks.thumbs", ["static"]))
package_data.update(find_package_data("sample_xblocks.filethumbs", ["static"]))
package_data.update(find_package_data("workbench", ["static", "templates", "test"]))

setup(
    name='xblock-sdk',
    version=VERSION,
    description='XBlock SDK',
    long_description="XBlock SDK",
    packages=[
        'sample_xblocks',
        'sample_xblocks.basic',
        'sample_xblocks.thumbs',
        'sample_xblocks.filethumbs',
        'workbench',
    ],
    install_requires=load_requirements('requirements/base.in'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
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
