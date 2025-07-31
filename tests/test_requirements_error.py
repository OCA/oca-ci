import subprocess
from .common import preserve_odoo_rc, preserve_odoo_venv, make_addons_dir


def test_constraints_txt_error():
    with preserve_odoo_rc(), preserve_odoo_venv(), make_addons_dir(
        ["addon_success"]
    ) as addons_dir:
        # This file should not exist, but we create it to test the error handling
        addons_dir.joinpath("test-constraints.txt").touch()
        result = subprocess.run(
            ["oca_install_addons"], cwd=addons_dir, text=True, capture_output=True
        )
        assert result.returncode == 1
        assert "test-constraints.txt already exists" in result.stdout

