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

    # @http.route('/api/solocruceros-invoice-register', auth='user', type='json', methods=['POST'], csrf=False)
    @http.route('/api/solocruceros-invoice-register', auth='user', type='json', methods=['POST'], csrf=False)
    def sc_api_invoice(self):
        try:
            #request.session.authenticate('Andres_Test', 'acastillo@develoop.net', 'Temp1243')
            #INICIALIZACION
            self.ID_LOG = 0
            self.INTENTS = 0
            body_data = json.loads(request.httprequest.data)
            _logger.info(body_data)

            self.validation(body_data)

            account = self.process_data(body_data)

            return { 'status_code':200, 'invoice_id': account.id, 'message':'success' }
        except Exception as e:
            _logger.info(str(e))
            return { 'status_code':500, 'message':'Error de tipo ' + str(e) }


    def validation(self, data):
        msg = ""
        if(data):
            msg = msg + ('' if data.get('partner_id', False) else 'Falta el valor de: partner_id \r\n')
            msg = msg + ('' if data.get('reserve_number', False) else 'Falta el valor de: reserve_number \r\n')
            #msg = msg + ('' if data['confirmationDate'] else 'Falta el valor de: confirmationDate \r\n')
            
            for index in range(len(data.get('invoice_lines', []))):
                
                if(not data['invoice_lines'][index].get('product_id', False)):
                    msg += 'Linea: ' + str(index) + ': Falta el valor de: product_id \r\n'
                elif(not request.env['product.template'].search([('id','=',data['invoice_lines'][index]['product_id'])])):
                    msg += 'No se encontro el producto con Id: ' + str(data['invoice_lines'][index]['product_id']) + '\r\n'

                if(not data['invoice_lines'][index].get('account_id', False)):
                    msg += 'Linea: ' + str(index) + ': Falta el valor de: account_id \r\n'
                elif(not request.env['account.account'].search([('id','=',data['invoice_lines'][index]['account_id'])])):
                    msg += 'No se encontro la cuenta con Id: ' + str(data['invoice_lines'][index]['account_id']) + '\r\n'

                #msg = msg + ('' if data['invoice_lines'][index]['product_id'] else 'Linea: ' + str(index) + ': Falta el valor de: product_id \r\n')
                msg = msg + ('' if data['invoice_lines'][index]['label'] else 'Linea: ' + str(index) + ': Falta el valor de: label \r\n')
                #msg = msg + ('' if data['invoice_lines'][index]['account_code'] else 'Linea: ' + str(index) + ': Falta el valor de: account_code \r\n')
                msg = msg + ('' if data['invoice_lines'][index]['quantity'] else 'Linea: ' + str(index) + ': Falta el valor de: quantity \r\n')
                msg = msg + ('' if data['invoice_lines'][index]['price'] else 'Linea: ' + str(index) + ': Falta el valor de: price \r\n')

        if(msg != ''):
            raise exceptions.UserError("Faltan los siguientes datos \r\n" +  msg)



    def process_data(self, data):
        reserve_number = data.get('reserve_number', False)
        confirmation_date = self.get_datetime(data.get('confirmationDate')) if data.get('confirmationDate', False) else False
        partner_id = request.env['res.partner'].search([('id','=',data.get('partner_id'))]).id if data.get('partner_id', False) else False
        
        account_move = request.env['account.move'].create({
            'partner_id': partner_id,
            'ref': reserve_number,
            'invoice_date': confirmation_date,
            'type':'out_invoice'
        })
        account_move._onchange_partner_id()
        
        for line in data['invoice_lines']:
            account = request.env['account.account'].search([('code','=',line['account_id'])])

            ctx = (request.context.copy())
            ctx.update(check_move_validity=False)
            request.context = ctx

            account_move_line = request.env['account.move.line'].create({
                'move_id': account_move.id,
                'product_id': line['product_id'],
                'name': line['label'],
                'account_id': account.id,
                'quantity': line['quantity'],
                'price_unit': line['price'],
                'exclude_from_invoice_tab':False
            })
            account_move_line._onchange_product_id()
            account_move_line.name = line['label']
            account_move_line.account_id = account.id
            account_move_line.quantity = line['quantity']
            account_move_line.price_unit = line['price']

        account_move.action_post()

        return account_move



    def get_datetime(self, date):
        if(date):
            yyyy = int(date[0: 4])
            mm = int(date[4: 6])
            dd = int(date[6: 8])
            _datetime = datetime.date(yyyy, mm, dd)
            return _datetime
        else:
            return ""