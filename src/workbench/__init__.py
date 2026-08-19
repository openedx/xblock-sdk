# pylint: disable=django-not-configured
"""
Provide a djangoapp for XBlock development
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("xblock-sdk")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
