===============
Getting Started
===============

We intend for XBlock-SDK to contain two main components: The simple workbench for previewing and working
on new XBlocks and some sample XBlocks that can be used as examples for other XBlocks that you may wish to author.

Prerequisites
-------------

You'll need some software installed in order to work with XBlock SDK:

Python 2.7

    Chances are good that you already have Python 2.7 installed.  If you need
    to install it, you can get a kit from `python.org`__.   Do not install the
    highest version you find.  Python 3.x will not work.  You want Python 2.7.

.. __: http://python.org/download/

Pip

    Python's package manager is called pip, with its own `installation
    instructions`__.

.. __: http://www.pip-installer.org/en/latest/installing.html

Git

    Git manages code repositories.  Github has a good `introduction to setting
    up git`__ if you need one.

.. __: https://help.github.com/articles/set-up-git



Get the XBlock-SDK repository
-------------------------

.. highlight: console

The XBlock code is on Github.  Get the code by cloning the XBlock-SDK repo::

    $ git clone https://github.com/edx/xblock-sdk.git

This will create the XBlock-SDK directory in your current directory.

In the XBlock-SDK directory, install its prerequisite Python packages::

    $ pip install -r requirements.txt

.. note::
    This will also install the latest version of XBlock.


Create a new XBlock
-------------------

.. highlight: console

The simplest way to get started on a new XBlock is to use the
script/startnew.py script in the XBlock repo.  Make a directory for your
development work, outside the XBlock directory, let's call it ``~/edxwork``,
and run the startnew.py script from there::

    $ cd ~
    $ mkdir edxwork
    $ cd edxwork
    $ /path/to/XBlock/script/startnew.py

The script will need two pieces of information, both related to the name of
your XBlock:  a short name that can be used for directory names, and a Python
class name.  You might choose "myxblock" for the short name and "MyXBlock" for
the class name.  We'll use those names in the rest of these instructions.  Your
files will be named using the actual name you gave.

When the script is done, you'll have a myxblock directory with a complete
working XBlock.  Of course, it's just the boilerplate for your XBlock, now you
have to start writing your code.

.. highlight: python

Most of your work will be in the myxblock/myxblock/myxblock.py file, which
contains the MyXBlock class.  There are "TO-DO" comments in the file indicating
where you should make changes::

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        etc...


For more details about the details of writing an XBlock, please refer to the
XBlock documentation: https://xblock.readthedocs.org/en/latest/getting_started.html#write-your-xblock

Testing your XBlock in the XBlock-SDK 
--------------------------------------

.. highlight: console

It's important to thoroughly test your XBlock to be sure that it does what you
want and that it works properly in the environments you need.

To run your XBlock in the SDK, you'll need to install it.  Using pip, you can
install your XBlock so that your working tree (the code you are editing) is the
installed version.  The makes it easy to change the code and see the changes
running without a cumbersome edit-install-run cycle.

Use pip to install your block::

    $ cd ~/edxwork
    $ pip install -e myxblock

Testing with the workbench
..........................

The simplest test environment is the XBlock workbench.  Once you've installed
your XBlock in the SDK, the workbench will display whatever scenarios you've defined in
your `workbench_scenarios` method.

Running the workbench
.....................

To run the workbench, go to the top-level directory and type::

    $ ./manage.py runserver

This will automatically start the workbench on port 8000. If you visit the page::

    http://localhost:8000

the workbench should be visible along with the `workbench_scenarios` of any installed XBlocks. 
