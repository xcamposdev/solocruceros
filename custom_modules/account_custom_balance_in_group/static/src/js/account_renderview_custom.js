odoo.define('account_custom_balance_in_group.account_renderview_custom', function (require) {
    'use strict';

    var accounts_reports = require('account_reports.account_report');

    accounts_reports.include({
        render_searchview_buttons: function() {
            this._super.apply(this, arguments);
            var self = this;
            this.$searchview_buttons.find('.js_account_report_bool_filter').unbind();
            this.$searchview_buttons.find('.js_account_report_bool_filter').click(function (event) {
                var option_value = $(this).data('filter');
                self.report_options[option_value] = !self.report_options[option_value];
                if (option_value === "unfold_all" && self.report_options[option_value] == true) {
                    self.report_options["group_account_type"] = false;
                }
                else if (option_value === "group_account_type" && self.report_options[option_value] == true) {
                    self.report_options["unfold_all"] = false;
                }
                if (option_value === 'unfold_all' || option_value === "group_account_type") {
                    self.unfold_all(self.report_options[option_value]);
                }
                self.reload();
            });
        }
    });

    return accounts_reports;
});