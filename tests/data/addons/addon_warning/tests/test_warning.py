import logging
from odoo.tests.common import TransactionCase


_logger = logging.getLogger(__name__)

class Test(TransactionCase):
    def test_log_warning(self):
        _logger.warning("This is a warning")
