# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

class log_view_custom(models.AbstractModel):

    _inherit = 'report.l10n_es_vat_book.l10n_es_vat_book_xlsx'

    def fill_issued_row_data(
        self, sheet, row, line, tax_line, with_total, draft_export
    ):
        """ Fill issued data """

        (
            country_code,
            identifier_type,
            vat_number,
        ) = line.partner_id._parse_aeat_vat_info()
        sheet.write("A" + str(row), self.format_boe_date(line.invoice_date))
        # sheet.write('B' + str(row), self.format_boe_date(line.invoice_date))
        sheet.write("C" + str(row), line.ref[:-20])
        sheet.write("D" + str(row), line.ref[-20:])
        sheet.write("E" + str(row), "")  # Final number
        sheet.write("F" + str(row), identifier_type)
        if country_code != "ES":
            sheet.write("G" + str(row), country_code)
        sheet.write("H" + str(row), vat_number)
        if not vat_number and line.partner_id.aeat_anonymous_cash_customer:
            sheet.write("I" + str(row), "VENTA POR CAJA")
        else:
            if line.partner_id:
                sheet.write("I" + str(row), line.partner_id.name[:40])
            else:
                sheet.write("I" + str(row), '')
        # TODO: Substitute Invoice
        # sheet.write('J' + str(row),
        #             line.invoice_id.refund_invoice_id.number or '')
        sheet.write("K" + str(row), "")  # Operation Key
        if with_total:
            sheet.write("L" + str(row), line.total_amount)
        sheet.write("M" + str(row), tax_line.base_amount)
        sheet.write("N" + str(row), tax_line.tax_id.amount)
        sheet.write("O" + str(row), tax_line.tax_amount)
        if tax_line.special_tax_id:
            map_vals = line.vat_book_id.get_special_taxes_dic()[
                tax_line.special_tax_id.id
            ]
            sheet.write(
                map_vals["fee_type_xlsx_column"] + str(row),
                tax_line.special_tax_id.amount,
            )
            sheet.write(
                map_vals["fee_amount_xlsx_column"] + str(row),
                tax_line.special_tax_amount,
            )
        if draft_export:
            last_column = sheet.dim_colmax
            num_row = row - 1
            sheet.write(num_row, last_column, tax_line.tax_id.name)