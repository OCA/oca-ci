import os
import subprocess
from .common import install_test_addons, dropdb, did_run_test_module


def test_checklog_enabled():
    """Test addon_warning with checklog enabled."""
    with install_test_addons(["addon_warning"]) as addons_dir:
        dropdb()
        subprocess.check_call(["oca_init_test_database"], cwd=addons_dir)
        os.environ["OCA_ENABLE_CHECKLOG_ODOO"] = "1"
        result = subprocess.run(
            ["oca_run_tests"], cwd=addons_dir, text=True, capture_output=True
        )
        os.environ["OCA_ENABLE_CHECKLOG_ODOO"] = ""
        assert result.returncode == 1 and "Error: Errors detected in log." in result.stderr

def test_checklog_disabled():
    """Test addon_warning with checklog disabled."""
    with install_test_addons(["addon_warning"]) as addons_dir:
        dropdb()
        subprocess.check_call(["oca_init_test_database"], cwd=addons_dir)
        result = subprocess.check_output(
            ["oca_run_tests"], cwd=addons_dir, text=True
        )
        assert did_run_test_module(result, "addon_warning.tests.test_warning")
