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
    #_order = 'x_account_id desc'

    x_currency_id = fields.Many2one('res.currency', string='Currency')
    x_invoice_number = fields.Char(string="Número factura")
    x_type = fields.Selection(selection=[
            ('entry', 'Asiento contable'),
            ('out_invoice', 'Factura de cliente'),
            ('out_refund', 'Factura rectificativa de cliente'),
            ('in_invoice', 'Factura de proveedor'),
            ('in_refund', 'Factura rectificativa de proveedor'),
            ('out_receipt', 'Recibo de ventas'),
            ('in_receipt', 'Recibo de compra'),
        ], string='Tipo')
    x_state = fields.Selection(selection=[
            ('draft', 'Borrador'),
            ('posted', 'Publicado'),
            ('cancel', 'Cancelado')
        ], string='Estado')
    x_invoice_date = fields.Date(string="Fecha factura")
    x_invoice_partner_id = fields.Many2one('res.partner', string="Razón social")
    x_invoice_dni_nif = fields.Char(string="DNI/NIF")
    x_invoice_fiscal_position_id = fields.Many2one('account.fiscal.position', string="Posición fiscal")
    x_invoice_amount_untaxes = fields.Monetary(string="Impuesto no incluido")
    x_tax_name = fields.Char(string="% Impuesto")
    x_tax_value = fields.Monetary(string="Total Impuesto")
    x_invoice_amount_total = fields.Monetary(string="Total Factura")


    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
            CREATE OR REPLACE VIEW %s AS (
                SELECT 
                    row_number() over (order by a_m.id desc) as id,
                    a_m.currency_id as x_currency_id,
                    a_m.name as x_invoice_number,
                    a_m.type as x_type,
                    a_m.state as x_state,
                    a_m.invoice_date as x_invoice_date,
                    a_m.partner_id as x_invoice_partner_id,
                    r_p.vat as x_invoice_dni_nif,
                    a_m.fiscal_position_id as x_invoice_fiscal_position_id,
                    CASE WHEN a_m.type = 'out_refund' OR a_m.type = 'in_refund' THEN a_m_l.tax_base_amount*-1 ELSE a_m_l.tax_base_amount END as x_invoice_amount_untaxes,
                    a_t.name as x_tax_name,
                    a_t.amount as  x_taxes_percent,
                    CASE WHEN a_m.type = 'out_refund' OR a_m.type = 'in_refund' THEN a_m_l.price_total*-1 ELSE a_m_l.price_total END as x_tax_value,
                    a_m.amount_total_signed as x_invoice_amount_total

                FROM account_move a_m INNER JOIN account_move_line a_m_l ON a_m.id = a_m_l.move_id
                            INNER JOIN res_partner r_p ON a_m.partner_id = r_p.id
                                INNER JOIN account_tax a_t ON a_t.id=a_m_l.tax_line_id

                WHERE a_m_l.tax_line_id is not null
            )
        ''' % (
            self._table,
        ))
