from pathlib import Path
import os
import subprocess
from .common import make_addons_dir, preserve_odoo_rc


def test_list_external_dependencies():
    with make_addons_dir(["addon_with_deb_dep"]) as addons_dir:
        res = subprocess.check_output(
            ["oca_list_external_dependencies", "deb"], cwd=addons_dir
        )
        assert res == b"nano\n"


def test_list_external_dependencies_transitive():
    """Test that transitive external dependencies are returned."""
    with preserve_odoo_rc(), make_addons_dir(
        ["addon_with_deb_dep"]
    ) as dep_addons_dir, make_addons_dir(["addon_with_deb_dep2"]) as addons_dir:
        Path(os.getenv("ODOO_RC")).write_text(f"[options]\naddons_path={dep_addons_dir}\n")
        res = subprocess.check_output(
            ["oca_list_external_dependencies", "deb"], cwd=addons_dir
        )
        assert res == b"curl\nnano\n"
