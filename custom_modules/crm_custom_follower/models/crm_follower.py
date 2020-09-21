# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError


class crm_custom_follower(models.Model):

    _inherit = 'crm.lead'

    @api.model
    def create(self, vals):
        _followers = []
        if(vals['partner_id'] is not None and vals['partner_id'] != False and vals['partner_id'] != self.env.user.partner_id.id):
            _followers.append(vals['partner_id'])
        if(vals['user_id'] is not None and vals['user_id'] != False and vals['user_id'] != self.env.user.id):
            user_partner_id = self.env['res.users'].search([('id','=',vals['user_id'])])
            _followers.append(user_partner_id.partner_id.id)
        
        default_followers = []
        if(len(_followers) > 0):
            default_followers = self.env['mail.followers']._add_default_followers(self._name, [], _followers, customer_ids=[])[0][0]
            vals['message_follower_ids'] = [(0, 0, fol_vals) for fol_vals in default_followers]
        
        return_value = super(crm_custom_follower, self.with_context()).create(vals)
        
        for follower in return_value['message_follower_ids']:
            if(follower.partner_id != return_value.partner_id and follower.partner_id != return_value.user_id.partner_id):
                follower.unlink()

        return return_value