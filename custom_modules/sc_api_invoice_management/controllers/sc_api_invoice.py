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

    @http.route('/api/solocruceros-invoice-register', auth='user', type='json', methods=['POST'], csrf=False)
    #@http.route('/api/solocruceros-invoice-register', auth='public', type='json', methods=['POST'], csrf=False)
    def sc_api_invoice(self):
        try:
            #request.session.authenticate('Andres_Test', 'acastillo@develoop.net', 'Temp1243')

            body_data = json.loads(request.httprequest.data)
            _logger.info(body_data)

            self.validation(body_data)

            #db, pool = pooler.get_db_and_pool(db_name)
            # create transaction cursor
            #cr = db.cursor()
            account_id = self.process_invoice(body_data)
            #cr.commit() # all good, we commit

            return { 'status_code':200, 'invoice_id': account_id, 'message':'success' }
        except Exception as e:
            _logger.info(str(e))
            request.cr.rollback()
            #cr.rollback() # error, rollback everything atomically
            return { 'status_code':500, 'message':'Error de tipo ' + str(e) }
        #finally:
            #cr.close() # always close cursor opened manually 481

    def validation(self, data):
        msg = ""
        if(data):
            msg = msg + ('' if data.get('partner_id', False) else 'Falta el valor de: partner_id \r\n')
            msg = msg + ('' if data.get('reserve_number', False) else 'Falta el valor de: reserve_number \r\n')
            
            for index in range(len(data.get('invoice_lines', []))):
                
                if not data['invoice_lines'][index].get('product_id', False):
                    msg += 'Linea: ' + str(index) + ': Falta el valor de: product_id \r\n'
                elif not request.env['product.template'].search([('id','=',data['invoice_lines'][index]['product_id'])]):
                    msg += 'No se encontro el producto con Id: ' + str(data['invoice_lines'][index]['product_id']) + '\r\n'

                if not data['invoice_lines'][index].get('account_id', False):
                    msg += 'Linea: ' + str(index) + ': Falta el valor de: account_id \r\n'
                elif not request.env['account.account'].search([('id','=',data['invoice_lines'][index]['account_id'])]):
                    msg += 'No se encontro la cuenta con Id: ' + str(data['invoice_lines'][index]['account_id']) + '\r\n'

                msg = msg + ('' if data['invoice_lines'][index]['label'] else 'Linea: ' + str(index) + ': Falta el valor de: label \r\n')
                msg = msg + ('' if data['invoice_lines'][index]['quantity'] else 'Linea: ' + str(index) + ': Falta el valor de: quantity \r\n')
                msg = msg + ('' if data['invoice_lines'][index]['price'] else 'Linea: ' + str(index) + ': Falta el valor de: price \r\n')

        if data.get('odoo_invoice_id', False) and data.get('payment_list', False):
            for index in range(len(data.get('payment_list', []))):
                
                if not data['payment_list'][index].get('diario_de_pago', False):
                    msg += 'Linea pago: ' + str(index) + ': Falta el valor de: diario_de_pago \r\n'
                # elif not request.env['account.journal'].search([('bank_account_id.acc_number','=',data['payment_list'][index]['diario_de_pago'])]):
                #     msg += 'No se encontro el diario de pago con Id: ' + str(data['payment_list'][index]['diario_de_pago']) + '\r\n'
                    
                if data['payment_list'][index].get('monto_pagado', True) == True:
                    msg += 'Linea pago: ' + str(index) + ': Falta el valor de: monto_pagado \r\n'

                if data['payment_list'][index].get('fecha_pago', True) == True:
                    msg += 'Linea pago: ' + str(index) + ': Falta el valor de: fecha_pago \r\n'

        if(msg != ''):
            raise exceptions.UserError("Faltan los siguientes datos \r\n" +  msg)

    def process_invoice(self, data):
        ctx = (request.context.copy())
        ctx.update(check_move_validity=False)
        request.context = ctx

        account_move = False
        if not data.get('odoo_invoice_id', False):
            account_move = self.create_account(data)
            return account_move.id
        else:
            self.create_rectification(data)
            account_move = self.create_account(data)
            return account_move.id

        

    def create_account(self, data):
        reserve_number = data.get('reserve_number', False)
        confirmation_date = self.get_datetime(data.get('confirmationDate')) if data.get('confirmationDate', False) else False
        partner_id = request.env['res.partner'].search([('id','=',data.get('partner_id'))]).id if data.get('partner_id', False) else False
        journal_id = request.env['account.journal'].search([('type','=?','sale')], limit=1)

        # Crea la Factura
        account_move = request.env['account.move'].create({
            'partner_id': partner_id,
            'ref': reserve_number,
            'invoice_date': confirmation_date,
            'journal_id':journal_id.id,
            'type':'out_invoice'
        })
        account_move._onchange_partner_id()

        #crea su detalle
        for line in data['invoice_lines']:
            account_move_line = request.env['account.move.line'].create({
                'move_id': account_move.id,
                'product_id': line['product_id'],
                'name': line['label'],
                'account_id': line['account_id'],
                'quantity': line['quantity'],
                'price_unit': line['price'],
                'exclude_from_invoice_tab': False
            })
            account_move_line._onchange_product_id()
            account_move_line.name = line['label']
            account_move_line.account_id = line['account_id']
            account_move_line.quantity = line['quantity']
            account_move_line.price_unit = line['price']
            
            account_move_line._onchange_price_subtotal()
            account_move_line._onchange_uom_id()
            account_move_line.price_unit = line['price']
            account_move_line._onchange_mark_recompute_taxes()
            account_move_line._onchange_credit()
            account_move_line._onchange_mark_recompute_taxes()
            
        account_move._onchange_invoice_line_ids()
        account_move.action_post()

        # Crea sus pagos
        if data.get('payment_list', False):
            currency = request.env['res.currency'].search([('name', '=', 'EUR')])
            payment_method_code = request.env['account.payment.method'].search([('code','=','manual'),('payment_type','=','inbound')])

            journal_process = []
            journals = request.env['account.journal'].search([('id','>',0)])
            for journal in journals:
                if journal.bank_account_id and journal.bank_account_id.acc_number:
                    code = journal.bank_account_id.acc_number.replace(" ", "")
                    journal_process.append({ 'id': journal.id, 'code': code })


            for payment in data['payment_list']:
                date_pay = self.get_datetime(payment['fecha_pago'])
                
                journal_find = list(_data for _data in journal_process if _data['code'] == payment['diario_de_pago'])
                
                payment = request.env['account.payment'].with_context(active_ids=account_move.ids, active_model='account.move', active_id=account_move.id) \
                    .create({
                    'amount': payment['monto_pagado'],
                    'communication': account_move.name,
                    'currency_id': currency.id,
                    'journal_id': journal_find[0]['id'],
                    'partner_id': account_move.partner_id.id,
                    'partner_type': 'customer',
                    'payment_date': date_pay,
                    #'invoice_ids': [(0, 0, account_move.ids )],
                    #ERROR:  inserción o actualización en la tabla «account_invoice_payment_rel» viola la llave foránea «account_invoice_payment_rel_invoice_id_fkey»
                    # DETAIL:  La llave (invoice_id)=(0) no está presente en la tabla «account_move».\n'
                    #'payment_difference_handling': ("reconcile" if (account_move.amount_residual == payment['monto_pagado']) else "open"),
                    'hide_payment_method': True,
                    'payment_method_id': payment_method_code.id,
                    'payment_method_code': 'manual',
                    'payment_type': 'inbound',
                })
                payment.post()

        return account_move

    def create_rectification(self, data):
        move = request.env['account.move'].search([('id','=',data.get('odoo_invoice_id'))])

        default_values_list = []
        default_values_list.append(self._prepare_default_reversal(move))
        new_moves = move._reverse_moves(default_values_list, cancel=True)
        

    def get_datetime(self, date):
        if(date):
            dd = int(date[0: 2])
            mm = int(date[3: 5])
            yyyy = int(date[6: 10])
            _datetime = datetime.date(yyyy, mm, dd)
            return _datetime
        else:
            return ""

    def _prepare_default_reversal(self, move):
            return {
            'ref': 'Reversión de: %s' % (move.name),
            'date': datetime.date.today(),
            'invoice_date': move.date,
            'journal_id': move.journal_id.id,
            'invoice_payment_term_id': None,
            'auto_post': False,
            'invoice_user_id': move.invoice_user_id.id,
        }
  