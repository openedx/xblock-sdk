=============================
Change history for XBlock SDK
=============================

These are notable changes in XBlock.

0.1 - In Progress
-----------------

* Make Scope enums (UserScope.* and BlockScope.*) into Sentinels, rather than just ints,
  so that they can have more meaningful string representations.

* Rename `export_xml` to `add_xml_to_node`, to more accurately capture the semantics.

* Allowed `Runtime` implementations to customize loading from **block_types** to
  `XBlock` classes.

