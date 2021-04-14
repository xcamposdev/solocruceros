odoo.define('custom_invoice_report_list.dataExport_custom.js', function (require) {
    "use strict";

    var DataExport = require('web.DataExport');

    var IncludeListView = {
        _exportData: function() {
            if(this.record.model == "account.invoice.report" && this.record.viewType == "list")
            {    
                this.record.model = "account.invoice.report2";
            }
            this._super.apply(this, arguments);
            
            if(this.record.model == "account.invoice.report2" && this.record.viewType == "list")
            {
                this.record.model = "account.invoice.report";
            }
        }
    }

    return DataExport.include(IncludeListView);
});