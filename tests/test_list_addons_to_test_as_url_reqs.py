import subprocess
import textwrap

from .common import make_addons_dir, make_addon_dist_name


def test_oca_list_addons_to_test_as_url_reqs__basic():
    """Basic successful test."""
    with make_addons_dir(
        ["addon_success", "addon_with_deb_dep", "uninstallable_addon"]
    ) as addons_dir:
        result = subprocess.check_output(
            ["oca_list_addons_to_test_as_url_reqs"], cwd=addons_dir, text=True
        )
        assert result == textwrap.dedent(
            f"""\
            {make_addon_dist_name('addon_success')} @ {addons_dir.as_uri()}/addon_success
            {make_addon_dist_name('addon_with_deb_dep')} @ {addons_dir.as_uri()}/addon_with_deb_dep
            """
        )


def test_oca_list_addons_to_test_as_url_reqs__editable():
    """Basic successful test with editables."""
    with make_addons_dir(
        ["addon_success", "addon_with_deb_dep", "uninstallable_addon"]
    ) as addons_dir:
        result = subprocess.check_output(
            ["oca_list_addons_to_test_as_url_reqs", "--editable"],
            cwd=addons_dir,
            text=True,
        )
        assert result == textwrap.dedent(
            f"""\
            -e {addons_dir.as_uri()}/addon_success#egg={make_addon_dist_name('addon_success')}
            -e {addons_dir.as_uri()}/addon_with_deb_dep#egg={make_addon_dist_name('addon_with_deb_dep')}
            """
        )


def test_oca_list_addons_to_test_as_url_reqs__skip_test_requirement():
    """Basic successful test."""
    with make_addons_dir(
        ["addon_success", "addon_with_deb_dep", "uninstallable_addon"]
    ) as addons_dir:
        # add URL reference to addon_success
        addons_dir.joinpath("test-requirements.txt").write_text(
            f"{make_addon_dist_name('addon_success')} @ git+https://github.com/oca/dummy@refs/pull/123/head"
        )
        result = subprocess.check_output(
            ["oca_list_addons_to_test_as_url_reqs"], cwd=addons_dir, text=True
        )
        # addon_success should not be in result because it is already in test-requirements.txt
        assert result == textwrap.dedent(
            f"""\
            {make_addon_dist_name('addon_with_deb_dep')} @ {addons_dir.as_uri()}/addon_with_deb_dep
            """
        )
