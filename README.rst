XBlock SDK |build-status| |coverage-status|
===========================================

This repository consists of three main components to assist in the creation of new XBlocks:

    * a template-based generator for new XBlocks (found in `prototype`)
    * sample XBlocks that can be the basis for new XBlock work (found in `sample_xblocks`)
    * Workbench runtime, a simple runtime for viewing and testing XBlocks in a browser (found in `workbench`)


Installation
------------

This code runs on Python 2.7.

1.  Get a local copy of this repo.

2.  (Optional)  Create and activate a virtualenv to work in.

3.  Install the requirements and register the XBlock entry points with (you may
    need to sudo this if you don't use virtualenv):

        $ make install

4.  Run the Django development server:

        $ python manage.py runserver

5.  Open a web browser to: http://127.0.0.1:8000

Testing
--------

To install all requirements and run the test suite:

    $ make

This will run:

    * Integration tests of XBlocks running within the workbench.
    * Individual tests written for the demo XBlocks

You can test XBlocks through a browser using `Selenium`_. We have included an
example Selenium test for ``thumbs`` that uses Django's `LiveServerTestCase`_.
It runs as part of the test suite as executed by the above command. You need to
have Firefox installed for this test case to run successfully.

.. _Selenium: http://docs.seleniumhq.org/
.. _LiveServerTestCase: https://docs.djangoproject.com/en/1.4/topics/testing/#django.test.LiveServerTestCase

To update and view test coverage:

    $ make cover

See the `coverage.py`_ docs for more info and options.

.. _coverage.py: http://nedbatchelder.com/code/coverage/

Using the workbench
-------------------

When you open the workbench, you'll see a list of sample XBlock configurations
(scenarios).  Each will display a page showing the XBlocks composited together,
along with internal information like the "database" contents.

The workbench database defaults to a sqlite3 database. If you're using devstack,
you may want to set `WORKBENCH_DATABASES` to point to your mysql db.

If you want to experiment with different students, you can use a URL parameter
to set the student ID, which defaults to 1:

    http://127.0.0.1:8000/?student=17

Different students will see different student state, for example, while seeing
the same content.  Student ids are strings, even if they contain only digits
as the default does.


Making your own XBlock
----------------------

Making an XBlock can be as simple as creating a Python class with a few
specific methods.  The ``thumbs`` XBlock demonstrates an XBlock with state,
views, and input handling.

We provide a script to create a new XBlock project to help you get started.
Run bin/workbench-make-xblock in a directory where you want to create your XBlock
project.  workbench-make-xblock will prompt you for the name of the XBlock, and will
create a minimal working XBlock, ready for you to begin development.

You can provide scenarios for the workbench to display, see the thumbs.py
sample for an example, or the xblock/problem.py file.  The scenarios are
written in a simple XML language.  Note this is not an XML format we are
proposing as a standard.

Once you install your XBlock into your virtualenv, the workbench will
automatically display its scenarios for you to experiment with.

If you are interested in making an XBlock to run for your course on edx.org,
please get in touch with us as soon as possible - in the ideation and design
phase is ideal. See our `XBlock review guidelines`_
for more information (note that this is not needed for XBlocks running on your
own instance of Open edX, or released to the wider community).

.. _XBlock review guidelines: https://openedx.atlassian.net/wiki/display/OPEN/XBlock+review+guidelines


External XBlocks
----------------

We have been moving towards hosting XBlocks in external repositories, some of
which have been installed and will appear in the workbench:

ACID XBlock: https://github.com/edx/acid-block


License
-------

The code in this repository is licensed under version 3 of the AGPL unless
otherwise noted.

Please see ``LICENSE.txt`` for details.


How to Contribute
-----------------

Contributions are very welcome. The easiest way is to fork this repo, and then
make a pull request from your fork. The first time you make a pull request, you
will be asked to sign a Contributor Agreement.

Please see our `contributor's guide`_ for more information on contributing.

.. _contributor's guide: http://edx.readthedocs.org/projects/edx-developer-guide/en/latest/process/overview.html


Reporting Security Issues
-------------------------

Please do not report security issues in public. Please email security@edx.org


Mailing List and IRC Channel
----------------------------

You can discuss this code on the `edx-code Google Group`__ or in the
``#edx-code`` IRC channel on Freenode.

__ https://groups.google.com/group/edx-code

.. |build-status| image:: https://travis-ci.org/edx/xblock-sdk.svg?branch=master
   :target: https://travis-ci.org/edx/xblock-sdk
.. |coverage-status| image:: https://coveralls.io/repos/edx/xblock-sdk/badge.png
   :target: https://coveralls.io/r/edx/xblock-sdk
