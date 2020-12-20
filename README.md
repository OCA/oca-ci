# Container image to run OCA CI tests and runbot

These images provide the following guarantees

- Odoo runtime dependencies are installed (wkhtmltopdf, lessc, etc).
- A shallow git clone of Odoo is in /opt/odoo.
- Odoo is installed in a virtualenv isolated from system python packages.
- The python, pip and odoo commands found first in PATH are from that
  virtualenv.

Environment variables:

- ODOO_VERSION
- PGHOST=postgres
- PGUSER=odoo
- PGPASSWORD=odoo
- PGDATABASE=odoo
- PIP_EXTRA_INDEX_URL=https://wheelhouse.odoo-community.org/oca-simple
- PIP_DISABLE_PIP_VERSION_CHECK=1
- PIP_NO_PYTHON_VERSION_WARNING=1
- ADDONS_DIR=.
- INCLUDE=
- EXCLUDE=

Available commands

- `oca_install_addons`: make addons to test (found in $ADDONS_DIR, modulo
  $INCLUDE and $EXCLUDE) and their dependencies available in the Odoo addons
  path
- `oca_init_test_database`: create a test database named $PGDATABASE with
  direct dependencies of addons to test installed in it
- `oca_run_tests`: run tests of addons on $PGDATABASE, with coverage

## Build

Build args:

- python_version (no default)
- odoo_version (no default)
- codename (default: focal)
- odoo_org_repo (default: odoo/odoo)
