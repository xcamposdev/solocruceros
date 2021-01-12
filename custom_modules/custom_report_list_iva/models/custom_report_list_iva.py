# -*- coding: utf-8 -*-

import logging
from odoo import tools
from odoo import api, fields, models, exceptions, _
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)

class custom_report_list_iva(models.Model):
    
    _name = "report.list.iva.custom"
    _description = "List of Iva"
    _auto = False
    _order = 'x_account_id desc'

    x_account_id = fields.Integer("account_id")
    x_currency_id = fields.Many2one('res.currency', string='Currency')
    x_invoice_number = fields.Char(string="Número factura")
    x_invoice_date = fields.Date(string="Fecha factura")
    x_invoice_partner_id = fields.Many2one('res.partner', string="Razón social")
    x_invoice_dni_nif = fields.Char(string="DNI/NIF")
    x_invoice_fiscal_position_id = fields.Many2one('account.fiscal.position', string="Posición fiscal")
    x_invoice_amount_untaxes = fields.Monetary(string="Impuesto no incluido")
    #x_invoice_tax_ids = fields.Many2many('account.tax', 'account_move_line_account_tax_rel', 'account_move_line_id')
    x_invoice_tax_ids = fields.Char(string="% Impuesto")
    #x_invoice_taxes_percent = fields.Char(string="% Impuesto")
    x_invoice_taxes_value = fields.Monetary(string="Total Impuesto")
    x_invoice_amount_total = fields.Monetary(string="Total Factura")


    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
            CREATE OR REPLACE VIEW %s AS (
                SELECT  max(x_account_line_id) id,
                        x_account_id, 
                        x_currency_id, 
                        x_invoice_number, 
                        x_invoice_date, 
                        x_invoice_partner_id, 
                        x_invoice_dni_nif, 
                        x_invoice_fiscal_position_id,
                        sum(x_invoice_amount_untaxes) x_invoice_amount_untaxes,
                        x_invoice_tax_ids x_invoice_tax_ids,
                        min(x_invoice_taxes_percent) x_invoice_taxes_percent,
                        sum(x_invoice_taxes_value) x_invoice_taxes_value, 
                        sum(x_invoice_amount_total) x_invoice_amount_total
                    FROM (
                        SELECT a_m.id as x_account_id,
                            a_m_l.id as x_account_line_id,
                            a_m.currency_id as x_currency_id,
                            a_m.name as x_invoice_number,
                            a_m.invoice_date as x_invoice_date,
                            a_m.partner_id as x_invoice_partner_id,
                            r_p.vat as x_invoice_dni_nif,
                            a_m.fiscal_position_id as x_invoice_fiscal_position_id,
                            CASE WHEN a_m.reversed_entry_id IS NULL THEN a_m_l.price_subtotal ELSE a_m_l.price_subtotal*-1 END as x_invoice_amount_untaxes,
                            --(SELECT name FROM account_tax WHERE id in (array_to_string(array_remove(ARRAY_AGG(a_m_l_tax.account_tax_id), NULL),','))) x_invoice_tax_ids,
                            --array_remove(ARRAY_AGG(a_m_l_tax.account_tax_id), NULL)::int[] x_invoice_tax_ids,
                            array_to_string(ARRAY_AGG(a_t.name),'; ') x_invoice_tax_ids,
                            sum(a_t.amount) x_invoice_taxes_percent,
                            CASE WHEN a_m.reversed_entry_id IS NULL THEN (a_m_l.price_subtotal * sum(a_t.amount) / 100) ELSE (a_m_l.price_subtotal * sum(a_t.amount) / 100)*-1 END  x_invoice_taxes_value,
                            CASE WHEN a_m.reversed_entry_id IS NULL THEN a_m_l.price_total ELSE a_m_l.price_total*-1 END as x_invoice_amount_total
                            --a_m_l.price_total as x_invoice_amount_total

                        FROM account_move a_m INNER JOIN account_move_line a_m_l ON a_m.id = a_m_l.move_id
                                    INNER JOIN res_partner r_p ON a_m.partner_id = r_p.id
                                    LEFT JOIN account_move_line_account_tax_rel a_m_l_tax ON a_m_l.id=a_m_l_tax.account_move_line_id
                                    LEFT JOIN account_tax a_t ON a_t.id=a_m_l_tax.account_tax_id

                        WHERE a_m_l.exclude_from_invoice_tab=false
                        GROUP BY a_m.id, a_m_l.id, a_m.currency_id, a_m.name, a_m.invoice_date, a_m.partner_id, r_p.vat, a_m.fiscal_position_id
                    ) a
                    GROUP BY a.x_account_id, a.x_currency_id, a.x_invoice_number, a.x_invoice_date, a.x_invoice_partner_id, a.x_invoice_dni_nif, a.x_invoice_fiscal_position_id, a.x_invoice_tax_ids
            )
        ''' % (
            self._table,
        ))

    # def read(self, fields=None, load='_classic_read'):
    #     to_return = super(custom_report_list_iva, self).read(fields=fields, load=load)
    #     for data in to_return:
    #         if data.get('x_invoice_tax_ids', False):
    #             taxes = self.env['account.tax'].search([('id','in',data.get('x_invoice_tax_ids'))])
    #             name = ""
    #             value = 0
    #             isfirst = True
    #             for tax in taxes:
    #                 name = name + ("" if isfirst else '; ') + str(_(tax.name))
    #                 value = value + data['x_invoice_amount_untaxes'] * tax.amount / 100
    #                 isfirst = False
    #             data['x_invoice_taxes_percent'] = name
    #             data['x_invoice_taxes_value'] = value
    #         else:
    #             data['x_invoice_taxes_percent'] = 0
    #             data['x_invoice_taxes_value'] = 0
    #     return to_return