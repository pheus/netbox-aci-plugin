sources = netbox_aci_plugin scripts
NETBOX_ROOT ?= /opt/netbox

.PHONY: test format lint coverage pre-commit seed clean
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

# shell, not nbshell: only shell reads piped stdin with exec(). nbshell
# drops to code.interact(), which truncates function bodies at the first
# blank line.
seed:
	cd $(NETBOX_ROOT) && \
	python netbox/manage.py shell < $(CURDIR)/scripts/seed_demo_data.py

clean:
	rm -rf *.egg-info
	rm -rf .tox dist site htmlcov .coverage .coverage.*
