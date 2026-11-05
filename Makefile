.PHONY: clean

clean:
	find . -type d \( -name .git -o -name .venv \) -prune -o -type f -name .DS_Store -exec rm -f {} +
	find . -type d \( -name .git -o -name .venv \) -prune -o -type d -name __pycache__ -prune -exec rm -rf {} +
