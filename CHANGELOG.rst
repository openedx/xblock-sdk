=============================
Change history for XBlock SDK
=============================

These are notable changes in XBlock.

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

