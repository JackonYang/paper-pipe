PY?=python3
PIP?=pip3
DC?=docker-compose

CODE_ROOT?=src

help:
	cd $(CODE_ROOT) && $(PY) manage.py --help

# ---- main steps ------

paper-download:
	cd $(CODE_ROOT) && $(PY) manage.py paper_download

run-pipe:
	make gen-meta-yaml
	make gen-notes-md

gen-meta-yaml:
	make gen-pdf-meta
	make gen-ref-meta

gen-notes-md:
	cd $(CODE_ROOT) && $(PY) manage.py gen-notes-md

# ---- export ----

export-for-dp:
	cd $(CODE_ROOT) && $(PY) manage.py export-for-digital-paper

# ---- micro steps ----

gen-pdf-meta:
	cd $(CODE_ROOT) && $(PY) manage.py gen-pdf-meta

gen-pdf-notes:
	cd $(CODE_ROOT) && $(PY) manage.py gen-notes-md --skip-gen-note-from-ref

gen-ref-meta:
	cd $(CODE_ROOT) && $(PY) manage.py gen_ref_meta

gen-ref-notes:
	cd $(CODE_ROOT) && $(PY) manage.py gen-notes-md --skip-gen-note-from-pdf

merge-notes:
	cd $(CODE_ROOT) && $(PY) manage.py gen-notes-md --skip-gen-note-from-pdf --skip-gen-note-from-ref

# ----

check-dup:
	cd code && python manage.py check-dup

clean-deleted:
	cd $(CODE_ROOT) && bash scripts/clean_deleted_data.sh

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

.PHONY: paper-download
.PHONY: gen-meta-yaml
.PHONY: gen-notes-md

.PHONY: gen-ref-meta gen-ref-notes
.PHONY: gen-pdf-meta gen-pdf-notes
.PHONY: merge-notes

.PHONY: check-dup
.PHONY: clean-deleted
.PHONY: dvc-add push-all

.PHONY: setup flake8 test
