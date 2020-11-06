# -*- coding: utf-8 -*-
import warnings
from odoo import api, fields, models, exceptions, _
from odoo.exceptions import AccessError, UserError, ValidationError

class crm_custom_auto_assignment(models.Model):

    _inherit = 'crm.lead'

    user_in_session = fields.Many2one('res.users','Usuario', default=lambda self: self._default_current_user_id())

    @api.model
    def _default_current_user_id(self):
        return self.env.user.id

    def Custom_Assign_Agent_logged(self):
        # Get parameter
        agent_logged = self.env['ir.config_parameter'].get_param('x_agent_logged_in_key')

        next_employee = self.env['hr.employee'].search(['&',('id','>', agent_logged),('last_check_out','=',False),('last_check_in', '!=', False)], order="id asc", limit=1)
        if(next_employee.id == False):
            self.env['ir.config_parameter'].set_param('x_agent_logged_in_key', 0)
            next_employee = self.env['hr.employee'].search(['&',('id','>', 0),('last_check_out','=',False),('last_check_in', '!=', False)], order="id asc", limit=1)
        
        if(next_employee.id != False):
            # select * From hr_attendance
            # eliminar el comercial de seguidores
            for follower in self.message_follower_ids:
                if(follower.partner_id == self.user_id.partner_id):
                    follower.unlink()
            
            # asignar comercial a seguidores
            #self.message_subscribe(next_employee.user_partner_id.ids, [])
            
            self.action = "exist" #'create','exist','nothing' 
            self.user_id = next_employee.user_id
            self.action_apply()

            # update last asign
            self.env['ir.config_parameter'].set_param('x_agent_logged_in_key', next_employee.id)

            # Notify to current user
            next_employee.user_id.notify_info(message='My information message', sticky=True)
            











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
            partner_id = self.with_context(active_id=lead_id)._find_matching_partner()
            action = 'create'
        result = self.env['crm.lead'].browse(lead_id).handle_partner_assignation(action, partner_id)
        return result.get(lead_id)

    def get_crm_lead_last_to_assign(self):
        lead_last = self.env['crm.lead'].search(['&',('id','>', 0),('type','=','lead')], order="id desc", limit=1)
        if(lead_last):
            return lead_last.id
        else:
            return 0

    def assign_new_lead(self):
        self.user_id = self.env.user.id
        res = self.convert_opportunity(self.partner_id.id, [], False)
        
        leads_to_allocate = self
        if self._context.get('no_force_assignation'):
            leads_to_allocate = leads_to_allocate.filtered(lambda lead: not self.user_id)
        if self.user_id:
            leads_to_allocate.allocate_salesman(self.user_id, team_id=self.team_id.id)

        return res


    def desasignarse(self):
        for follower in self.message_follower_ids:
            if(follower.partner_id == self.user_id.partner_id):
                follower.unlink()

        self.write({
            'user_id':False,
            'type':'lead'
        })