# -*- coding: utf-8 -*-
import warnings
import logging
from odoo import api, fields, models, exceptions, _
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)


class crm_custom_auto_assignment(models.Model):

    _inherit = 'crm.lead'

    user_in_session = fields.Many2one('res.users','Usuario', default=lambda self: self._default_current_user_id())
    

    @api.model
    def _default_current_user_id(self):
        return self.env.user.id

    def Custom_Assign_Agent_logged(self):
        if not self.user_id:
            # Get parameter
            agent_logged = self.env['ir.config_parameter'].sudo().get_param('x_agent_logged_in_key')

            next_employee = self.env['hr.employee'].sudo().search(['&',('id','>', agent_logged),('last_check_out','=',False),('last_check_in', '!=', False), ('x_oportunity_notification', '=', 'si')], order="id asc", limit=1)
            if(next_employee.id == False):
                self.env['ir.config_parameter'].sudo().set_param('x_agent_logged_in_key', 0)
                next_employee = self.env['hr.employee'].sudo().search(['&',('id','>', 0),('last_check_out','=',False),('last_check_in', '!=', False), ('x_oportunity_notification', '=', 'si')], order="id asc", limit=1)
            
            if(next_employee.id != False):
                # select * From hr_attendance
                # eliminar el comercial de seguidores
                
                # asignar comercial a seguidores
                #self.message_subscribe(next_employee.user_partner_id.ids, [])
                
                self.action = "exist" #'create','exist','nothing' 
                self.user_id = next_employee.user_id
                self.action_apply()
                
                for follower in self.sudo().message_follower_ids:
                    if(follower.partner_id != self.sudo().user_id.partner_id and self.partner_id != follower.partner_id):
                        follower.unlink()

                # assign new client follower
                list_id = []
                list_id.append(self.sudo().partner_id.id)            
                self.message_subscribe(partner_ids=list_id)

                # update last asign
                self.env['ir.config_parameter'].sudo().set_param('x_agent_logged_in_key', next_employee.id)

                # Notify to current user
                next_employee.user_id.notify_info(message='Se ha agregado una nueva oportunidad y ha sido asignada a ti.', sticky=True, record_id=self.id)
        else: 
                for follower in self.sudo().message_follower_ids:
                    if(follower.partner_id != self.sudo().user_id.partner_id and self.partner_id != follower.partner_id):
                        follower.unlink()

                # assign new client follower
                list_id = []
                list_id.append(self.sudo().partner_id.id)            
                self.message_subscribe(partner_ids=list_id)

                # update last asign
                self.env['ir.config_parameter'].sudo().set_param('x_agent_logged_in_key', self.user_id)

                # Notify to current user
                self.user_id.notify_info(message='Se ha agregado una nueva oportunidad y ha sido asignada a ti.', sticky=True, record_id=self.id)
            

    def search(self, args, offset=0, limit=None, order=None, count=False):
        if args:
            if ['type', '=', 'opportunity'] in args:
                stage_id = list(_arg[2] for _arg in args if _arg[0] == "stage_id" and len(_arg) == 3)
                if(stage_id):
                    stage = self.env['crm.stage'].search([('id','=',stage_id)])
                    if(stage.name == 'Nuevo'):
                        order = 'date_open desc'

        res = self._search(args, offset=offset, limit=limit, order=order, count=count)
        return res if count else self.browse(res)

    def action_apply(self):
        self.ensure_one()
        values = {
            'team_id': self.team_id.id,
        }

        if self.partner_id:
            values['partner_id'] = self.partner_id.id

        if self.name == 'merge':
            leads = self.with_context(active_test=False).opportunity_ids.merge_opportunity()
            if not leads.active:
                leads.write({'active': True, 'activity_type_id': False, 'lost_reason': False})
            if leads.type == "lead":
                values.update({'lead_ids': leads.ids, 'user_ids': [self.user_id.id]})
                self.with_context(active_ids=leads.ids)._convert_opportunity(values)
            elif not self._context.get('no_force_assignation') or not leads.user_id:
                values['user_id'] = self.user_id.id
                leads.write(values)
        else:
            leads = self.env['crm.lead'].browse(self._context.get('active_ids', []))
            values.update({'lead_ids': leads.ids, 'user_ids': [self.user_id.id]})
            self._convert_opportunity(values)
        
    def _convert_opportunity(self, vals):
        self.ensure_one()

        res = False

        leads = self.env['crm.lead'].browse(vals.get('lead_ids'))
        for lead in leads:
            self_def_user = self.with_context(default_user_id=self.user_id.id)

            partner_id = False
            if self.action != 'nothing':
                partner_id = self_def_user._create_partner(
                    lead.id, self.action, vals.get('partner_id') or lead.partner_id.id)

            res = lead.convert_opportunity(partner_id, [], False)
        user_ids = vals.get('user_ids')

        leads_to_allocate = leads
        if self._context.get('no_force_assignation'):
            leads_to_allocate = leads_to_allocate.filtered(lambda lead: not lead.user_id)

        if user_ids:
            leads_to_allocate.allocate_salesman(user_ids, team_id=(vals.get('team_id')))

        return res

    def _create_partner(self, lead_id, action, partner_id):
        """ Create partner based on action.
            :return dict: dictionary organized as followed: {lead_id: partner_assigned_id}
        """
        #TODO this method in only called by Lead2OpportunityPartner
        #wizard and would probably diserve to be refactored or at least
        #moved to a better place
        if action == 'each_exist_or_create':
            partner_id = self.sudo().with_context(active_id=lead_id)._find_matching_partner()
            action = 'create'
        result = self.env['crm.lead'].browse(lead_id).handle_partner_assignation(action, partner_id)
        return result.get(lead_id)

    def get_crm_lead_last_to_assign(self):
        lead_last = self.env['crm.lead'].sudo().search(['&',('id','>', 0),('type','=','lead')], order="id desc", limit=1)
        if(lead_last):
            return lead_last.id
        else:
            return 0

    def assign_new_lead(self):
        self.sudo().user_id = self.env.user.id
        res = self.sudo().convert_opportunity(self.partner_id.id, [], False)
        
        leads_to_allocate = self
        if self.sudo()._context.get('no_force_assignation'):
            leads_to_allocate = leads_to_allocate.filtered(lambda lead: not self.user_id)
        if self.sudo().user_id:
            leads_to_allocate.allocate_salesman(self.user_id, team_id=self.team_id.id)

        return res


    def desasignarse(self):
        for follower in self.sudo().message_follower_ids:
            if(follower.partner_id == self.user_id.partner_id):
                follower.unlink()

        self.write({
            'user_id':False,
            'type':'lead'
        })

class hr_employee_opportunity_custom(models.Model):

    _inherit = 'hr.employee'

    x_oportunity_notification = fields.Selection([
        ('si','Si'),
        ('no','No')
        ], string = "Recibir Oportunidades", default='no') 