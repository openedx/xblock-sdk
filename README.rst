XBlock SDK
==========

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

        $ pip install -r requirements.txt

4. Create and sync the sqllite DB

        $ python manage.py syncdb

4.  Run the Django development server:

        $ python manage.py runserver

5.  Open a web browser to: http://127.0.0.1:8000

Testing
--------

To run the test suite:

    $ python manage.py test

This will run:

    * Integration tests of XBlocks running within the workbench.
    * Individual tests written for the demo XBlocks

You can test XBlocks through a browser using `Selenium`_. We have included an
example Selenium test for ``thumbs`` that uses Django's `LiveServerTestCase`_.
It runs as part of the test suite as executed by the above command. You need to
have Firefox installed for this test case to run successfully.

.. _Selenium: http://docs.seleniumhq.org/
.. _LiveServerTestCase: https://docs.djangoproject.com/en/1.4/topics/testing/#django.test.LiveServerTestCase

To run the test suite under coverage:

    $ coverage run manage.py test

to execute the tests. Then to view the coverage report:

    $ coverage report

See the `coverage.py`_ docs for more info and options.

.. _coverage.py: http://nedbatchelder.com/code/coverage/


License
-------

The code in this repository is licensed under version 3 of the AGPL unless
otherwise noted.

Please see ``LICENSE.txt`` for details.


How to Contribute
-----------------

Contributions are very welcome. The easiest way is to fork this repo, and then
make a pull request from your fork. The first time you make a pull request, you
may be asked to sign a Contributor Agreement.


Reporting Security Issues
-------------------------

Please do not report security issues in public. Please email security@edx.org


Mailing List and IRC Channel
----------------------------

You can discuss this code on the `edx-code Google Group`__ or in the
``#edx-code`` IRC channel on Freenode.

__ https://groups.google.com/group/edx-code
