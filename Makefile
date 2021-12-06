.DEFAULT_GOAL := test
isort = isort --skip tests/assets src docs/examples tests setup.py
black = black --exclude assets --target-version py37 src docs/examples tests setup.py

.PHONY: install
install:
	python -m pip install -U setuptools pip pip-tools
	python -m piptools sync requirements.txt requirements-dev.txt docs/requirements.txt
	pip install -e .
	pre-commit install

# An environment setup that requires linux+docker and does not require the particular python version to be available.
.PHONY: install-docker
install-docker:
	docker run --rm -it -v "$(pwd):/code" --user "$(id -u)" --workdir /code -e HOME=/code python:3.7 bash -c "rm -rf env && python3.7 -m venv env && . ./env/bin/activate && make install && bash"

.PHONY: update
update:
	@echo "-------------------------"
	@echo "- Updating dependencies -"
	@echo "-------------------------"

  # Sync your virtualenv with the expected state
	python -m piptools sync requirements.txt requirements-dev.txt docs/requirements.txt

	pip install -U pip

	rm requirements.txt
	touch requirements.txt
	pip-compile -Ur --allow-unsafe

	rm docs/requirements.txt
	touch docs/requirements.txt
	pip-compile -Ur --allow-unsafe docs/requirements.in --output-file docs/requirements.txt

	rm requirements-dev.txt
	touch requirements-dev.txt
	pip-compile -Ur --allow-unsafe requirements-dev.in --output-file requirements-dev.txt

  # Sync your virtualenv with the new state
	python -m piptools sync requirements.txt requirements-dev.txt docs/requirements.txt

	pip install -e .

	@echo ""

.PHONY: format
format:
	@echo "----------------------"
	@echo "- Formating the code -"
	@echo "----------------------"

	$(isort)
	$(black)

	@echo ""

.PHONY: lint
lint:
	@echo "--------------------"
	@echo "- Testing the lint -"
	@echo "--------------------"

	flakehell lint --exclude assets src/ tests/ setup.py
	$(isort) --check-only --df
	$(black) --check --diff

	@echo ""

.PHONY: mypy
mypy:
	@echo "----------------"
	@echo "- Testing mypy -"
	@echo "----------------"

	mypy src

	@echo ""

.PHONY: test
test: test-code test-examples

.PHONY: test-code
test-code:
	@echo "----------------"
	@echo "- Testing code -"
	@echo "----------------"

	pytest --cov-report term-missing --cov src tests ${ARGS}

	@echo ""

.PHONY: test-examples
test-examples:
	@echo "--------------------"
	@echo "- Testing examples -"
	@echo "--------------------"

	@find docs/examples -type f -name '*.py' | xargs -I'{}' sh -c 'python {} >/dev/null 2>&1 || (echo "{} failed" ; exit 1)'

	@echo ""

.PHONY: all
all: lint mypy test security

.PHONY: clean
clean:
	@echo "---------------------------"
	@echo "- Cleaning unwanted files -"
	@echo "---------------------------"

	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*.rej' `
	rm -rf `find . -type d -name '*.egg-info' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -rf .cache
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -f .coverage
	rm -f .coverage.*
	rm -rf build
	rm -rf dist
	rm -f src/*.c pydantic/*.so
	python setup.py clean
	rm -rf site
	rm -rf docs/_build
	rm -rf docs/.changelog.md docs/.version.md docs/.tmp_schema_mappings.html
	rm -rf codecov.sh
	rm -rf coverage.xml

	@echo ""

.PHONY: docs
docs: test-examples
	@echo "-------------------------"
	@echo "- Serving documentation -"
	@echo "-------------------------"

	mkdocs serve

	@echo ""

.PHONY: bump
bump: pull-master bump-version build-package upload-pypi clean

.PHONY: pull-master
pull-master:
	@echo "------------------------"
	@echo "- Updating repository  -"
	@echo "------------------------"

	git checkout master
	git pull

	@echo ""

.PHONY: build-package
build-package: clean
	@echo "------------------------"
	@echo "- Building the package -"
	@echo "------------------------"

	python setup.py -q bdist_wheel
	python setup.py -q sdist

	@echo ""

.PHONY: build-docs
build-docs: test-examples
	@echo "--------------------------"
	@echo "- Building documentation -"
	@echo "--------------------------"

	mkdocs build

	@echo ""

.PHONY: upload-pypi
upload-pypi:
	@echo "-----------------------------"
	@echo "- Uploading package to pypi -"
	@echo "-----------------------------"

	twine upload -r pypi dist/*

	@echo ""

.PHONY: upload-testing-pypi
upload-testing-pypi:
	@echo "-------------------------------------"
	@echo "- Uploading package to pypi testing -"
	@echo "-------------------------------------"

	twine upload -r testpypi dist/*

	@echo ""

.PHONY: bump-version
bump-version:
	@echo "---------------------------"
	@echo "- Bumping program version -"
	@echo "---------------------------"

	cz bump --changelog --no-verify
	git push --tags
	git push

	@echo ""

.PHONY: version
version:
	@python -c "import repository_pattern.version; print(repository_pattern.version.version_info())"

.PHONY: security
security:
	@echo "--------------------"
	@echo "- Testing security -"
	@echo "--------------------"

	safety check
	@echo ""
	bandit -r src

	@echo ""

.PHONY: release
release:
	@echo "----------------------"
	@echo "- Generating Release -"
	@echo "----------------------"

	cz bump --changelog

	@echo ""
