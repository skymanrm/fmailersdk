.PHONY: help test test-sync test-async test-specific install clean build publish-test publish

# Python and PYTHONPATH configuration
PYTHON := python
# `src` first, so the suite tests this working tree. It used to name one
# developer's home directory, which exists nowhere else — so everywhere else
# the tests silently imported whatever `postwing` was installed in the
# environment and passed against code that was not in this repo.
PYTHONPATH := src:$$PYTHONPATH
VENV := .venv
VENV_PYTHON := $(VENV)/bin/python

help:
	@echo "Available targets:"
	@echo "  make test              - Run all tests"
	@echo "  make test-sync         - Run synchronous tests only"
	@echo "  make test-async        - Run asynchronous tests only"
	@echo "  make test-specific TEST=<test_name> - Run specific test"
	@echo "  make install           - Install dependencies"
	@echo "  make build             - Build package for distribution"
	@echo "  make publish-test      - Publish to TestPyPI"
	@echo "  make publish           - Publish to PyPI"
	@echo "  make clean             - Clean build artifacts"

test:
	@echo "Running all tests..."
	@PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s tests

test-sync:
	@echo "Running synchronous tests..."
	@PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest tests.test_sdk.PostwingTestUtils

test-async:
	@echo "Running asynchronous tests..."
	@PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest tests.test_sdk.PostwingAsyncTestUtils

test-specific:
	@if [ -z "$(TEST)" ]; then \
		echo "Error: TEST variable not set. Usage: make test-specific TEST=tests.test_sdk.PostwingAsyncTestUtils.test_send_simple_async_success"; \
		exit 1; \
	fi
	@echo "Running specific test: $(TEST)"
	@PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest $(TEST)

install:
	@echo "Installing dependencies..."
	@pip install -r requirements.txt

build:
	@echo "Building package..."
	@python -m build

publish-test:
	@echo "Checking distribution..."
	@twine check dist/*
	@echo "Publishing to TestPyPI..."
	@twine upload --repository testpypi dist/*

publish:
	@echo "Checking distribution..."
	@twine check dist/*
	@echo "Publishing to PyPI..."
	@twine upload dist/*

clean:
	@echo "Cleaning build artifacts..."
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@echo "Clean complete!"
