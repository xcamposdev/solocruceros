# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError


class crm_custom_hide(models.TransientModel):
    _name = 'crm.lead2opportunity.partner.custom'
    _inherit = 'crm.lead2opportunity.partner'

    name = fields.Selection([
        ('convert', 'Convert to opportunity'),
        # ('merge', 'Merge with existing opportunities')
    ], 'Conversion Action', required=True)