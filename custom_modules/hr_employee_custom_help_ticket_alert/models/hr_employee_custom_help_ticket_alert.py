# -*- coding: utf-8 -*-
import warnings
import logging
from datetime import datetime
from odoo import api, fields, models, exceptions, _
from odoo.exceptions import AccessError, UserError, ValidationError
_logger = logging.getLogger(__name__)

class hr_employee_custom_help_ticket_alert(models.Model):

    _inherit = 'hr.employee'

    def attendance_manual(self, next_action, entered_pin=None):
        self.ensure_one()
        can_check_without_pin = not self.env.user.has_group('hr_attendance.group_hr_attendance_use_pin') or (self.user_id == self.env.user and entered_pin is None)
        if can_check_without_pin or entered_pin is not None and entered_pin == self.sudo().pin:

            #################################################
            have_tickets = self.env['helpdesk.ticket'].sudo().search(['&',('user_id','=',self.env.user.id), ('active', '=', True)], order="id asc")
            for have_ticket in have_tickets:
                days = '0'
                if(have_ticket):
                    today = datetime.today()
                    last_update_days = (today - have_ticket.date_last_stage_update).days

                    if (last_update_days >= 10 and last_update_days < 30 and have_ticket.x_is_sending_10 == False and self.env.user.attendance_state == 'checked_out'):
                        #enviar email si tiene ticket  
                        days = 10
                        self.send_notification(have_ticket, days)
                        # Enviar alert
                        self.user_id.notify_info(message='Tienes un ticket que debe ser atendido de manera urgente.', sticky=True)
                    elif (last_update_days >= 30 and have_ticket.x_is_sending_30 == False and self.env.user.attendance_state == 'checked_out'):
                        #enviar email si tiene ticket  
                        days = 30
                        self.send_notification(have_ticket, days)
                        # Enviar Alert
                        self.user_id.notify_info(message='Tienes un ticket que debe ser atendido de manera urgente.', sticky=True)
            ##############################################

            return self._attendance_action(next_action)
        return {'warning': _('Wrong PIN')}
    
    def send_notification(self, ticket, days):
        self.ensure_one()
        email_tmp_id = self.env.ref('hr_employee_custom_help_ticket_alert.email_template_ticket_alert').id
        email_tmp = self.env['mail.template'].browse(email_tmp_id)
        x_reservas_email = self.env['ir.config_parameter'].sudo().get_param('x_email_solocruceros_reservas')

        if(email_tmp):
            values = email_tmp.generate_email(self.id, fields=None)
            values['email_to'] = x_reservas_email
            values['email_from'] = x_reservas_email
            values['subject'] = 'Ticket con nombre ' + ticket.name + ' asignado a ti, hace ' + str(days) + ' dias que no cambia de etapa.'
            values['res_id'] = False

            if values['email_to'] and values['email_from']:
                mail_mail_obj = self.env['mail.mail']
                msg_id = mail_mail_obj.create(values)
            
                if msg_id:
                    mail_mail_obj.send(msg_id)
                    if(days == 10):
                        ticket.write({ 'x_is_sending_10': True })
                    if(days == 30):
                        ticket.write({ 'x_is_sending_30': True })


class helpdesk_ticket_custom_help_ticket_alert(models.Model):

    _inherit = 'helpdesk.ticket'

    x_is_sending_10 = fields.Boolean("Es 10 dias", default=False)
    x_is_sending_30 = fields.Boolean("Es 30 dias", default=False)