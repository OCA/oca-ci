# Container image to run OCA CI tests and runbot

These images provide the following guarantees

- Odoo runtime dependencies installed (wkhtmltopdf, lessc, etc)
- Odoo shallow git clone in /opt/odoo
- Odoo installed in a virtualenv isolated from system python packages
- python, pip, odoo commands in PATH are from that virtualenv
- start in an empty work directory

Environment variables:

- ODOO_VERSION
- PGHOST=postgres
- PGUSER=odoo
- PGPASSWORD=odoo
- PGDATABASE=odoo
- ADDONS_DIR=.
- PIP_EXTRA_INDEX_URL=https://wheelhouse.odoo-community.org/oca-simple
- PIP_DISABLE_PIP_VERSION_CHECK=1
- PIP_NO_PYTHON_VERSION_WARNING=1
- INCLUDE=
- EXCLUDE=

Available commands

- `oca_install_addons`: install addons to test found in $ADDONS_DIR, and
  their dependencies
- `oca_init_test_database`: create a test database with direct dependencies of
  addons to test
- `oca_run_tests`: run tests with coverage

## Build

Build args:

- python_version (no default)
- odoo_version (no default)
- codename (default: focal)
- odoo_org_repo (default: odoo/odoo)
