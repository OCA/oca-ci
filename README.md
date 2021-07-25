# Container image to run OCA CI tests

⚠️ These images are meant for running CI tests of the Odoo Community
Association. They are *not* intended for any other purpose, and in particular
they are not fit for running Odoo in production. If you decide to base your own
CI on these images, be aware that, while we will not break things without
reason, we will prioritize ease of maintenance for OCA over backward
compatibility. ⚠️

These images provide the following guarantees:

- Odoo runtime dependencies are installed (`wkhtmltopdf`, `lessc`, etc).
- Odoo source code is in `/opt/odoo`.
- Odoo is installed in editable mode in a virtualenv isolated from system python packages.
- The Odoo configuration file exists at `$ODOO_RC`.
- The `python`, `pip` and `odoo` (`openerp-server` for Odoo < 10) commands
  found first in `PATH` are from that virtualenv.
- `coverage` is installed in that virtualenv.
- Prerequisites for running Odoo tests are installed in that virtualenv
  (this notably includes `websocket-client` and the chrome browser for running
  browser tests).

Environment variables:

- `ODOO_VERSION` (8.0, ..., 14.0, ...)
- `ODOO_RC`
- `OPENERP_SERVER=$ODOO_RC`
- `PGHOST=postgres`
- `PGUSER=odoo`
- `PGPASSWORD=odoo`
- `PGDATABASE=odoo`
- `PIP_INDEX_URL=https://wheelhouse.odoo-community.org/oca-simple-and-pypi`
- `PIP_DISABLE_PIP_VERSION_CHECK=1`
- `PIP_NO_PYTHON_VERSION_WARNING=1`
- `ADDONS_DIR=.`
- `INCLUDE=`
- `EXCLUDE=`
- `OCA_GIT_USER_NAME=oca-ci`: git user name to commit `.pot` files
- `OCA_GIT_USER_EMAIL=oca-ci@odoo-community.org`: git user email to commit
  `.pot` files

Available commands:

- `oca_install_addons`: make addons to test (found in `$ADDONS_DIR`, modulo
  `$INCLUDE` an `$EXCLUDE`) and their dependencies available in the Odoo addons
  path.
- `oca_init_test_database`: create a test database named `$PGDATABASE` with
  direct dependencies of addons to test installed in it
- `oca_run_tests`: run tests of addons on `$PGDATABASE`, with coverage.
- `oca_export_and_commit_pot`: export `.pot` files for all addons in
  `$ADDONS_DIR` that are installed in `$PGDATABASE`; git commit changes if any,
  using `$OCA_GIT_USER_NAME` and `$OCA_GIT_USER_EMAIL`.

## Build

Build args:

- python_version (no default)
- odoo_version (no default)
- codename (default: focal)
- odoo_org_repo (default: odoo/odoo)

## Tests

Tests are written using [pytest](https://pytest.org) in the `tests` directory.

You can run them using the `runtests.sh` script inside the container, like this:

```console
docker run -v $PWD/tests:/mnt/tests ghcr.io/oca/oca-ci/py3.8-odoo14.0:latest /mnt/tests/runtests.sh -v
```
