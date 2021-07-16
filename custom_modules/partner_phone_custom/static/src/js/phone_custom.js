odoo.define('partner_phone_custom.phone_custom_js', function (require) {
    "use strict";
    
    var BasicFieldCustom = require('web.basic_fields');
    var Phone = BasicFieldCustom.FieldPhone

    Phone.include({
        _renderReadonly: function () {
            var new_value = this.value;
            if (new_value != null && new_value != false)
                new_value = new_value.replace('+','00')

            this.$el.text(this.value)
                .addClass('o_form_uri o_text_overflow')
                .attr('href', this.prefix + ': ' + new_value);
            this.$el.removeClass('o_text_overflow');
        }
    });
});