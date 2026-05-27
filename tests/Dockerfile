# Run the regression test suite in a pinned environment.
#
# Why this exists: HA 2026.3+ requires Python 3.14.2, the test deps are
# heavy (~100 transitive packages), and PYTHONPATH has to be the repo root
# for the tests to import `custom_components.localtuya.light`. Encapsulating
# all of that here lets developers do a pre-push smoke test with just
# `tests/run-tests` and no per-host Python juggling.
#
# Not the source of truth for CI — CI runs tox per .github/workflows/tox.yaml.
# If this image and CI diverge, CI wins.
FROM python:3.14-slim

RUN pip install --no-cache-dir 'pytest>=7.0' 'homeassistant>=2026.3'

WORKDIR /repo
COPY custom_components/ ./custom_components/
COPY tests/             ./tests/

ENV PYTHONPATH=/repo

CMD ["pytest", "-v", "--durations=10", "tests/"]
