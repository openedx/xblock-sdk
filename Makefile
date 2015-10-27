#!/usr/bin/make -f

# Commands
APT_GET=apt-get -y
CP=cp
HOSTNAME=hostname
INSTALL_PACKAGE=$(APT_GET) install
# Files
SQLITE_DB=var/workbench.db
# Packages
LIBS_BUILD=build-essential
LIBS_PYTHON=python python-dev python-distribute python-pip
LIBS_LIBXML=libxml2-dev libxslt1-dev zlib1g-dev
LIBS_SOURCE_CONTROL=git
# Variables
HOST_PORT=8008
HOST_ADDRESS=0
HOSTNAME_VALUE=workbench
SUPERVISOR_CONF=supervisor.conf  # Comment-out to disable
SUPERVISOR_CTL=supervisorctl

all: install
	$(MAKE) run

.PHONY: provision
provision:
	$(HOSTNAME) "$(HOSTNAME_VALUE)"
	echo "$(HOSTNAME_VALUE)" > /etc/hostname
	$(APT_GET) update
	$(APT_GET) upgrade
	$(INSTALL_PACKAGE) apt-transport-https
	$(INSTALL_PACKAGE) $(LIBS_SOURCE_CONTROL)
	$(INSTALL_PACKAGE) $(LIBS_BUILD)
	$(INSTALL_PACKAGE) $(LIBS_PYTHON)
	$(INSTALL_PACKAGE) $(LIBS_LIBXML)
ifdef SUPERVISOR_CONF
	$(INSTALL_PACKAGE) supervisor
	$(CP) $(SUPERVISOR_CONF) /etc/supervisor/conf.d/workbench.conf
	$(SUPERVISOR_CTL) reread
	$(SUPERVISOR_CTL) update
endif
	$(MAKE) install

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
test: install
	python manage.py test

.PHONY: quality
quality:
	pep8
	pylint workbench/ sample_xblocks/ setup.py

.PHONY: cover
cover:
	coverage run manage.py test
	coverage report

run:
	python ./manage.py runserver $(HOST_ADDRESS):$(HOST_PORT)
