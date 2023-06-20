XBlock SDK
#############################

.. note::

  This README was auto-generated. Maintainer: please review its contents and
  update all relevant sections. Instructions to you are marked with
  "PLACEHOLDER" or "TODO". Update or remove those sections, and remove this
  note when you are done.

|pypi-badge| |ci-badge| |codecov-badge| |doc-badge| |pyversions-badge|
|license-badge| |status-badge|

Purpose
*******

This repository consists of three main components to assist in the creation of new XBlocks:

* a template-based generator for new XBlocks (found in the ``prototype`` directory)

* sample XBlocks that can be the basis for new XBlock work (found in the ``sample_xblocks`` directory)

* Workbench runtime, a simple runtime for viewing and testing XBlocks in a browser (found in the ``workbench`` directory)

Getting Started
***************

Developing
==========

This code runs on Python 3.8 or newer.

One Time Setup
--------------
.. code-block::

  # Clone the repository
  git clone git@github.com:openedx/xblock-sdk.git
  cd xblock-sdk

  # Set up a virtualenv with the same name as the repo and activate it
  # Here's how you might do that if you have virtualenvwrapper setup.
  mkvirtualenv -p python3.8 xblock-sdk

  # Install system requirements needed to run this on ubuntu.
  # Note: Debian 10 needs libjpeg62-turbo-dev instead of libjpeg62-dev.
  sudo apt-get install python-dev libxml2-dev libxslt-dev lib32z1-dev libjpeg62-dev

Every time you develop something in this repo
---------------------------------------------

Locally
~~~~~~~

#.  Install the requirements and register the XBlock entry points::

    $ make install

#.  Run the Django development server::

    $ python manage.py runserver

#.  Open a web browser to: http://127.0.0.1:8000

Docker
~~~~~~

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
~~~~~~~

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


Deploying
=========

This repository is deployed to PyPI.  To deploy a new version.

#. Bump the version of the package in ``workbench/__init__.py``

#. Make a new release in github or push a new tag up to Github.

The pypi-publish github action should trigger.  It will build and deploy the source and wheel package to PyPI.

Getting Help
************

Documentation
=============

Start by going through `the documentation`_.  If you need more help see below.

.. _the documentation: https://edx.readthedocs.io/projects/xblock-tutorial/en/latest/sdk/get_started_sdk.html

More Help
=========

If you're having trouble, we have discussion forums at
https://discuss.openedx.org where you can connect with others in the
community.

Our real-time conversations are on Slack. You can request a `Slack
invitation`_, then join our `community Slack workspace`_.

For anything non-trivial, the best path is to open an issue in this
repository with as many details about the issue you are facing as you
can provide.

https://github.com/openedx/xblock-sdk/issues

For more information about these options, see the `Getting Help`_ page.

.. _Slack invitation: https://openedx.org/slack
.. _community Slack workspace: https://openedx.slack.com/
.. _Getting Help: https://openedx.org/getting-help

License
*******

The code in this repository is licensed under the APACHE 2.0 license unless
otherwise noted.

Please see `LICENSE.txt <LICENSE.txt>`_ for details.

Contributing
************

Contributions are very welcome.
Please read `How To Contribute <https://openedx.org/r/how-to-contribute>`_ for details.

This project is currently accepting all types of contributions, bug fixes,
security fixes, maintenance work, or new features.  However, please make sure
to have a discussion about your new feature idea with the maintainers prior to
beginning development to maximize the chances of your change being accepted.
You can start a conversation by creating a new issue on this repo summarizing
your idea.

The Open edX Code of Conduct
****************************

All community members are expected to follow the `Open edX Code of Conduct`_.

.. _Open edX Code of Conduct: https://openedx.org/code-of-conduct/

People
******

The assigned maintainers for this component and other project details may be
found in `Backstage`_. Backstage pulls this data from the ``catalog-info.yaml``
file in this repo.

.. _Backstage: https://backstage.openedx.org/catalog/default/component/xblock-sdk

Reporting Security Issues
*************************

Please do not report security issues in public. Please email security@openedx.org.

.. |pypi-badge| image:: https://img.shields.io/pypi/v/xblock-sdk.svg
    :target: https://pypi.python.org/pypi/xblock-sdk/
    :alt: PyPI

.. |ci-badge| image:: https://github.com/openedx/xblock-sdk/workflows/Python%20CI/badge.svg?branch=main
    :target: https://github.com/openedx/xblock-sdk/actions
    :alt: CI

.. |codecov-badge| image:: https://codecov.io/github/openedx/xblock-sdk/coverage.svg?branch=main
    :target: https://codecov.io/github/openedx/xblock-sdk?branch=main
    :alt: Codecov

.. |doc-badge| image:: https://readthedocs.org/projects/xblock-sdk/badge/?version=latest
    :target: https://docs.openedx.org/projects/xblock-sdk
    :alt: Documentation

.. |pyversions-badge| image:: https://img.shields.io/pypi/pyversions/xblock-sdk.svg
    :target: https://pypi.python.org/pypi/xblock-sdk/
    :alt: Supported Python versions

.. |license-badge| image:: https://img.shields.io/github/license/openedx/xblock-sdk.svg
    :target: https://github.com/openedx/xblock-sdk/blob/main/LICENSE.txt
    :alt: License

.. |status-badge| image:: https://img.shields.io/badge/Status-Maintained-brightgreen



Other Documentation
*******************

Using the workbench
===================

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
======================

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
===============

Included in this repository are some example XBlocks that demonstrate how to use
various aspects of the XBlock SDK. You can see a more detailed description of
those examples in `the README`_ located in that repository:

There is a rich community of XBlock developers that have put together a large
number of XBlocks that have been used in various contexts, mostly on the edx-platform.
You can see examples of what that community has done in the `edx-platform wiki`_.

.. _the README: https://github.com/openedx/xblock-sdk/blob/master/sample_xblocks/README.rst
.. _edx-platform wiki: https://openedx.atlassian.net/wiki/spaces/COMM/pages/43385346/XBlocks+Directory
