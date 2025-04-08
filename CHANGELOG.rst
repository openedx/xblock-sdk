=============================
Change history for XBlock SDK
=============================

These are notable changes in XBlock.

0.13.0 - 2025-04-08
-------------------
* upgraded to Ubuntu 24.04 and Python 3.12
* replaced deprecated docker-compose command with docker compose
* remove unsupported docker instructions, as part of https://github.com/openedx/public-engineering/issues/263
* Added support for Django 5.2

0.12.0 - 2024-05-30
------------------
* dropped python 3.8 support
* transitioned from deprecated pkg_resources lib to importlib.resources

0.9.0
-----
* Xblock bumped to 3.0.0. Removed the deprecated id_generator method parameter in xblock.runtime

0.8.0
-----
* Added support for python 3.12
* Dropped support for django 3.2


0.7.0
-----
* Added support for Django 4.2

0.6.0
-----
* Removed boto usage.
* openedx-django-pyf is now using boto3 to generate URL.

0.5.0
-----
* Removed Django22, 30 and 31 support
* Added Django40 support
* Renamed CI job so that our modernizers work fine
* Code changes related to things removed in Django40

0.4.0
-----
* Added support for Django 3.0, Django 3.1 and Django 3.2 tests
* Added GitHub CI to replace Travis

0.3.0
-----
* Dropped support for Python 3.5
* Upgraded Code To Python 3.8 Standards
* Upgraded dependencies to Python 3.8

0.2.0
-----
* Released on PyPI

0.1.5
-----
* Use tox to test against Django 1.8 and 1.11.

* Add quality testing via tox and pylint.

0.1 - In Progress
-----------------

* Make Scope enums (UserScope.* and BlockScope.*) into Sentinels, rather than just ints,
  so that they can have more meaningful string representations.

* Rename `export_xml` to `add_xml_to_node`, to more accurately capture the semantics.

* Allowed `Runtime` implementations to customize loading from **block_types** to
  `XBlock` classes.

