"""Setup for {{cookiecutter.short_name|lower}} XBlock."""

import os
from setuptools import setup


def package_data(pkg, root):
    """Generic function to find package_data for `pkg` under `root`."""
    data = []
    for dirname, _, files in os.walk(os.path.join(pkg, root)):
        for fname in files:
            data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='{{cookiecutter.short_name|lower}}-xblock',
    version='0.1',
    description='{{cookiecutter.short_name|lower}} XBlock',   # TODO: write a better description.
    packages=[
        '{{cookiecutter.short_name|lower}}',
    ],
    install_requires=[
        'XBlock',
    ],
    entry_points={
        'xblock.v1': [
            '{{cookiecutter.short_name|lower}} = {{cookiecutter.short_name|lower}}:{{cookiecutter.class_name}}',
        ]
    },
    package_data=package_data("{{cookiecutter.short_name|lower}}", "static"),
)
