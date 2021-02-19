# -*- coding: utf-8 -*-

import logging
import json
import datetime
import copy 

from odoo import http
from odoo.http import request
from odoo import exceptions

_logger = logging.getLogger(__name__)

class scApiInvoiceManagement(http.Controller):

    OPERATION_CREATE = 'create'
    OPERATION_ADDPAY = 'addPay'
    OPERATION_OVERRIDE = 'override'
    

    @http.route('/api/solocruceros-invoice-register', auth='user', type='json', methods=['POST'], csrf=False)
    def sc_api_invoice(self):
        try:
            body_data = json.loads(request.httprequest.data)
            _logger.info(body_data)

            if body_data.get('type', False):
                if body_data.get('type') == self.OPERATION_CREATE or body_data.get('type') == self.OPERATION_OVERRIDE:
                    return self.create_or_override(body_data)

                if body_data.get('type') == self.OPERATION_ADDPAY:
                    return self.addpay(body_data)
            else:
                raise exceptions.UserError("No se identificó el tipo de operación")
            
        except Exception as e:
            _logger.info(str(e))
            request.cr.rollback()
            return { 'status_code':500, 'message':'Error de tipo ' + str(e) }



    def validate_invoice(self, data):
        msg = ""

        # Validate for Account Move
        if data.get('type') == self.OPERATION_OVERRIDE:
            if not data.get('odoo_invoice_id', False):
                msg += 'Falta el valor de: odoo_invoice_id \r\n'
            elif not request.env['account.move'].search([('name','=',data.get('odoo_invoice_id'))]):
                msg += 'No se encontro la factura con Id: ' + str(data.get('odoo_invoice_id')) + '\r\n'

        msg += '' if data.get('partner_id', False) else 'Falta el valor de: partner_id \r\n'
        msg += '' if data.get('reserve_number', False) else 'Falta el valor de: reserve_number \r\n'
    
        # Validate for Account Move Line
        for index in range(len(data.get('invoice_lines', []))):
            
            if not data['invoice_lines'][index].get('product_id', False):
                msg += 'Linea: ' + str(index) + ': Falta el valor de: product_id \r\n'
            elif not request.env['product.template'].search([('id','=',data['invoice_lines'][index]['product_id'])]):
                msg += 'No se encontro el producto con Id: ' + str(data['invoice_lines'][index]['product_id']) + '\r\n'
            if not data['invoice_lines'][index].get('account_id', False):
                msg += 'Linea: ' + str(index) + ': Falta el valor de: account_id \r\n'
            elif not request.env['account.account'].search([('id','=',data['invoice_lines'][index]['account_id'])]):
                msg += 'No se encontro la cuenta con Id: ' + str(data['invoice_lines'][index]['account_id']) + '\r\n'

            msg += '' if data['invoice_lines'][index].get('label', False) else 'Linea: ' + str(index) + ': Falta el valor de: label \r\n'
            msg += '' if data['invoice_lines'][index].get('quantity', False) else 'Linea: ' + str(index) + ': Falta el valor de: quantity \r\n'
            #msg += '' if data['invoice_lines'][index].get('price', False) or data['invoice_lines'][index].get('price', False) == 0 else 'Linea: ' + str(index) + ': Falta el valor de: price \r\n'
            
        # Validate for Payments
        if data.get('odoo_invoice_id', False) and data.get('payment_list', False):
            msg += self.validate_payment(data)
        return msg
    
    def validate_payment(self, data):
        msg = ""
        if not data.get('odoo_invoice_id', False):
            msg += 'Falta el valor de: odoo_invoice_id \r\n'
        elif not request.env['account.move'].search([('name','=',data.get('odoo_invoice_id'))]):
            msg += 'No se encontro la factura con Id: ' + str(data.get('odoo_invoice_id')) + '\r\n'

        if msg == '':
            journals = self.get_all_journal()
            for index in range(len(data.get('payment_list', []))):
                    
                if not data['payment_list'][index].get('diario_de_pago', False):
                    msg += 'Linea pago: ' + str(index) + ': Falta el valor de: diario_de_pago \r\n'
                else:
                    journal_find = list(_data for _data in journals if _data['code'] == data['payment_list'][index]['diario_de_pago'])
                    if not journal_find:
                        msg += 'No se encontro el diario de pago con Id: ' + str(data['payment_list'][index]['diario_de_pago']) + '\r\n'
                    
                if data['payment_list'][index].get('monto_pagado', True) == True:
                    msg += 'Linea pago: ' + str(index) + ': Falta el valor de: monto_pagado \r\n'

                if data['payment_list'][index].get('fecha_pago', True) == True:
                    msg += 'Linea pago: ' + str(index) + ': Falta el valor de: fecha_pago \r\n'
        return msg



    def create_or_override(self, data):
        
        error_text = self.validate_invoice(data)
        if error_text != '':
            raise exceptions.UserError("Faltan los siguientes datos \r\n" +  error_text)
        
        ctx = (request.context.copy())
        ctx.update(check_move_validity=False)
        request.context = ctx

        if data.get('type', False) == self.OPERATION_CREATE:
            to_return = self.create_account(data)
            _logger.info(json.dumps(to_return))
            return { 'status_code':200, 'invoice_id': json.dumps(to_return), 'message':'success' }
        elif data.get('type', False) == self.OPERATION_OVERRIDE:
            to_return = self.create_rectification(data)
            _logger.info(json.dumps(to_return))
            return { 'status_code':200, 'invoice_id': json.dumps(to_return), 'message':'success' }
        
    def addpay(self, data):
        
        error_text = self.validate_payment(data)
        if error_text != '':
            raise exceptions.UserError("Faltan los siguientes datos \r\n" +  error_text)
        
        payments = self.create_payment(data)
        to_return = {
            'invoice': data.get('odoo_invoice_id'),
            'payments': payments,
        }
        
        _logger.info(json.dumps(to_return))
        return { 'status_code':200, 'invoice_id': json.dumps(to_return), 'message':'success' }



    def create_account(self, data):
        reserve_number = data.get('reserve_number', False)
        confirmation_date = self.get_datetime(data.get('confirmationDate')) if data.get('confirmationDate', False) else False
        partner_id = request.env['res.partner'].search([('id','=',data.get('partner_id'))]) if data.get('partner_id', False) else False
        journal_id = request.env['account.journal'].search([('type','=?','sale')], limit=1)

        # Check account
        self.check_client_account_receivable(partner_id, reserve_number)

        # Crea la Factura
        account_move = request.env['account.move'].create({
            'partner_id': partner_id.id,
            'ref': reserve_number,
            'invoice_date': confirmation_date,
            'journal_id': journal_id.id,
            'type': 'out_invoice'
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
                #'tax_ids': tax_id.ids,
                'price_unit': line['price'],
                'exclude_from_invoice_tab': False
            })
            account_move_line._onchange_product_id()
            account_move_line.name = line['label']
            account_move_line.account_id = line['account_id']
            account_move_line.quantity = line['quantity']
            account_move_line.price_unit = line['price']
            
            account_move_line._onchange_price_subtotal()
            account_move_line._onchange_credit()
            account_move_line._onchange_mark_recompute_taxes()
            
        account_move._onchange_invoice_line_ids()
        account_move.action_post()
        data['odoo_invoice_id'] = account_move.name

        # Crea sus pagos
        payments = self.create_payment(data)
        to_return = {
            'invoice': account_move.name,
            'payments': payments,
        }

        return to_return

    def create_rectification(self, data):
        move = request.env['account.move'].search([('name','=',data.get('odoo_invoice_id'))])
        payments = request.env['account.payment'].search([('invoice_ids','in',move.id)])

        default_values_list = []
        default_values_list.append(self._prepare_default_reversal(move))
        new_moves = move._reverse_moves(default_values_list, cancel=True)

        to_return = self.create_account(data)

        # Asignar pagos
        # for payment in payments:
        #     payment.invoice_ids = [(6, 0, [new_moves.id])]
        #     (new_moves[0] + payment.invoice_ids).line_ids.filtered(lambda line: not line.reconciled and line.account_id == payment.destination_account_id).reconcile()
        move_new = request.env['account.move'].search([('name','=',to_return.get('invoice'))])
        pay_term_line_ids = move_new.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
        
        domain = [('account_id', 'in', pay_term_line_ids.mapped('account_id').ids),
                    '|', ('move_id.state', '=', 'posted'), '&', ('move_id.state', '=', 'draft'), ('journal_id.post_at', '=', 'bank_rec'),
                    ('partner_id', '=', move_new.commercial_partner_id.id),
                    ('reconciled', '=', False), '|', ('amount_residual', '!=', 0.0),
                    ('amount_residual_currency', '!=', 0.0)]
        if move_new.is_inbound():
            domain.extend([('credit', '>', 0), ('debit', '=', 0)])
        else:
            domain.extend([('credit', '=', 0), ('debit', '>', 0)])
        
        lines = request.env['account.move.line'].search(domain)
        for _line in lines:
            lines = request.env['account.move.line'].browse(_line.id)
            lines += move_new.line_ids.filtered(lambda line: line.account_id == lines[0].account_id and not line.reconciled)
            lines.reconcile()


        #scApiInvoiceManagement' object has no attribute 'line_ids'
        # if move_new.invoice_ids:
        #     (moves[0] + rec.invoice_ids).line_ids \
        #                 .filtered(lambda line: not line.reconciled and line.account_id == rec.destination_account_id)\
        #                 .reconcile()

        # for payment in payments:
        #     payment.invoice_ids = [(6, 0, [move_new.id])]

        # #1
        # if rec.invoice_ids:
        #     (moves[0] + rec.invoice_ids).line_ids.filtered(lambda line: not line.reconciled and line.account_id == rec.destination_account_id).reconcile()
        # #2
        # lines = self.env['account.move.line'].browse(line_id)
        # lines += self.line_ids.filtered(lambda line: line.account_id == lines[0].account_id and not line.reconciled)
        # return lines.reconcile()


        return to_return

    def create_payment(self, data):
         # Crea sus pagos
        id_return = []
        if data.get('payment_list', False):
            account_move = request.env['account.move'].search([('name','=',data.get('odoo_invoice_id'))])
            currency = request.env['res.currency'].search([('name', '=', 'EUR')])
            payment_method_code = request.env['account.payment.method'].search([('code','=','manual'),('payment_type','=','inbound')])

            journals = self.get_all_journal()

            for payment in data['payment_list']:
                date_pay = self.get_datetime(payment['fecha_pago'])
                
                journal_find = list(_data for _data in journals if _data['code'] == payment['diario_de_pago'])
                
                _payment = request.env['account.payment'].with_context(active_ids=account_move.ids, active_model='account.move', active_id=account_move.id) \
                    .create({
                    'amount': payment['monto_pagado'],
                    'communication': account_move.name,
                    'currency_id': currency.id,
                    'journal_id': journal_find[0]['id'],
                    'partner_id': account_move.partner_id.id,
                    'partner_type': 'customer',
                    'payment_date': date_pay,
                    'hide_payment_method': True,
                    'payment_method_id': payment_method_code.id,
                    'payment_method_code': 'manual',
                    'payment_type': 'inbound',
                })
                _payment.post()
                id_return.append({ 'soloId': payment['soloId'], 'odooId': _payment.id })
                    
        return id_return


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
  
    def get_all_journal(self):
        journal_process = []
        journals = request.env['account.journal'].search([('id','>',0)])
        for journal in journals:
            if journal.bank_account_id and journal.bank_account_id.acc_number:
                code = journal.bank_account_id.acc_number.replace(" ", "")
                journal_process.append({ 'id': journal.id, 'code': code })
        return journal_process

    def check_client_account_receivable(self, partner_id, reserve_number):
        account_client = request.env['ir.config_parameter'].sudo().get_param('x_default_client_account_receivable')

        reserve_number = reserve_number.replace("-", "")
        if partner_id.property_account_receivable_id.code == account_client:
            account_default = request.env['account.account'].search([('code','=',account_client)])
            zero = 12 - len(reserve_number) - len("430")
            code = "430"
            for i in range(zero):
                code += "0"
            code += reserve_number
            
            account_check = request.env['account.account'].search([('code','=',code)])
            if not account_check:
                new_account = request.env['account.account'].create({
                    'code': code,
                    'name': partner_id.name,
                    'user_type_id': account_default.user_type_id.id,
                    'group_id': account_default.group_id.id,
                    'reconcile': account_default.reconcile,
                    'deprecated': account_default.deprecated,
                })
            else:
                new_account = account_check
                
            partner_id.write({
                'property_account_receivable_id': new_account.id
            })
