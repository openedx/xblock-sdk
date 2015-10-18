#!/usr/bin/make -f

SQLITE_DB=var/workbench.db

all: install test

.PHONY: install
install: pip $(SQLITE_DB)

.PHONY: pip
pip:
	# TODO: we need to install requirements.txt so XBlock is installed
	# from a GitHub repo.  Once XBlock is available through PyPi,
	# we can install all requirements using setup.py
	pip install -r requirements.txt
	pip install -e .
	pip install -r test-requirements.txt

var:
	mkdir var || true

$(SQLITE_DB): var
	# The --noinput flag is for non-interactive runs, e.g. TravisCI.
	python manage.py syncdb --noinput

test:
	python manage.py test

.PHONY: quality
quality:
	pep8
	pylint workbench/ sample_xblocks/ setup.py

cover:
	coverage run manage.py test
	coverage report
