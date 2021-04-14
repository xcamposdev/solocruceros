# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError


class res_partner_custom(models.Model):

    _inherit = 'res.partner'

    x_dni_passport_nie = fields.Char("DNI, Pasaporte o NIE")
