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

    @api.multi
    def on_message_forward(self):
        res = self.env['ir.actions.act_window'].for_xml_id('mail_forward', 'compose_action')
        # Generate email subject as possible from record_name and subject
        subject = [_("FWD")] #[_t("FWD")];
        if self.record_name and self.parent_id: # ? record_name ?
            subject.append(self.record_name)
        if (self.subject) :
            subject.append(self.subject)
        else:
            if len(subject) < 2:
                subject.append("(No subject)")
        # Get only ID  from the attachments
        attachment_ids = []
        for n in self.attachment_ids:
            attachment_ids.append(self.attachment_ids[n].id)
        # Get necessary fields from the forwarded message
        header = [
            "----------" + _("Forwarded message") + "----------",
            _("From: ") + self.email_from, # author_id[1] = email_from
            _("Date: ") + self.date,
        ]
        if self.subject:
            header.append(_("Subject: ") + self.subject)
        # if self.email_to:
        #     header.append(_("To: ") + self.email_to) # in mail.mail not in mail.message
        # if self.email_cc:
        #     header.append(_("CC: ") + self.email_cc) # in mail.mail not in mail.message
        header = '<br/>'.join(html_escape(s) for s in header)

        context = {
            "default_attachment_ids": attachment_ids,
            "default_body":
                "<p><i>" + header + "</i></p><br/>" +
                self.body,
            "default_model": self.model,
            "default_res_id": self.res_id,
            "default_subject": ": ".join(subject)
        }
        if self.model and self.res_id:
            context["default_destination_object_id"] = ",".join([self.model, str(self.res_id)])
        res['context'] = context
        return res

    @api.multi
    def on_message_reply(self): # todo
        res = self.env['ir.actions.act_window'].for_xml_id('mail_forward', 'compose_action')
        # Generate email subject as possible from record_name and subject
        subject = [_("RE")]
        if self.record_name and self.parent_id: # ? record_name ?
            subject.append(self.record_name)
        if (self.subject) :
            subject.append(self.subject)
        else:
            if subject.length < 2:
                subject.append("(No subject)")
        # Get only ID  from the attachments
        attachment_ids = []
        for n in self.attachment_ids:
            attachment_ids.append(self.attachment_ids[n].id)
        # Get necessary fields from the forwarded message
        header = [
            "----------" + _("Reply message") + "----------",
            _("From: ") + self.email_from, # author_id[1] = email_from
            _("Date: ") + self.date,
        ]
        if self.subject:
            header.append(_("Subject: ") + self.subject)
        # if self.email_to:
        #     header.append(_("To: ") + self.email_to) # in mail.mail not in mail.message
        # if self.email_cc:
        #     header.append(_("CC: ") + self.email_cc) # in mail.mail not in mail.message
        header = '<br/>'.join(html_escape(s) for s in header)

        context = {
            "default_attachment_ids": attachment_ids,
            "default_body":
                "<p><i>" + header + "</i></p><br/>" +
                self.body,
            "default_model": self.model,
            "default_res_id": self.res_id,
            "default_subject": ": ".join(subject)
        }
        if self.model and self.res_id:
            context["default_destination_object_id"] = ",".join([self.model, str(self.res_id)])
        res['context'] = context
        return res

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
    def set_messages_read(self):
        active_ids = self.env.context.get('active_ids', [])
        mail = self.env['mail.message'].browse(active_ids)
        mail.set_message_read(read=True, create_missing=True)


    """
    voir section Widget Events and Properties :
    https://www.odoo.com/documentation/9.0/howtos/web.html
    """