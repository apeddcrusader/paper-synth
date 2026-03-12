.PHONY: setup test lint format verify clean demo

setup:
	python -m pip install -e ".[dev]"

test:
	python -m pytest --tb=short -q

lint:
	python -m ruff check src/ tests/
	python -m ruff format --check src/ tests/

format:
	python -m ruff format src/ tests/
	python -m ruff check --fix src/ tests/

verify: format lint test
	@echo "All checks passed."

clean:
	rm -rf *.egg-info dist build __pycache__ .pytest_cache
