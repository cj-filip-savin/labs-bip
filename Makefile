
export PROJECT 			:= $(shell egrep -m 1 -e '^name' pyproject.toml | sed -E 's/^name = "(.*)"/\1/')
export VERSION 			:= $(shell egrep -m 1 -e '^version' pyproject.toml | sed -E 's/^version = "(.*)"/\1/')
export DESCRIPTION 		:= $(shell egrep -m 1 -e '^description' pyproject.toml | sed -E 's/^description = "(.*)"/\1/')
export GIT_HASH 		:= $(shell git rev-parse --short HEAD || echo "no_git")
export PROJECT_ROOT_DIR := $(dir $(abspath $(firstword $(MAKEFILE_LIST))))
export FULL_VERSION     := $(VERSION)-$(GIT_HASH)

help:
	#
	# >>> $(PROJECT) v$(FULL_VERSION) <<< $(DESCRIPTION)
	#
	# Available make targets:
	#
	@egrep -B1 -e '### ' $(lastword $(MAKEFILE_LIST)) \
		| tr -d '\n' \
		| sed -E 's/--/\n/g' \
		| grep '###' \
		| sed -E 's/^(.*):.*###(.*)/# \1\t\2/' \
		| awk -F'\t' '{ if ($$1) { printf "%-20s - %s\n", $$1, $$2 } }'
	#

run: .venv
	### Run package
	poetry run python -m $(PROJECT)

test: .venv const-update
	### Run tests
	poetry run pytest

lint: .venv
	### Run Python code lint
	poetry run pylint $(PROJECT) tests

build: .venv const-update openapi-export
	### Build project
	poetry build

clean:
	### Clean build artifacts
	-find $(PROJECT) -type d -name '__pycache__' -exec rm -rf {} \;
	rm -rf dist

deep-clean: clean
	### Clean everything
	rm -rf .venv .pytest_cache

.venv:
	# Create Python virtual environment using Poetry
	poetry config virtualenvs.in-project true
	poetry install

const-update:
	### Update main __init__.py with data from pyproject.toml
	sed -i.bak -E \
		-e "s/^__program__ ?=.*/__program__ = \"$(PROJECT)\"/" \
		-e "s/^__version__ ?=.*/__version__ = \"$(FULL_VERSION)\"/" \
		-e "s/^__description__ ?=.*/__description__ = \"$(DESCRIPTION)\"/" $(PROJECT)/__init__.py \
		&& rm $(PROJECT)/__init__.py.bak
