# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, exceptions, _
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)

class ForecastSales(models.Model):
    
    _name = 'x.menu.account.join'
    _description = "unir menu contabilidad"

    x_id_old = fields.Integer("Id Antiguo")
    x_id_new_id = fields.Integer("Id Nuevo")

    def update_account_menu_in_one(self):
        test = ""