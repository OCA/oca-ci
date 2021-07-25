import subprocess
from .common import install_test_addons, dropdb, did_run_test_module


def test_success():
    """Basic successful test."""
    with install_test_addons(["addon_success"]) as addons_dir:
        dropdb()
        subprocess.check_call(["oca_init_test_database"], cwd=addons_dir)
        result = subprocess.check_output(
            ["oca_run_tests"], cwd=addons_dir, text=True
        )
        assert did_run_test_module(result, "addon_success.tests.test_success")
