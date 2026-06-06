sources = netbox_aci_plugin
NETBOX_ROOT ?= /opt/netbox

.PHONY: test format lint coverage pre-commit clean
test: format lint coverage

format:
	ruff format $(sources)

lint:
	ruff check $(sources)

coverage:
	cd $(NETBOX_ROOT) && \
	export COVERAGE_RCFILE=$(CURDIR)/pyproject.toml && \
	coverage run netbox/manage.py test netbox_aci_plugin.tests -v 2 && \
	coverage combine && \
	coverage report && \
	coverage html

pre-commit:
	pre-commit run --all-files

clean:
	rm -rf *.egg-info
	rm -rf .tox dist site htmlcov .coverage .coverage.*
