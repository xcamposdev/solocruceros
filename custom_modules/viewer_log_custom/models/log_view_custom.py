# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

class log_view_custom(models.AbstractModel):

    _inherit = 'report.l10n_es_vat_book.l10n_es_vat_book_xlsx'

    def fill_issued_row_data(self, sheet, row, line, tax_line, with_total, draft_export):
        _logger.info(line)
        _logger.info(line.partner_id)
        super(log_view_custom, self).fill_issued_row_data(sheet, row, line, tax_line, with_total, draft_export)