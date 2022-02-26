from pathlib import Path
import os

from .common import install_test_addons


def test_addons_path():
    """Test must not fail where there are no installable addons."""
    assert (
        Path(os.environ["ODOO_RC"]).read_text()
        == "[options]\n"
    )
    with install_test_addons(["addon_success"]):
        assert (
            Path(os.environ["ODOO_RC"]).read_text()
            == "[options]\naddons_path=/opt/odoo/addons,.\n"
        )
