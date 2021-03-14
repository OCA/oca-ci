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
        expect-dev

# Install wkhtml
RUN curl -sSL https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.$(lsb_release -c -s)_amd64.deb -o /tmp/wkhtml.deb \
    && apt-get update -qq \
    && dpkg --force-depends -i /tmp/wkhtml.deb \
    && DEBIAN_FRONTEND=noninteractive apt-get install -qq -f --no-install-recommends \
    && rm /tmp/wkhtml.deb

# Install nodejs
RUN curl -sSL https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - \
    && echo "deb https://deb.nodesource.com/node_15.x `lsb_release -c -s` main" > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update -qq \
    && DEBIAN_FRONTEND=noninteractive apt-get install -qq nodejs
RUN npm install -g rtlcss lessc

# Install postgresql client
RUN curl -sSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -s -c`-pgdg main" > /etc/apt/sources.list.d/pgclient.list \
    && apt-get update -qq \
    && DEBIAN_FRONTEND=noninteractive apt-get install -qq postgresql-client-12

RUN add-apt-repository -y ppa:deadsnakes/ppa

ARG python_version

# Install build dependencies for common Odoo requirements
RUN apt-get update -qq \
    && DEBIAN_FRONTEND=noninteractive apt-get install -qq --no-install-recommends \
       build-essential \
       python$python_version-dev \
       # we need python 3 for our helper scripts
       python3 \
       # virtualenv needs distutils https://github.com/pypa/virtualenv/issues/1910,
       # and why do distros split the python stdlib :/
       python3-distutils \
       # for psycopg
       libpq-dev \
       # for lxml
       libxml2-dev \
       libxslt1-dev \
       libz-dev \
       # for python-ldap
       libldap2-dev \
       libsasl2-dev \
       # need libjpeg to build older pillow versions
       libjpeg-dev

# We don't use the ubuntu virtualenv package because it unbundles pip dependencies
# in virtualenvs it create.
RUN curl -sSL https://bootstrap.pypa.io/virtualenv.pyz -o /usr/local/share/virtualenv.pyz

# Install the 'addons' helper script
# TODO: move it out of acsoo to a standalone, OCA-managed package, that
# could do additional addons manifest analysis such as checking license compatibility.
RUN python3 /usr/local/share/virtualenv.pyz /opt/acsoo \
    && /opt/acsoo/bin/pip install --no-cache-dir acsoo==3.0.2
COPY bin/addons /usr/local/bin

# Install setuptools-odoo-get-requirements helper script
RUN python3 /usr/local/share/virtualenv.pyz /opt/setuptools-odoo \
    && /opt/setuptools-odoo/bin/pip install --no-cache-dir "setuptools-odoo>=2.7" \
    && ln -s /opt/setuptools-odoo/bin/setuptools-odoo-get-requirements /usr/local/bin/

# Make a virtualenv for Odoo so we isolate from system python dependencies
# and make sure addons we'll install declare all their python dependencies properly
RUN python3 /usr/local/share/virtualenv.pyz -p python$python_version /opt/odoo-venv \
    && /opt/odoo-venv/bin/pip list
ENV PATH=/opt/odoo-venv/bin:$PATH

ARG odoo_version

# Install Odoo requirements (use ADD for correct layer caching).
# We use requirements from OCB for easier maintenance of older versions.
# We use no-binary for psycopg2 because its binary wheels are sometimes broken
# and not very portable.
ADD https://raw.githubusercontent.com/OCA/OCB/$odoo_version/requirements.txt /tmp/ocb-requirements.txt
RUN pip install --no-cache-dir --no-binary psycopg2 -r /tmp/ocb-requirements.txt

# Install other test requirements
RUN pip install --no-cache-dir coverage "odoo-autodiscover>=2 ; python_version<'3'"

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
ENV INCLUDE=
ENV EXCLUDE=
