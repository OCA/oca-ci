import subprocess

import pytest

from .common import install_test_addons, dropdb, odoo_version_info

pytestmark = pytest.mark.skipif(
    odoo_version_info < (20, 0), reason="Hoot tests are run since Odoo 20"
)


def test_hoot_success():
    """Test that Hoot tests of the addons to test are run."""
    with install_test_addons(["addon_hoot_success"]) as addons_dir:
        dropdb()
        subprocess.check_call(["oca_init_test_database"], cwd=addons_dir)
        result = subprocess.check_output(
            ["oca_run_tests"], cwd=addons_dir, text=True
        )
        test_name = "@addon_hoot_success/addon_hoot_success/success"
        assert f'[HOOT] Running test "{test_name}"' in result
        assert "[HOOT] Test suite succeeded" in result


def test_hoot_failure():
    """Test that a failing Hoot test makes oca_run_tests fail."""
    with install_test_addons(["addon_hoot_failure"]) as addons_dir:
        dropdb()
        subprocess.check_call(["oca_init_test_database"], cwd=addons_dir)
        result = subprocess.run(
            ["oca_run_tests"], cwd=addons_dir, text=True, capture_output=True
        )
        test_name = "@addon_hoot_failure/addon_hoot_failure/failure"
        assert result.returncode != 0
        assert f'[HOOT] Test "{test_name}" failed' in result.stdout
