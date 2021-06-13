"""Various test that the Dockerfile did what the README promises."""

import os
import shutil
from pathlib import Path
import subprocess

import pytest

from .common import odoo_bin, odoo_version_info


def test_odoo_bin_in_path():
    assert shutil.which(odoo_bin)


def test_wkhtomtopdf_in_path():
    assert shutil.which("wkhtmltopdf")


def test_python_in_path():
    assert shutil.which("python")
    assert Path(shutil.which("python")).parent == Path(shutil.which(odoo_bin)).parent


def test_pip_in_path():
    assert shutil.which("pip")
    assert Path(shutil.which("pip")).parent == Path(shutil.which(odoo_bin)).parent


def test_addons_dir():
    assert os.environ["ADDONS_DIR"] == "."


def test_odoo_rc():
    odoo_rc = Path(os.environ["ODOO_RC"])
    assert odoo_rc.exists()
    assert odoo_rc.read_text() == "[options]\n"


def test_openerp_server_rc():
    assert os.environ["OPENERP_SERVER"] == os.environ["ODOO_RC"]


@pytest.mark.skipif(odoo_version_info >= (10, 0), reason="Odoo>=10")
def test_import_openerp():
    subprocess.check_call(["python", "-c", "import openerp; openerp.addons.__path__"])


@pytest.mark.skipif(odoo_version_info < (10, 0), reason="Odoo<10")
def test_import_odoo():
    subprocess.check_call(["python", "-c", "import odoo; odoo.addons.__path__"])
