=============================
Change history for XBlock SDK
=============================

These are notable changes in XBlock.

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

