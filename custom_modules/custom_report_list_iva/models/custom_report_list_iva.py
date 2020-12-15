# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, exceptions, _
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)

class custom_report_list_iva(models.Model):

    _inherit = 'account.move' 

    x_invoice_dni_nif = fields.Char(string="DNI/NIF")
    x_invoice_taxes_percent = fields.Char(string="% Impuesto")
    x_invoice_taxes_value = fields.Char(string="Total Impuesto")
    x_calculate = fields.Char(string="Calculador", compute="calculate_values")

    def calculate_values(self):
        for invoice in self:
            invoice.x_invoice_dni_nif = invoice.partner_id.vat
            invoice.x_invoice_taxes_percent = invoice.amount_tax_signed
            invoice.x_invoice_taxes_value = invoice.amount_tax
            invoice.x_calculate = 0

    def button_print_report(self):
        data = {
        	'model_id': self.id,
        }
        return self.env.ref('custom_report_list_iva.print_iva_report_pdf').report_action(self, data=data)

    

    
   