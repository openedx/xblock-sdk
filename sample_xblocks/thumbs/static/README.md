# XBlock Static Files

An XBlock can load resources from its package using Python's
[importlib.resources](https://docs.python.org/3/library/importlib.resources.html).

We use a directory structure with folders for `css`, `html`, and `js`
files.  However, this structure is not mandatory.  Each XBlock can
choose its directory structure, as long as it specifies the correct
paths to `importlib.resources`.

We include unit tests for JavaScript in the `js` folder.  See `js/README.md`
for details on how to run these tests.
