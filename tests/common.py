import os


odoo_version_info = tuple(map(int, os.environ["ODOO_VERSION"].split(".")))


if odoo_version_info < (10, 0):
    odoo_bin = "openerp-server"
else:
    odoo_bin = "odoo"
