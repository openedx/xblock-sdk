===========================================
XBlock SDK |build-status| |coverage-status|
===========================================

This repository consists of three main components to assist in the creation of new XBlocks:

* a template-based generator for new XBlocks (found in the ``prototype`` directory)

* sample XBlocks that can be the basis for new XBlock work (found in the ``sample_xblocks`` directory)

* Workbench runtime, a simple runtime for viewing and testing XBlocks in a browser (found in the ``workbench`` directory)


Installation
------------

This code runs on Python 3.5 or newer.

#.  Install standard development libraries. Here's how you do it on Ubuntu or Debian::

    $ sudo apt-get install python-dev libxml2-dev libxslt-dev lib32z1-dev libjpeg62-dev

    Note: Debian 10 needs libjpeg62-turbo-dev instead of libjpeg62-dev.

#.  Get a local copy of this repo.

#.  Create and activate a virtualenv to work in.

#.  Install the requirements and register the XBlock entry points::

    $ make install

#.  Run the Django development server::

    $ python manage.py runserver

#.  Open a web browser to: http://127.0.0.1:8000

Docker
------

Alternatively, you can build and run the xblock-sdk in Docker (we are using docker-compose which
can be installed as explained at https://docs.docker.com/compose/install/)

After cloning this repository locally, go into the repository directory and build the Docker image::

    $ make docker_build

or manually run

    $ docker-compose build

You can then run the locally-built version using the following command::

    $ make dev.up

or manually run::

    $ docker-compose up -d

and stop the container (without removing data) by::

    $ make dev.stop

or manually run::

    $ docker-compose stop

Note, using::

    $ make dev.down

or::

    $ docker-compose down

will shut down the container and delete non-persistant data.

On the first startup run the following command to create the SQLite database.
(Otherwise you will get an error no such table: workbench_xblockstate.)

Command::

    $ docker container exec -it edx.devstack.xblock-sdk python3.8 manage.py migrate

You should now be able to access the XBlock SDK environment in your browser at http://localhost:8000

You can open a bash shell in the running container by using::

    $ make app-shell

or::

    $ docker container exec -it edx.devstack.xblock-sdk bash

Testing
--------

If using Docker, all these commands need to be run inside the xblock-sdk container.

Testing is done via tox to test all supported versions:

#.  Create and activate a virtualenv to work in.

#.  Run just unit tests via tox::

    $ tox

For each supported version of Django (currently 1.8 and 1.11) this will run:

* Integration tests of XBlocks running within the workbench.
* Individual tests written for the demo XBlocks

To run the unit tests in your virtualenv you can use::

    $ make test


To run all tox unit tests and quality checks::

    $ make test-all


To run just the quality checks::

    $ make quality

You can test XBlocks through a browser using `Selenium`_. We have included an
example Selenium test for ``thumbs`` that uses Django's `LiveServerTestCase`_.
It runs as part of the test suite as executed by the above command.

.. _Selenium: http://docs.seleniumhq.org/
.. _LiveServerTestCase: https://docs.djangoproject.com/en/1.11/topics/testing/tools/#django.test.LiveServerTestCase

To update and view test coverage::

    $ make coverage

See the `coverage.py`_ docs for more info and options.

.. _coverage.py: http://coverage.readthedocs.org/


Using the workbench
-------------------

When you open the workbench, you'll see a list of sample XBlock configurations
(scenarios).  Each will display a page showing the XBlocks composited together,
along with internal information like the "database" contents.

The workbench database defaults to a sqlite3 database. If you're using devstack,
you may want to set ``WORKBENCH_DATABASES`` to point to your MySQL db.

If you want to experiment with different students, you can use a URL parameter
to set the student ID, which defaults to 1::

    http://127.0.0.1:8000/?student=17

Different students will see different student state, for example, while seeing
the same content.  The default student ID contains only digits but it is not
necessary to limit student IDs to digits. Student IDs are represented as
strings.


Making your own XBlock
----------------------

Making an XBlock involves creating a Python class that conforms to the XBlock
specification. See the ``sample_xblocks`` directory for examples and
`the XBlock tutorial`_ for a full walk-through.

.. _the XBlock tutorial: http://edx.readthedocs.org/projects/xblock-tutorial

We provide a script to create a new XBlock project to help you get started.
Run ``bin/workbench-make-xblock`` in a directory where you want to create your XBlock
project.  The script will prompt you for the name of the XBlock, and will
create a minimal working XBlock, ready for you to begin development.

You can provide scenarios for the workbench to display: see the ``thumbs.py``
sample for an example, or the ``xblock/problem.py`` file.  The scenarios are
written in a simple XML language.  Note this is not an XML format we are
proposing as a standard.

Once you install your XBlock into your virtualenv, the workbench will
automatically display its scenarios for you to experiment with.

If you are interested in making an XBlock to run for your course on edx.org,
please get in touch with us as soon as possible -- in the ideation and design
phase is ideal. See our `XBlock review guidelines`_
for more information (note that this is not needed for XBlocks running on your
own instance of Open edX, or released to the wider community).

.. _XBlock review guidelines: https://openedx.atlassian.net/wiki/display/OPEN/XBlock+review+guidelines


Example XBlocks
---------------

Included in this repository are some example XBlocks that demonstrate how to use
various aspects of the XBlock SDK. You can see a more detailed description of
those examples in `the README`_ located in that repository:

There is a rich community of XBlock developers that have put together a large
number of XBlocks that have been used in various contexts, mostly on the edx-platform.
You can see examples of what that community has done in the `edx-platform wiki`_.

.. _the README: https://github.com/openedx/xblock-sdk/blob/master/sample_xblocks/README.rst
.. _edx-platform wiki: https://openedx.atlassian.net/wiki/spaces/COMM/pages/43385346/XBlocks+Directory


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

.. |build-status| image:: https://github.com/openedx/xblock-sdk/workflows/Python%20CI/badge.svg?branch=master
:target: https://github.com/openedx/xblock-sdk/actions?query=workflow%3A%22Python+CI%22
.. |coverage-status| image:: https://coveralls.io/repos/edx/xblock-sdk/badge.png
   :target: https://coveralls.io/r/edx/xblock-sdk
