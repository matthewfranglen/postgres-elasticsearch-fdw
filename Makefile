.PHONY: requirements clean format test deploy

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PROJECT_NAME = pg_es_fdw

DEP_PROJECT_PYTHON = .make/poetry
POETRY_VENV = $(shell poetry env info -p)

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Install Python Dependencies
requirements : $(DEP_PROJECT_PYTHON)

## Completely reset environment
purge : clean
ifneq ($(POETRY_VENV),)
	poetry env remove $(shell basename $(POETRY_VENV))
endif
	if [ -e .make ]; then rm -rf .make; fi

## Delete all compiled Python files
clean :
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Format Python code
format : $(DEP_PROJECT_PYTHON)
	poetry run black pg_es_fdw tests

## Run Tests
test : $(DEP_PROJECT_PYTHON)
	poetry run tests/run.py --pg 9.4 9.5 9.6 10 11 --es 5 6 7

## Publish to pypi
publish : $(DEP_PROJECT_PYTHON)
	poetry publish --build

$(DEP_PROJECT_PYTHON) : pyproject.toml
	poetry install
	if [ ! -e .make ]; then mkdir .make; fi
	touch $(DEP_PROJECT_PYTHON)

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################



#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
