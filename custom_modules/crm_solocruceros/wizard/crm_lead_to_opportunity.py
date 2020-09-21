# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class Lead2OpportunityPartner(models.TransientModel):

    _name = 'crm.lead2opportunity.partner'
    _description = 'Convert Lead to Opportunity without merge option'
    _inherit = 'crm.lead2opportunity.partner'

    @api.model
    def default_get(self, fields):
        """ Default get for name, opportunity_ids.
            If there is an exisitng partner link to the lead, find all existing
            opportunities links with this partner to merge all information together
        """
        result = super(Lead2OpportunityPartner, self).default_get(fields)
        if self._context.get('active_id'):
            #tomerge = {int(self._context['active_id'])}

            partner_id = result.get('partner_id')
            lead = self.env['crm.lead'].browse(self._context['active_id'])
            email = lead.partner_id.email if lead.partner_id else lead.email_from

            #tomerge.update(self._get_duplicated_leads(partner_id, email, include_lost=True).ids)

            if 'action' in fields and not result.get('action'):
                result['action'] = 'exist' if partner_id else 'create'
            if 'partner_id' in fields:
                result['partner_id'] = partner_id
            #if 'name' in fields:
                #result['name'] = 'merge' if len(tomerge) >= 2 else 'convert'
            #if 'opportunity_ids' in fields and len(tomerge) >= 2:
                #result['opportunity_ids'] = list(tomerge)
            if 'name' in fields:
                result['name'] = 'convert'
            if lead.user_id:
                result['user_id'] = lead.user_id.id
            if lead.team_id:
                result['team_id'] = lead.team_id.id
            if not partner_id and not lead.contact_name:
                result['action'] = 'nothing'
        return result

    name = fields.Selection([
        ('convert', 'Convert to opportunity')#,
       # ('merge', 'Merge with existing opportunities')
    ], 'Conversion Action', required=True)
    

    
    opportunity_ids = fields.Many2many('crm.lead', string='Opportunities')
    user_id = fields.Many2one('res.users', 'Salesperson', index=True)
    team_id = fields.Many2one('crm.team', 'Sales Team', oldname='section_id', index=True)


