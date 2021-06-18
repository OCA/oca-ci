import subprocess
from .common import install_test_addons


def test_no_addons():
    """Test must not fail where there are no installable addons."""
    with install_test_addons(["uninstallable_addon"]) as addons_dir:
        # no need to initialize test database because tests will not be attempted
        subprocess.check_call(["oca_run_tests"], cwd=addons_dir)
