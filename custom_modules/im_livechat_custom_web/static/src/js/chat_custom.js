odoo.define('sc_api_invoice_management.chat_custom.js', function (require) {
    "use strict";

    var AbstractThreadWindow = require('mail.AbstractThreadWindow');

    var LivechatWindow = AbstractThreadWindow.extend({
        events: _.extend(AbstractThreadWindow.prototype.events, {
            'click .o_thread_window_close': '_onClickClose_custom',
        }),

        _onClickClose_custom: function() {
            alert("DIO");
        },
    });
    
    return LivechatWindow;
});