import ast
import contextlib
import os
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path

ODOO_VENV = "/opt/odoo-venv"

test_addons_dir = Path(__file__).parent / "data" / "addons"

odoo_version_info = tuple(map(int, os.environ["ODOO_VERSION"].split(".")))

odoo_bin = "odoo"

# build addons with whool (True) or setuptools-odoo (False)
use_whool = (odoo_version_info >= (17, 0))


@contextlib.contextmanager
def preserve_odoo_rc():
    odoo_rc_path = Path(os.environ["ODOO_RC"])
    odoo_rc = odoo_rc_path.read_bytes()
    try:
        yield
    finally:
        odoo_rc_path.write_bytes(odoo_rc)


@contextlib.contextmanager
def preserve_odoo_venv():
    subprocess.check_call(["cp", "-arl", ODOO_VENV, ODOO_VENV + ".org"])
    try:
        yield
    finally:
        subprocess.check_call(["rm", "-r", ODOO_VENV])
        subprocess.check_call(["mv", ODOO_VENV + ".org", ODOO_VENV])


def get_addon_project_dir(addons_dir: Path, addon_name: str) -> Path:
    if use_whool:
        # When using whool, the project dir is the addon dir, where pyproject.toml is
        return addons_dir / addon_name
    else:
        # When using setuptools-odoo, the setup directory is on the side
        return addons_dir / "setup" / addon_name


@contextlib.contextmanager
def make_addons_dir(test_addons):
    """Copy test addons to a temporary directory.

    Adjust the addons version to match the Odoo version being tested.
    Rename __manifest__.py to __openerp__.py for older Odoo versions.
    Add pyproject.toml.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        for addon_name in test_addons:
            shutil.copytree(test_addons_dir / addon_name, tmppath / addon_name)
            # prefix Odoo version
            manifest_path = tmppath / addon_name / "__manifest__.py"
            manifest = ast.literal_eval(manifest_path.read_text())
            manifest["version"] = os.environ["ODOO_VERSION"] + "." + manifest["version"]
            manifest_path.write_text(repr(manifest))
            if odoo_version_info < (10, 0):
                manifest_path.rename(manifest_path.parent / "__openerp__.py")
            if use_whool:
                pyproject_toml_dir = get_addon_project_dir(tmppath, addon_name)
                assert pyproject_toml_dir.is_dir()
                pyproject_toml_dir.joinpath("pyproject.toml").write_text(
                    textwrap.dedent(
                        """\
                        [build-system]
                        requires = ["whool"]
                        build-backend = "whool.buildapi"
                        """
                    )
                )
            else:
                setup_py_dir = get_addon_project_dir(tmppath, addon_name)
                setup_py_dir.mkdir(parents=True, exist_ok=True)
                setup_py_dir.joinpath("setup.py").write_text(
                    textwrap.dedent(
                        """\
                        import setuptools

                        setuptools.setup(
                            setup_requires=['setuptools-odoo'],
                            odoo_addon=True,
                        )
                        """
                    )
                )
                setup_py_dir.joinpath("odoo").mkdir()
                setup_py_dir.joinpath("odoo").joinpath("addons").mkdir()
                setup_py_dir.joinpath("odoo").joinpath("addons").joinpath(addon_name).symlink_to(
                    tmppath / addon_name
                )
        yield tmppath


@contextlib.contextmanager
def install_test_addons(test_addons):
    with preserve_odoo_rc(), preserve_odoo_venv(), make_addons_dir(
        test_addons
    ) as addons_dir:
        subprocess.check_call(["oca_install_addons"], cwd=addons_dir)
        yield addons_dir


def dropdb():
    subprocess.check_call(["dropdb", "--if-exists", os.environ["PGDATABASE"]])


def did_run_test_module(output, test_module):
    """Check that a test did run by looking in the Odoo log.

    test_module is the full name of the test (addon_name.tests.test_module).
    """
    return "odoo.addons." + test_module in output


def make_addon_dist_name(addon_name):
    odoo_series = int(os.getenv("ODOO_VERSION").partition(".")[0])
    return "odoo{odoo_series}-addon-{name}".format(
        name=addon_name,
        odoo_series=odoo_series if odoo_series < 15 else "",
    )
