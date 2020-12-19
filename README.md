# Container image to run OCA CI tests and runbot

These images provide the following guarantees

- Odoo runtime dependencies installed (wkhtmltopdf, lessc, etc)
- Odoo source in /opt/odoo
- Odoo installed in a virtualenv isolated from system python packages
- python, pip, odoo commands in PATH are from that virtualenv
- start in an empty work directory

Pre-set environment variables
- TODO: odoo version


Environment variables that control behavior:

- TODO: include, exclude addons?
- PIP_EXTRA_INDEX_URL
- PG*

Available commands

- `oca_install_addons`: install addons to test found in current directory, and
  their dependencies
- `oca_run_tests`: create a test database with direct dependencies of addons to
  test and run tests with coverage

## Build

build args:

- codename (default: focal)
- python_version (default: python3.8)

