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
    && rm -rf /var/lib/apt/lists/*

# Install wkhtml
RUN curl -sSL https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.$(lsb_release -c -s)_amd64.deb -o /tmp/wkhtml.deb \
    && apt-get update -qq \
    && dpkg --force-depends -i /tmp/wkhtml.deb \
    && DEBIAN_FRONTEND=noninteractive apt-get install -qq -f --no-install-recommends \
    && rm /tmp/wkhtml.deb \
    && rm -rf /var/lib/apt/lists/*

# Install nodejs
RUN curl -sSL https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - \
    && echo "deb https://deb.nodesource.com/node_15.x `lsb_release -c -s` main" > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update -qq \
    && DEBIAN_FRONTEND=noninteractive apt-get install -qq nodejs \
    && rm -rf /var/lib/apt/lists/*
RUN npm install -g rtlcss lessc

RUN curl -sSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -s -c`-pgdg main" > /etc/apt/sources.list.d/pgclient.list \
    && apt-get update -qq \
    && DEBIAN_FRONTEND=noninteractive apt-get install -qq postgresql-client-12 \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN curl -sSL http://nightly.odoo.com/odoo.key | apt-key add - \
    && echo "deb http://nightly.odoo.com/deb/$(lsb_release -s -c) ./" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update -qq \
    && DEBIAN_FRONTEND=noninteractive apt-get install -qq google-chrome-stable=80.0.3987.116-1 \
    && rm -rf /var/lib/apt/lists/*

RUN add-apt-repository -y ppa:deadsnakes/ppa

ARG python_version

# Install build dependencies for common Odoo requirements
RUN apt-get update -qq \
    && DEBIAN_FRONTEND=noninteractive apt-get install -qq --no-install-recommends \
       build-essential \
       python$python_version-dev \
       # for psycopg
       libpq-dev \
       # for lxml
       libxml2-dev \
       libxslt1-dev \
       libz-dev \
       # for python-ldap
       libldap2-dev \
       libsasl2-dev \
       # for older pillow versions
       libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# Make a virtualenv for Odoo so we isolate from system python dependencies
# and make sure addons we'll install declare all their python dependencies properly
RUN curl -sSL https://bootstrap.pypa.io/virtualenv/$python_version/virtualenv.pyz -o /usr/local/bin/virtualenv.pyz \
    && python$python_version /usr/local/bin/virtualenv.pyz -p python$python_version --download /opt/odoo-venv \
    && /opt/odoo-venv/bin/pip list
ENV PATH=/opt/odoo-venv/bin:$PATH

ARG odoo_version

# Install Odoo requirements (use ADD for correct layer caching)
ADD https://raw.githubusercontent.com/OCA/OCB/$odoo_version/requirements.txt /tmp/ocb-requirements.txt
RUN pip install --no-cache -r /tmp/ocb-requirements.txt

# Install other test requirements
RUN pip install coverage websocket-client

# Install Odoo (use ADD for correct layer caching)
ADD https://api.github.com/repos/odoo/odoo/git/refs/heads/$odoo_version /tmp/odoo-version.json
RUN git clone --depth=1 --branch=$odoo_version https://github.com/odoo/odoo /opt/odoo
RUN pip install --no-cache  -e /opt/odoo \
    && pip list

ENV PGHOST postgres
ENV PGUSER odoo
ENV PGPASSWORD odoo
ENV PGDATABASE odoo
