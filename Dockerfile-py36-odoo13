FROM ubuntu:18.04

RUN set -ex \
  && apt update \
  && apt -y install python3-venv

RUN apt -y install git

RUN git clone --depth=1 --branch=13.0 https://github.com/odoo/odoo odoo-src

ENV PIP_USE_FEATURE 2020-resolver

RUN set -ex \
  && python3 -m venv odoo-venv \
  && odoo-venv/bin/pip install -U pip wheel setuptools \
  && odoo-venv/bin/pip install -r odoo-src/requirements.txt -e odoo-src -f https://wheelhouse.acsone.eu/manylinux1 \
  && odoo-venv/bin/pip install -U websocket-client

RUN set -ex \
  && python3 -m venv /opt/acsoo-venv \
  && /opt/acsoo-venv/bin/pip install -U pip wheel setuptools \
  && /opt/acsoo-venv/bin/pip install acsoo

ENV PATH=/odoo-venv/bin:$PATH
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

COPY addons /usr/local/bin

# TODO wkhtmltopdf
# TODO other common apt packages for OCA
# TODO remove dependency on acsoo by moving the acsoo addons to a standalone command
# TODO remove dependency on https://wheelhouse.acsone.eu/manylinux1 by pre-installing build deps

# This Dockerfile is for Odoo 13 with python 3.6
