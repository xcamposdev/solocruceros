# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError


class res_partner_custom(models.Model):

    _inherit = 'res.partner'

    x_dni_passport_nie = fields.Char("DNI, Pasaporte o NIE")

    @api.model
    def create(self, values):
        vat = ""
        try:
            if values.get('vat'):
                vat = values.get('vat')
                country_id = values.get('country_id')
                code = self.env['res.country'].browse(country_id).code if country_id else False
                vat_country, vat_number = self._split_vat(values['vat'])
                if code and code.lower() != vat_country:
                    values['vat'] = str(code) + str(values['vat'])
            return super(res_partner_custom, self).create(values)            
        except Exception as e:
            _logger.info("Error al formatear nif {}".format(e))
            values['vat'] = vat
            return super(res_partner_custom, self).create(values)
        
