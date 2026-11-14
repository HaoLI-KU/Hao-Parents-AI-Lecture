PYTHON ?= python3
.PHONY: all build check serve clean

all: build check

build:
	$(PYTHON) site/build.py

check:
	$(PYTHON) site/check_site.py

serve:
	$(PYTHON) -m http.server 8000 --directory docs

clean:
	find . -type d \( -name .git -o -name .venv \) -prune -o -type f -name .DS_Store -exec rm -f {} +
	find . -type d \( -name .git -o -name .venv \) -prune -o -type d -name __pycache__ -prune -exec rm -rf {} +
