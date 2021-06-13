import subprocess
from .common import make_addons_dir


def test_list_external_dependencies():
    with make_addons_dir(["addon_with_deb_dep"]) as addons_dir:
        res = subprocess.check_output(
            ["oca_list_external_dependencies", "deb"], cwd=addons_dir
        )
        assert res == b"nano\n"
