GAME ?= fallout_prequel.py
TIMEOUT ?= 120

.PHONY: install lint test smoke check golden

install:
	uv sync --all-extras --dev

lint:
	uv run ruff check .
	uv run ruff format --check .
	-uv run mypy $(GAME)

test:
	FALLOUT_TEST_MODE=1 uv run pytest tests/ -q

# Runs every sequence in tests/scripts/. Minimised crash reproducers
# from the Playtester land here and guard against regression forever.
# FALLOUT_TEST_MODE=1 is mandatory: without it slow_print sleeps per
# character and a full run takes minutes.
smoke:
	@set -e; \
	found=0; fail=0; \
	for f in tests/scripts/*.txt; do \
		[ -e "$$f" ] || continue; \
		found=1; \
		printf 'smoke: %-45s ' "$$f"; \
		if FALLOUT_TEST_MODE=1 timeout $(TIMEOUT) \
		     python3 $(GAME) < "$$f" > /dev/null 2>&1; then \
			echo "ok"; \
		else \
			code=$$?; \
			echo "FAIL (exit $$code)"; \
			fail=1; \
		fi; \
	done; \
	if [ "$$found" = "0" ]; then \
		echo "smoke: no sequences in tests/scripts/ yet"; \
	fi; \
	exit $$fail

# Golden path only — quick sanity check during development.
golden:
	@FALLOUT_TEST_MODE=1 timeout $(TIMEOUT) \
	  python3 $(GAME) < tests/scripts/golden-path.txt > /dev/null 2>&1 \
	  && echo "golden: ok" || echo "golden: FAIL"

check: lint test smoke
