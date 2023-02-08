.PHONY: install uninstall version clean run test format lint

VENV=venv
PYTHON=${VENV_NAME}/bin/python3
PIP=$(VENV)/bin/pip
PROJECT=app

$(VENV)/bin/activate: requirements_dev.txt requirements_test.txt requirements.txt
	test -d $(VENV) || python3.10 -m venv $(VENV)
	touch $(VENV)/bin/activate

install: $(VENV)/bin/activate
	${PIP} install -U pip
	${PIP} install -r requirements_dev.txt

uninstall:
	rm -fr $(VENV)

version: $(VENV)/bin/activate
	${PYTHON} --version
	${PIP} freeze

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -fr .mypy_cache

run: $(VENV)/bin/activate
	$(VENV)/bin/flask --app $(PROJECT):create_app run --reload

test: $(VENV)/bin/activate
	$(VENV)/bin/pytest -vv --diff-width=60 --cov $(PROJECT)

format: $(VENV)/bin/activate
	$(VENV)/bin/black $(PROJECT)

lint/black: $(VENV)/bin/activate
	$(VENV)/bin/black --diff --check $(PROJECT)

lint/mypy: $(VENV)/bin/activate
	$(VENV)/bin/mypy --strict --implicit-reexport $(PROJECT)

lint/cohesion: $(VENV)/bin/activate
	$(VENV)/bin/cohesion -d $(PROJECT)

lint/vulture: $(VENV)/bin/activate
	$(VENV)/bin/vulture --min-confidence 70 $(PROJECT)

lint: lint/black lint/mypy lint/cohesion lint/vulture
