odoo.define("web_notify.WebClient", function(require) {
    "use strict";

    var WebClient = require("web.WebClient");
    var session = require("web.session");
    var Dialog = require('web.Dialog');
    require("bus.BusService");

    // properties
    _audio: null,

    WebClient.include({
        show_application: function() {
            var res = this._super();
            this.start_polling();
            return res;
        },
        start_polling: function() {
            this.channel_success = "notify_success_" + session.uid;
            this.channel_danger = "notify_danger_" + session.uid;
            this.channel_warning = "notify_warning_" + session.uid;
            this.channel_info = "notify_info_" + session.uid;
            this.channel_default = "notify_default_" + session.uid;
            this.all_channels = [
                this.channel_success,
                this.channel_danger,
                this.channel_warning,
                this.channel_info,
                this.channel_default,
            ];
            this.call("bus_service", "addChannel", this.channel_success);
            this.call("bus_service", "addChannel", this.channel_danger);
            this.call("bus_service", "addChannel", this.channel_warning);
            this.call("bus_service", "addChannel", this.channel_info);
            this.call("bus_service", "addChannel", this.channel_default);
            this.call("bus_service", "on", "notification", this, this.bus_notification);
            this.call("bus_service", "startPolling");
        },
        bus_notification: function(notifications) {
            var self = this;
            _.each(notifications, function(notification) {
                var channel = notification[0];
                var message = notification[1];
                if (
                    self.all_channels !== null &&
                    self.all_channels.indexOf(channel) > -1
                ) {
                    self.on_message(message);
                }
            });
        },
        on_message: function(message) {
            /*return this.call("notification", "notify", {
                type: message.type,
                title: message.title,
                message: message.message,
                sticky: message.sticky,
                className: message.className,
            }); */
            var self =this;
            var dialog = new Dialog(this, {
                title: 'Información',
                size: 'medium',
                $content: ("<div style='font-size:14px;font-family:Helvetica, Arial, sans-serif;'>" + message.message + "</div>"),
                buttons: [{
                    text: ('Ok'),
                    classes: "btn-primary",
                    close: true,
                    click: function () {
                        //location.reload();
                        self._rpc({
                            model: "ir.model.data",
                            method: 'get_object_reference',
                            args: ['crm', 'crm_lead_view_form']
                        }).then(function (result) {
                            self.do_action({
                                name: "flujo",
                                type: 'ir.actions.act_window',
                                res_model: 'crm.lead',
                                views: [[result[1], 'form']],
                                view_mode: 'form',
                                res_id: message.record_id
                            });
                        });
                    },
                }],
            }).open();
            this._beep();

        },
        _beep: function() {
            if (typeof(Audio) !== "undefined") {
                if (!this._audio) {
                    this._audio = new Audio();
                    var ext = this._audio.canPlayType("audio/ogg; codecs=vorbis") ? ".ogg" : ".mp3";
                    var session = this.getSession();
                    this._audio.src = session.url("/mail/static/src/audio/ting" + ext);
                }
                Promise.resolve(this._audio.play()).catch(_.noop);
            }
        }
    });
});
