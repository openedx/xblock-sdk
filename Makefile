all: install test

install:
	# TODO: we need to install requirements.txt so XBlock is installed
	# from a GitHub repo.  Once XBlock is available through PyPi,
	# we can install all requirements using setup.py
	pip install -r requirements.txt
	pip install -e .
	pip install -r test-requirements.txt

test:
	python manage.py test