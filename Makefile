.PHONY: parse convert build clean all

PYTHON = python3
PIP = pip3
HUGO = hugo
VENV = .venv
VENV_PYTHON = $(VENV)/bin/python
VENV_PIP = $(VENV)/bin/pip

all: venv parse convert build

# Setup virtual environment and install dependencies
venv: $(VENV)/bin/activate

$(VENV)/bin/activate: requirements.txt
	@echo "Setting up virtual environment..."
	$(PYTHON) -m venv $(VENV)
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements.txt
	@touch $(VENV)/bin/activate

# Parse only stories that have not been parsed before
parse: venv
	@echo "Parsing new stories..."
	$(VENV_PYTHON) parse_stories.py

# Convert parsed stories into the proper format for the website
convert: venv
	@echo "Converting stories to website format..."
	$(VENV_PYTHON) convert_stories.py

# Build the website using Hugo
build:
	@echo "Building website..."
	cd website && $(HUGO)

# Clean up generated files (but keep the raw parsed stories)
clean:
	@echo "Cleaning up..."
	rm -rf $(VENV)
	rm -rf website/public
	rm -rf website/resources
	# Not removing website/content/stories as they are needed for build,
	# but they can be regenerated with 'make convert'
	# rm -rf website/content/stories/*.md
