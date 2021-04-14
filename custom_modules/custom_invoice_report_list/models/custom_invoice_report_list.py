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


    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        #data2 = super().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
        if self._context.get('from_action', False) and self._context.get('from_action') == 'custom':
            # if self._context.get('params', False) == False or \
            #     (self._context.get('params',False) and self._context.get('params').get('view_type',False) and self._context.get('params').get('view_type') == 'list'):
            data = self.env['account.invoice.report2'].sudo().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
            toreturn = []
            for record in data:
                new_data = {
                    'id': record.get('id', False),
                    'partner_id': record.get('partner_id', False),
                    'invoice_date': record.get('invoice_date',False),
                    'name': record.get('name',False),
                    'invoice_user_id': record.get('invoice_user_id',False),
                    'invoice_date_due': record.get('invoice_date_due',False),
                    'currency_id': record.get('currency_id',False),
                    'state': record.get('state',False),
                    'x_amount_untaxed_signed': record.get('x_amount_untaxed_signed',False),
                    'x_amount_tax_signed': record.get('x_amount_tax_signed',False),
                    'x_amount_total_signed': record.get('x_amount_total_signed',False),
                    'x_residual_signed': record.get('x_residual_signed',False),
                }
                toreturn.append(new_data)
            return toreturn
        else:        
            return super().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)