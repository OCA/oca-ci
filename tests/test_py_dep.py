import subprocess

from .common import install_test_addons


def test_success():
    """Basic successful test."""
    with install_test_addons(["addon_with_py_dep"]):
        result = subprocess.check_output(["pip", "freeze"], text=True)
        assert "wrapt==" in result
