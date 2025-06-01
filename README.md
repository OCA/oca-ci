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
- The `python`, `pip` and `odoo` commands
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
- `ADDONS_PATH=/opt/odoo/addons`
- `INCLUDE=`
- `EXCLUDE=`
- `OCA_GIT_USER_NAME=oca-ci`: git user name to commit `.pot` files
- `OCA_GIT_USER_EMAIL=oca-ci@odoo-community.org`: git user email to commit
- `OCA_ENABLE_CHECKLOG_ODOO=`: enable odoo log error checking
  `.pot` files

## Using Odoo Enterprise Modules

This CI setup allows for the integration of Odoo Enterprise modules at **runtime** during the CI job, rather than building them directly into the Docker images. This provides flexibility and keeps the base Docker images lean.

Integration is controlled by GitHub Actions matrix variables and a repository secret:

### Required Configuration

1.  **Matrix Variables** (in your `.github/workflows/ci.yaml`):
    *   `odoo_enterprise_repo_url`: The SSH URL of the Odoo Enterprise repository. This now defaults to `git@github.com:odoo/enterprise.git`. You only need to set this in your matrix if you use a different enterprise repository.
    *   `odoo_enterprise_version`: The specific branch or tag to check out from the Odoo Enterprise repository. This now defaults to the value of `odoo_version` for the current CI job (e.g., if `odoo_version` is `16.0`, this will also default to `16.0`). You only need to set this if your enterprise versioning scheme differs from your Odoo Community version.

    You only need to explicitly define these variables in your CI matrix if you wish to override these default values.

2.  **GitHub Secret** (Mandatory for Enterprise usage):
    *   `ODOO_ENTERPRISE_SSH_PRIVATE_KEY`: This secret must be configured in your GitHub repository's settings (`Settings` > `Secrets and variables` > `Actions`). It should contain the private SSH key that has read-access to the Odoo Enterprise repository (either the default or your custom one). There is no default for this secret; it must be provided if you intend to use Odoo Enterprise modules.

### How it Works

When `odoo_enterprise_repo_url` and `odoo_enterprise_version` are defined in the CI matrix, and the `ODOO_ENTERPRISE_SSH_PRIVATE_KEY` secret is available, the workflow performs the following steps before running the tests:

1.  **SSH Setup**: The runner's SSH environment is configured using the provided private key to allow access to your enterprise repository.
2.  **Enterprise Code Checkout**: The specified version of your Odoo Enterprise code is checked out from `odoo_enterprise_repo_url` into a directory (e.g., `odoo-enterprise`) in the GitHub Actions runner's workspace.
3.  **Volume Mounting**: When the Docker container for tests is started, this directory containing the enterprise code is mounted as a volume into `/opt/odoo-enterprise` inside the container.
4.  **Addons Path Update**: The `ADDONS_PATH` environment variable within the container is automatically prepended with `/opt/odoo-enterprise`, ensuring that Odoo can discover and load these enterprise modules.

If `odoo_enterprise_repo_url` is not provided, is empty, or the `ODOO_ENTERPRISE_SSH_PRIVATE_KEY` secret is missing, these steps are skipped, and the tests will run using only the standard Odoo addons from the base image.

### Example Workflow Configuration

Here’s how you might configure your `.github/workflows/ci.yaml` to use Odoo Enterprise modules:

