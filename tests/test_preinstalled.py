"""Various test that the Dockerfile did what the README promises."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from .common import odoo_bin, make_addons_dir


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


def test_import_odoo():
    subprocess.check_call(["python", "-c", "import odoo.addons"])
    subprocess.check_call(["python", "-c", "import odoo.cli"])


def _target_python_version():
    version = subprocess.check_output(
        ["python", "-c", "import platform; print(platform.python_version())"],
        universal_newlines=True,
    )
    major, minor = version.split(".")[:2]
    return int(major), int(minor)


@pytest.mark.skipif(
    _target_python_version() < (3, 7), reason="Whool requires python3.7 or higher"
)
def test_import_odoo_after_addon_install():
    with make_addons_dir(["addon_success"]) as addons_dir:
        addon_dir = addons_dir / "addon_success"
        subprocess.check_call(["git", "init"], cwd=addon_dir)
        subprocess.check_call(["git", "add", "."], cwd=addon_dir)
        subprocess.check_call(["git", "config", "user.email", "..."], cwd=addon_dir)
        subprocess.check_call(
            ["git", "config", "user.name", "me@example.com"], cwd=addon_dir
        )
        subprocess.check_call(["git", "commit", "-m", "..."], cwd=addon_dir)
        subprocess.check_call(
            ["python", "-m", "pip", "install", addons_dir / "addon_success"]
        )
    subprocess.check_call(["python", "-c", "import odoo.cli"])
