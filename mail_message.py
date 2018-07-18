# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tools import html2plaintext
from openerp import models, fields, api, _

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
}

def html_escape(text):
    return "".join(html_escape_table.get(c,c) for c in text)

class MailMessage(models.Model):
    _inherit = 'mail.message'

#         if (!this.do_check_attachment_upload()) {
#         return false;
#         }
#         var
#         recipient_done = $.Deferred();
#         if (this.is_log) {
#         recipient_done.resolve([]);
#
#     }
#     else {
#     recipient_done = this.check_recipient_partners();
#
# }
# $.when(recipient_done).done(function(partner_ids)
# {
#     var
# context = {
#     'default_parent_id': self.id,
#     'default_body': mail.ChatterUtils.get_text2html(self.$el ? (self.$el.find(
#     'textarea:not(.oe_compact)').val() | | ''): ''),
# 'default_attachment_ids': _.map(self.attachment_ids, function(file)
# {
# return file.id;}),
# 'default_partner_ids': partner_ids,
#                        'default_is_log': self.is_log,
#                                          'mail_post_autofollow': true,
#                                                                  'mail_post_autofollow_partner_ids': partner_ids,
#                                                                                                      'is_private': self.is_private,
# };
# if (default_composition_mode != 'reply' & & self.context.default_model & & self.context.default_res_id) {
# context.default_model = self.context.default_model;
# context.default_res_id = self.context.default_res_id;
# }
# if (self.context.option == 'forward'){
# context['option'] = 'forward';
# }
    @api.multi
    def on_message_forward(self):
        context = dict(self._context or {})
        if context['option'] == 'forward':
            subject = [_("Fwd")]
            header = [
                "----------" + _("Forwarded message") + "----------",
                _("From: ") + self.email_from,
                _("Date: ") + self.date,
            ]
        else:
            if context['option'] == 'reply':
                subject = [_("Re")]
                header = [
                    "----------" + _("Replyed message") + "----------",
                    _("From: ") + self.email_from,
                    _("Date: ") + self.date,
                ]

        if self.record_name and self.parent_id:
            subject.append(self.record_name)
        if self.subject:
            subject.append(self.subject)
        else:
            if len(subject) < 2:
                subject.append(_("No subject"))

        if self.subject:
            header.append(_("Subject: ") + self.subject)

        header = '<br/>'.join(html_escape(s) for s in header)

        context = {
            'default_parent_id': self.id,
            'default_body':
                "<p><i>" + header + "</i></p><br/>" +
                self.body,
            'default_attachment_ids': self.attachment_ids.ids,
            'default_partner_ids': self.partner_ids.ids,
            'mail_post_autofollow': True,
            'mail_post_autofollow_partner_ids': self.partner_ids.ids,
        }

        # private message: no model, no res_id
        is_private = False
        if not self.model or not self.res_id:
            is_private = True

        context["is_private"] = is_private

        if self.model:
            context["default_model"] = self.model
        if self.res_id:
            context["default_res_id"] = self.res_id

        if self.model and self.res_id:
            context["default_destination_object_id"] = ",".join([self.model, str(self.res_id)])

        action = self.env['ir.actions.act_window'].for_xml_id('mail_forward', 'compose_action')
        action['context'] = context
        return action

    @api.multi
    @api.depends('body')
    def _get_description_short(self):
        res = {}
        for message in self:
            truncated_text = self.env["ir.fields.converter"].text_from_html(
                message.body, 40, 100)

            if message.subject:
                message.short_description = message.subject + u": " + truncated_text
            else:
                message.short_description = truncated_text

    short_description = fields.Char(string = "description", compute=_get_description_short, help='Message description: either the subject, or the beginning of the body')

    # todo date epoch arrondi sur le jour : pour groupby

    # todo mark as read voir Mail Batch Read

    # totry : <button name="your_xml_act_window_name"  string="My Button"  confirm="Are you sure you want to delete this stuff???" />

    @api.multi
    @api.depends("to_read")
    def _on_open_set_messages_read(self):
        context = dict(self._context or {})
        print (self[0])
        for message in self:
            if message.parent_id.id:
                print (message.id, message.parent_id)
#        self[0].set_message_read(True)  # only first not the parent (assume already be reed if parent)
#        self.refresh()

    on_open = fields.Integer(compute="_on_open_set_messages_read", store=False)

    @api.multi
    def toogle_messages_to_read(self):
        for message in self:
            message.set_message_read(not message.to_read)
            message.refresh()

    @api.multi
    def toogle_messages_starred(self):
        for message in self:
            message.set_message_starred(not message.starred)
            message.refresh()

    @api.multi
    def myset_messages_to_read(self):
        for message in self:
            message.set_message_read(True)
            # message.message_id.child_ids.set_message_read(True)
            message.refresh()

    @api.multi
    def unset_messages_to_read(self):
        for message in self:
            message.set_message_read(False)
            message.refresh()

    # @api.multi
    # def set_messages_read(self):
    #     self.message_id.set_message_read(True)
    #     self.message_id.child_ids.set_message_read(True)

    """
    voir section Widget Events and Properties :
    https://www.odoo.com/documentation/9.0/howtos/web.html
    """
