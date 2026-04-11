.PHONY: download convert build clean all detect fix-broken

PYTHON = python3
PIP = pip3
HUGO = hugo
VENV = .venv
VENV_PYTHON = $(VENV)/bin/python
VENV_PIP = $(VENV)/bin/pip

all: venv download convert build

# Setup virtual environment and install dependencies
venv: $(VENV)/bin/activate

$(VENV)/bin/activate: requirements.txt
	@echo "Setting up virtual environment..."
	$(PYTHON) -m venv $(VENV)
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements.txt
	@touch $(VENV)/bin/activate

# Download raw HTML stories
download: venv
	@echo "Downloading raw HTML stories..."
	$(VENV_PYTHON) download_stories.py

# Convert raw HTML stories into Markdown for the website
convert: venv
	@echo "Converting stories to website format..."
	$(VENV_PYTHON) convert_to_markdown.py

# Build the website using Hugo and create a deployable archive
build:
	@echo "Building website..."
	cd website && $(HUGO)
	@echo "Creating archive..."
	tar -czf website-archive.tar.gz -C website/public .

# Clean up generated files (but keep the raw HTML stories)
clean:
	@echo "Cleaning up..."
	rm -rf $(VENV)
	rm -rf website/public
	rm -rf website/resources
	rm -f website-archive.tar.gz
	# rm -rf website/content/stories/*.md

# Detect stories with broken markdown
detect: venv
	@echo "Detecting broken markdown in converted stories..."
	$(VENV_PYTHON) detect_broken_markdown.py

# Detect and delete converted stories with broken markdown (so they can be re-converted)
fix-broken: venv
	@echo "Fixing broken markdown (deleting converted files)..."
	$(VENV_PYTHON) detect_broken_markdown.py --delete --force
