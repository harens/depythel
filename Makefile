.PHONY: docs  # The docs directory already exists
all: format test

POETRY_CMD:=rp  # Relaxed poetry
CMD:=$(POETRY_CMD) run python -m

format: ## Runs black and isort
	$(CMD) isort .
	$(CMD) black .

test: pytest type-checking lint dependencies  ## Runs all available tests (pytest, type checking, etc.)

pytest:  ## Runs pytest on the tests folder and outputs coverage.xml
	$(CMD) pytest --cov-report=xml:coverage.xml --cov=depythel_api/depythel --cov=depythel_clt depythel_api/tests tests

install-pytest:
	$(CMD) pip install pytest pytest-cov pytest-mock

type-checking:  ## Runs mypy --strict
	$(CMD) mypy --strict depythel_api depythel_clt tests

install-type-checking:  # pytest required for mypy of test files
	$(CMD) pip install mypy pytest pytest-mock

dependencies:  ## Verifies pyproject.toml file integrity
	$(POETRY_CMD) check
	$(CMD) pip check

install-dependencies:
	@:

lint:  ## Tests whether formatting meets standards
	$(CMD) black --check .
	$(CMD) isort --check-only .
	$(CMD) pydocstyle --convention=google .

install-lint:
	$(CMD) pip install black isort pydocstyle
