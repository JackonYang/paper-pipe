PY?=python3
PIP?=pip3
DC?=docker-compose

CODE_ROOT?=.

help:
	cd $(CODE_ROOT) && $(PY) manage.py --help

gen-notes-md:
	cd $(CODE_ROOT) && $(PY) manage.py gen-notes-md

merge-notes:
	cd $(CODE_ROOT) && $(PY) manage.py gen-notes-md --skip-gen-note-from-pdf --skip-gen-note-from-ref

gen-pdf-meta:
	cd $(CODE_ROOT) && $(PY) manage.py gen-pdf-meta

paper-download:
	cd $(CODE_ROOT) && $(PY) manage.py paper_download
	make collect-ref-meta

collect-ref-meta:
	cd $(CODE_ROOT) && $(PY) manage.py collect_ref_meta

# ----

check-dup:
	cd code && python manage.py check-dup

clean-deleted:
	cd $(CODE_ROOT) && bash scripts/clean_deleted_data.sh

gen-readme:
	cd code && python manage.py update-readme

dvc-add:
	dvc add pdfs/*.pdf
	make gen-meta
	make check-dup

push-all:
	make flake8
	dvc push
	git push

# ---- common commands of python project ----

setup:
	bash $(CODE_ROOT)/scripts/set-env-mac.sh

flake8:
	flake8 $(CODE_ROOT)

test:
	PYTHONPATH=$(CODE_ROOT) pytest --cov $(CODE_ROOT) --cov-report term-missing:skip-covered --capture=no -p no:cacheprovider

.PHONY: help
.PHONY: paper-download collect-ref-meta
.PHONY: gen-notes-md gen-pdf-meta merge-notes

.PHONY: check-dup
.PHONY: clean-deleted
.PHONY: dvc-add push-all

.PHONY: setup flake8 test
