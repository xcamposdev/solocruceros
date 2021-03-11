# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from odoo import api, fields, models, exceptions, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_is_zero, float_compare
_logger = logging.getLogger(__name__)

class InvoiceReportListCustom(models.Model):

    _inherit = 'account.invoice.report'

    x_amount_untaxed_signed = fields.Monetary("Impuesto no incluido", compute="get_datas")
    x_amount_tax_signed = fields.Monetary(string='Impuesto', compute="get_datas")
    x_amount_total_signed = fields.Monetary(string='Total', compute="get_datas")
    x_residual_signed = fields.Monetary(string='Importe adeudado', compute="get_datas")

    def get_datas(self):
        for invoice in self:
            invoice.x_amount_untaxed_signed = invoice.move_id.amount_untaxed_signed
            invoice.x_amount_tax_signed = invoice.move_id.amount_tax
            invoice.x_amount_total_signed = invoice.move_id.amount_total_signed
            invoice.x_residual_signed = invoice.move_id.amount_residual_signed