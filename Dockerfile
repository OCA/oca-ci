ARG codename=focal

FROM ubuntu:$codename
ENV LANG C.UTF-8
USER root

# Basic dependencies
RUN apt-get update -qq \
    && DEBIAN_FRONTEND=noninteractive apt-get install -qq --no-install-recommends \
        ca-certificates \
        curl \
        gettext \
        git \
        gnupg \
        lsb-release \
        software-properties-common \
        expect-dev \
        pipx

ENV PIPX_BIN_DIR=/usr/local/bin

# Install wkhtml
RUN case $(lsb_release -c -s) in \
      focal) WKHTML_DEB_URL=https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.focal_amd64.deb ;; \
      jammy) WKHTML_DEB_URL=https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb ;; \
    esac \
    && curl -sSL $WKHTML_DEB_URL -o /tmp/wkhtml.deb \
    && apt-get update -qq \
    && DEBIAN_FRONTEND=noninteractive apt-get install -qq -y --no-install-recommends /tmp/wkhtml.deb  \
    && rm /tmp/wkhtml.deb

# Install nodejs dependencies
RUN case $(lsb_release -c -s) in \
      focal) NODE_SOURCE="deb https://deb.nodesource.com/node_15.x focal main" \
             && curl -sSL https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - ;; \
      jammy) NODE_SOURCE="deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" \
             && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg ;; \
    esac \
    && echo "$NODE_SOURCE" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update -qq \
    && DEBIAN_FRONTEND=noninteractive apt-get install -qq nodejs
# less is for odoo<12
RUN npm install -g rtlcss less@3.0.4 less-plugin-clean-css

# Install postgresql client
RUN curl -sSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -s -c`-pgdg main" > /etc/apt/sources.list.d/pgclient.list \
    && apt-get update -qq \
    && DEBIAN_FRONTEND=noninteractive apt-get install -qq postgresql-client-12

# Install Google Chrome for browser tests
RUN curl -sSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o /tmp/chrome.deb \
    && apt-get -y install --no-install-recommends /tmp/chrome.deb \
    && rm /tmp/chrome.deb

RUN add-apt-repository -y ppa:deadsnakes/ppa

ARG python_version

# Install build dependencies for python libs commonly used by Odoo and OCA
RUN apt-get update -qq \
    && DEBIAN_FRONTEND=noninteractive apt-get install -qq --no-install-recommends \
       build-essential \
       python${python_version}-dev \
       python${python_version}-venv \
       # we need python 3 for our helper scripts
       python3 \
       python3-venv \
       # for psycopg
       libpq-dev \
       # for lxml
       libxml2-dev \
       libxslt1-dev \
       libz-dev \
       libxmlsec1-dev \
       # for python-ldap
       libldap2-dev \
       libsasl2-dev \
       # need libjpeg to build older pillow versions
       libjpeg-dev \
       # for pycups
       libcups2-dev \
       # for mysqlclient \
       default-libmysqlclient-dev \
       # some other build tools
       swig \
       libffi-dev \
       pkg-config

# We use manifestoo to check licenses, development status and list addons and dependencies
RUN pipx install --pip-args="--no-cache-dir" "manifestoo>=0.3.1"

# Install pyproject-dependencies helper scripts.
ARG build_deps="setuptools-odoo wheel whool"
RUN pipx install --pip-args="--no-cache-dir" pyproject-dependencies
RUN pipx inject --pip-args="--no-cache-dir" pyproject-dependencies $build_deps

# Make a virtualenv for Odoo so we isolate from system python dependencies and
# make sure addons we test declare all their python dependencies properly
# Use setuptools<64 because it is the last version that does not support PEP 660,
# and setuptools's PEP 660 default implementation breaks compatibility with Odoo
# when editable installs are done in standard-based mode by pip.
ARG setuptools_constraint="<64"
RUN python$python_version -m venv /opt/odoo-venv \
    && /opt/odoo-venv/bin/pip install -U "setuptools$setuptools_constraint" "pip" \
    && /opt/odoo-venv/bin/pip list
ENV PATH=/opt/odoo-venv/bin:$PATH

ARG odoo_version

# Install Odoo requirements (use ADD for correct layer caching).
# We use requirements from OCB for easier maintenance of older versions.
# We use no-binary for psycopg2 because its binary wheels are sometimes broken
# and not very portable.
ADD https://raw.githubusercontent.com/OCA/OCB/$odoo_version/requirements.txt /tmp/ocb-requirements.txt
RUN pip install --no-cache-dir --no-binary psycopg2 -r /tmp/ocb-requirements.txt

# Install other test requirements.
# - coverage
# - websocket-client is required for Odoo browser tests
RUN pip install --no-cache-dir \
  coverage \
  websocket-client

# Install Odoo (use ADD for correct layer caching)
ARG odoo_org_repo=odoo/odoo
ADD https://api.github.com/repos/$odoo_org_repo/git/refs/heads/$odoo_version /tmp/odoo-version.json
RUN mkdir /tmp/getodoo \
    && (curl -sSL https://github.com/$odoo_org_repo/tarball/$odoo_version | tar -C /tmp/getodoo -xz) \
    && mv /tmp/getodoo/* /opt/odoo \
    && rmdir /tmp/getodoo
RUN pip install --no-cache-dir -e /opt/odoo \
    && pip list

# Make an empty odoo.cfg
RUN echo "[options]" > /etc/odoo.cfg
ENV ODOO_RC=/etc/odoo.cfg
ENV OPENERP_SERVER=/etc/odoo.cfg

COPY bin/* /usr/local/bin/

ENV ODOO_VERSION=$odoo_version
ENV PGHOST=postgres
ENV PGUSER=odoo
ENV PGPASSWORD=odoo
ENV PGDATABASE=odoo
# This PEP 503 index uses odoo addons from OCA and redirects the rest to PyPI,
# in effect hiding all non-OCA Odoo addons that are on PyPI.
ENV PIP_INDEX_URL=https://wheelhouse.odoo-community.org/oca-simple-and-pypi
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_PYTHON_VERSION_WARNING=1
# Control addons discovery. INCLUDE and EXCLUDE are comma-separated list of
# addons to include (default: all) and exclude (default: none)
ENV ADDONS_DIR=.
ENV ADDONS_PATH=/opt/odoo/addons
ENV INCLUDE=
ENV EXCLUDE=
ENV OCA_GIT_USER_NAME=oca-ci
ENV OCA_GIT_USER_EMAIL=oca-ci@odoo-community.org
