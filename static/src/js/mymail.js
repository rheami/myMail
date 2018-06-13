console.log("I'm here!!");
openerp.mymail = function (instance, local) {

    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    var self = this;

    console.log("loading my module...mymail");
    openerp.web.ListView.include({
        load_list: function(data) {
           this._super(data);
           if (this.$buttons) {
               this.$buttons.find('.oe_custom_button').off().click(this.proxy('do_the_job')) ;
               console.log('Creer un nouveau email button method call...');
           }
        },
        do_the_job: function () {
            this.do_action({
                type: "ir.actions.act_window",
                name: "Сreer un nouveau email",
                res_model: "mail.message",
                views: [[false,'form']],
                target: 'current',
                view_type : 'form',
                view_mode : 'form',
                flags: {'form': {'action_buttons': true, 'options': {'mode': 'edit'}}}
                });
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        }
    });

};