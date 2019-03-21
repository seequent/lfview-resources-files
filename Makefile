ORG=seequent
APP=lfview-resources-files
MODULE=lfview

.PHONY: local-install local-docs docs-pages graphs \
	build build27 docs tests tests27 \
	lint-yapf lint-pylint publish

local-install:
	pip install -e .

local-docs:
	pip install -e .[docs]
	cd docs && make clean && make html

docs-pages:
	if [ -f "docs/index.rst" ]; then \
	    rm docs/index.rst; \
	fi
	if [ -d "docs/content" ]; then \
		rm -r docs/content; \
	fi
	mkdir docs/content
	if [ -d "docs/images" ]; then \
		rm -r docs/images; \
	fi
	mkdir docs/images
	cp docs/scripts/build_docs.py . && python build_docs.py && rm build_docs.py
	cd docs && make clean && make html

graphs:
	pyreverse -my -A -o pdf -p $(MODULE) $(MODULE)/**.py $(MODULE)/**/**.py

build:
	docker build -t $(ORG)/$(APP):latest -f Dockerfile .

build27:
	docker build -t $(ORG)/$(APP):latest27 -f Dockerfile.27 .

docs: build
	docker run -it --rm \
		--name=$(APP) \
		-v $(shell pwd)/docs:/usr/src/app/docs \
		$(ORG)/$(APP):latest \
		make docs-pages

tests: build
	mkdir -p cover
	docker run -it --rm \
		--name=$(APP)-tests \
		-v $(shell pwd)/$(MODULE):/usr/src/app/$(MODULE) \
		-v $(shell pwd)/tests:/usr/src/app/tests \
		-v $(shell pwd)/cover:/usr/src/app/cover \
		$(ORG)/$(APP):latest \
		bash -c "pytest --cov=$(MODULE) --cov-report term --cov-report html:cover/ tests/ && cp .coverage cover/"
	mv -f cover/.coverage ./

tests27: build27
	docker run -it --rm \
		--name=$(APP)-tests \
		-v $(shell pwd)/$(MODULE):/usr/src/app/$(MODULE) \
		-v $(shell pwd)/tests:/usr/src/app/tests \
		$(ORG)/$(APP):latest27 \
		bash -c "pytest tests/"

lint-yapf: build
	docker run -it --rm \
		--name=$(APP)-tests \
		-v $(shell pwd)/.style.yapf:/usr/src/app/.style.yapf \
		-v $(shell pwd)/$(MODULE):/usr/src/app/$(MODULE) \
		-v $(shell pwd)/tests:/usr/src/app/tests \
		$(ORG)/$(APP) \
		yapf -rd $(MODULE) tests

lint-pylint: build
	docker run -it --rm \
		--name=$(APP)-tests \
		-v $(shell pwd)/.pylintrc:/usr/src/app/.pylintrc \
		-v $(shell pwd)/$(MODULE):/usr/src/app/$(MODULE) \
		-v $(shell pwd)/tests:/usr/src/app/tests \
		$(ORG)/$(APP) \
		pylint --rcfile=.pylintrc $(MODULE) tests

publish: build
	mkdir -p dist
	docker run -it --rm \
		--name=$(APP)-publish \
		-v $(shell pwd)/$(MODULE):/usr/src/app/$(MODULE) \
		-v $(shell pwd)/dist:/usr/src/app/dist \
		$(ORG)/$(APP) \
		python setup.py sdist bdist_wheel
	pip install twine
	twine upload dist/*
