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
	pip install -r requirements/base.txt
	pip install -e .
	pip install -r requirements/test.txt

var:
	mkdir var || true

$(SQLITE_DB): var
	# The --noinput flag is for non-interactive runs, e.g. TravisCI.
	python manage.py syncdb --noinput

.PHONY: test
test:
	python manage.py test

.PHONY: quality
quality:
	pep8
	pylint workbench/ sample_xblocks/ setup.py

.PHONY: cover
cover:
	coverage run manage.py test
	coverage report

clean:
	rm -f workbench.log* workbench.test.*
	rm -rf workbench/static/djpyfs
	rm -rf *.egg-info
	rm -f .coverage
	find . -name '.git' -prune -o -name '*.pyc' -exec rm {} \;