```yaml
# .github/workflows/ci.yaml
name: ci
on: [push, pull_request]

jobs:
  main:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        include:
          - python_version: "3.10"
            codename: "jammy"
            odoo_version: "16.0" # This should match your enterprise version
            odoo_org_repo: "odoo/odoo" # Or "oca/ocb"
            image_name: py3.10-odoo16.0 # Ensure this matches your built image
            # Odoo Enterprise settings (these are the defaults, override if needed):
            odoo_enterprise_repo_url: "git@github.com:odoo/enterprise.git"
            odoo_enterprise_version: "${{ matrix.odoo_version }}" # Defaults to the job's odoo_version

    steps:
      - name: Checkout # Checks out your current project (e.g., custom addons)
        uses: actions/checkout@v4

      # Docker build steps (Login, Build image, Push image) would be here
      # These steps build the base Odoo image without enterprise code.
      # Example:
      # - name: Set up Docker Buildx
      #   uses: docker/setup-buildx-action@v3
      # - name: Login to ghcr.io
      #   uses: docker/login-action@v3
      #   with:
      #     registry: ghcr.io
      #     username: ${{ github.repository_owner }}
      #     password: ${{ secrets.GITHUB_TOKEN }}
      # - name: Build image
      #   uses: docker/build-push-action@v6
      #   with:
      #     # build-args for the base image, NOT enterprise ones
      #     build-args: |
      #       codename=${{ matrix.codename }}
      #       python_version=${{ matrix.python_version }}
      #       odoo_version=${{ matrix.odoo_version }}
      #     tags: ghcr.io/letzdoo/letzdoo-ci/${{ matrix.image_name }} # Adjust image tag
      #     load: true # if tests run on the same job

      # Test execution step
      - name: Tests
        env:
          # Pass the SSH key to the test step environment
          ODOO_ENTERPRISE_SSH_PRIVATE_KEY: ${{ secrets.ODOO_ENTERPRISE_SSH_PRIVATE_KEY }}
          # PGHOST is usually set if your Postgres service is named 'postgres'
          PGHOST: localhost # Or your postgres service name if different
        run: |
          # The actual docker run command will be more complex
          # and include volume mounts for your project's addons, etc.
          # The ENTERPRISE_ARGS are now handled internally by the ci.yaml script steps
          docker run \
            -v ${{ github.workspace }}:/mnt/custom-addons \
            -e ADDONS_PATH="/mnt/custom-addons:/opt/odoo/addons" \
            # Potentially other existing env vars and volume mounts
            ghcr.io/letzdoo/letzdoo-ci/${{ matrix.image_name }} \
            /mnt/tests/runtests.sh -v # Or your test execution script
```

**Note:** The example above is simplified. Your actual `docker run` command in the "Tests" step will likely include other volume mounts (e.g., for your custom addons) and environment variables. The key is that the `odoo_enterprise_repo_url`, `odoo_enterprise_version` matrix variables, and the `ODOO_ENTERPRISE_SSH_PRIVATE_KEY` secret will trigger the automatic checkout and mounting of enterprise code if configured as per the main CI workflow logic.

Available commands:

- `oca_install_addons`: make addons to test (found in `$ADDONS_DIR`, modulo
  `$INCLUDE` an `$EXCLUDE`) and their dependencies available in the Odoo addons
  path. Append `addons_path=${ADDONS_PATH},${ADDONS_DIR}` to `$ODOO_RC`.
- `oca_init_test_database`: create a test database named `$PGDATABASE` with
  direct dependencies of addons to test installed in it
- `oca_run_tests`: run tests of addons on `$PGDATABASE`, with coverage.
- `oca_export_and_commit_pot`: export `.pot` files for all addons in
  `$ADDONS_DIR` that are installed in `$PGDATABASE`; git commit changes if any,
  using `$OCA_GIT_USER_NAME` and `$OCA_GIT_USER_EMAIL`.
- `oca_git_push_if_remote_did_not_change`: push local commits unless the remote
  tracked branch has evolved.
- `oca_export_and_push_pot` combines the two previous commands.
- `oca_checklog_odoo` checks odoo logs for errors (including warnings)

## Build

Build args:

- python_version (no default)
- odoo_version (no default)
- codename (default: focal)
- odoo_org_repo (default: odoo/odoo)

## Tests

Tests are written using [pytest](https://pytest.org) in the `tests` directory.

You can run them using the `runtests.sh` script inside the container.

In the test directory, there is a `docker-compose.yml` to help run the tests.
Tune it to your liking, then run:

`docker compose run --build test ./runtests.sh -v`

This docker-compose mounts this project, and `runtests.sh` adds then `bin` directory to
the `PATH` for easier dev/test iteration.

There is also a devcontainer configuration.
