# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import json
import datetime
import copy 

from odoo import http
from odoo.http import request
from odoo import exceptions

_logger = logging.getLogger(__name__)

class scApiInvoiceManagement(http.Controller):

    @http.route('/api/invoice', auth='user', type='json', methods=['POST'], csrf=False)
    def sc_api_invoice(self):
        try:
            #request.session.authenticate('Andres_Test', 'acastillo@develoop.net', 'Temp1243')
            #INICIALIZACION
            self.ID_LOG = 0
            self.INTENTS = 0
            #body_data = json.loads(request.httprequest.data)
            
            return { 'status_code':200, 'message':'success' }
        except Exception as e:
            _logger.info(str(e))
            return { 'status_code':500, 'message':'Error de tipo ' + str(e) }
