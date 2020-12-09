odoo.define('invoice.action_button', function (require) {
    "use strict";

    var Dialog = require('web.Dialog');
    var core = require('web.core');
    var KanbanController = require('web.KanbanController');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var _t = core._t;
    KanbanController.include({
        renderButtons: function($node) {
        this._super.apply(this, arguments);
            if (this.modelName === "crm.lead" && this.viewType === "kanban") {
                if (this.$buttons) {
                    this.$buttons.find('.oe_action_new_lead_button').click(this.proxy('action_new_lead'));
                }
            }
        },

        action_new_lead: function () {
            var self = this
            var _context = self.initialState.context;
            
            rpc.query({
                model: 'crm.lead',
                method: 'get_crm_lead_last_to_assign',
                args: [{}],
                kwargs: { context: {
                    'lang': _context.lang,
                    'tz': _context.tz,
                    'uid': _context.uid,
                    'allowed_company_ids': _context.allowed_company_ids,
                }},
            }).then(function (e) {
                if (e === 0)
                {
                    var dialog = new Dialog(this, {
                        title: 'Información',
                        size: 'medium',
                        $content: _t("<div style='font-size:14px;font-family:Helvetica, Arial, sans-serif;'>No existe iniciativas disponibles.</div>"),
                        buttons: [{
                            text: _t('Ok'),
                            classes: "btn-primary",
                            close: true
                        }],
                    }).open();
                }
                else
                {
                    rpc.query({
                        model: 'crm.lead',
                        method: 'assign_new_lead',
                        args: [e],
                        kwargs: { context: {
                            'lang': _context.lang,
                            'tz': _context.tz,
                            'uid': _context.uid,
                            'allowed_company_ids': _context.allowed_company_ids,
                            'active_model': 'crm.lead',
                            'active_id': e,
                            'active_ids': [e]
                        }},
                    }).then(function (ev) {
                        location.reload();
                    });
                }
            });
            return;
        },
    })
});