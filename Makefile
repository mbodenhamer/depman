all: test

VERSION = `./metadata depman/metadata.yml version`

PACKAGE = depman
IMAGE = mbodenhamer/${PACKAGE}-dev
PYDEV = docker run --rm -it -e BE_UID=`id -u` -e BE_GID=`id -g` \
	-v /var/run/docker.sock:/var/run/docker.sock \
	-v $(CURDIR):/app $(IMAGE)
VERSIONS = 2.7.14,3.6.2

#-------------------------------------------------------------------------------
# Docker image management

docker-build:
	@docker build -t $(IMAGE):latest --build-arg versions=$(VERSIONS) .

docker-first-build:
	@docker build -t $(IMAGE):latest --build-arg versions=$(VERSIONS) \
	--build-arg reqs=requirements.yml .
	@$(PYDEV) depman export dev -t pip -o dev-requirements.in --no-header
	@$(PYDEV) depman export prod -t pip -o requirements.in --no-header
	@$(PYDEV) pip-compile dev-requirements.in
	@$(PYDEV) pip-compile requirements.in

docker-rmi:
	@docker rmi $(IMAGE)

docker-push:
	@docker push ${IMAGE}:latest

docker-pull:
	@docker pull ${IMAGE}:latest

docker-shell:
	@$(PYDEV) bash

.PHONY: docker-build docker-first-build docker-rmi docker-shell
#-------------------------------------------------------------------------------
# Build management

check:
	@$(PYDEV) check-manifest

build: check
	@$(PYDEV) python setup.py sdist bdist_wheel

.PHONY: check build
#-------------------------------------------------------------------------------
# Documentation

docs:
	@$(PYDEV) sphinx-apidoc -f -o docs/ depman/ $$(find depman -name tests)	
	@$(PYDEV) make -C docs html

view:
	@python -c "import webbrowser as wb; \
	wb.open('docs/_build/html/index.html')"

.PHONY: docs view
#-------------------------------------------------------------------------------
# Dependency management

pip-compile:
	@$(PYDEV) pip-compile dev-requirements.in
	@$(PYDEV) pip-compile requirements.in

print-version:
	@echo $(VERSION)

.PHONY: pip-compile
#-------------------------------------------------------------------------------
# Tests

PY36 = source .tox/py36/bin/activate
TEST = nosetests -s -v --pdb --pdb-failures
UNIT_TEST = $(TEST) -w $(PACKAGE)/
INSTALL = pip install .

test:
	@$(PYDEV) coverage erase
	@$(PYDEV) tox
	@$(PYDEV) coverage html

unit-test:
	@$(PYDEV) bash -c "$(UNIT_TEST)"

py3-unit-test:
	@$(PYDEV) bash -c "$(PY36); $(UNIT_TEST)"

quick-test:
	@$(PYDEV) bash -c "$(INSTALL); $(TEST)"

py3-quick-test:
	@$(PYDEV) bash -c "$(PY36); $(INSTALL); $(TEST)"

dist-test: build
	@$(PYDEV) dist-test $(VERSION)

show:
	@python -c "import webbrowser as wb; wb.open('htmlcov/index.html')"

.PHONY: test quick-test dist-test show unit-test py3-unit-test py3-quick-test
#-------------------------------------------------------------------------------
# Cleanup

clean:
	@$(PYDEV) fmap -r ${PACKAGE} 'rm -f' '*.py[co]'
	@$(PYDEV) fmap -r ${PACKAGE} -d rmdir __pycache__
	@$(PYDEV) fmap -r tests 'rm -f' '*.py[co]'
	@$(PYDEV) fmap -r tests -d rmdir __pycache__
	@$(PYDEV) make -C docs clean

.PHONY: clean
#-------------------------------------------------------------------------------
