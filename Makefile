sources = netbox_aci_plugin

.PHONY: test format lint unittest pre-commit clean
test: format lint unittest

format:
	ruff format $(sources) tests

lint:
	ruff check $(sources) tests

pre-commit:
	pre-commit run --all-files

clean:
	rm -rf *.egg-info
	rm -rf .tox dist site
