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
    def _get_body(self):
        for message in self:
            mybody = u"<hr/>" + message.body + u"<hr/>"
            url = None
            if message.res_id:
                url = '#id=%s&model=%s&view_type=form' % (
                    message.res_id,
                    message.model
                )

                title = _("Associated Model: ")
                url = u'<p><b> %s</b><a href="%s">%s</a></p>' % (title, url, message.record_name)
                mybody = mybody + url

            message.mybody = mybody

    @api.multi
    @api.depends('body')
    def _get_description_short(self):
        for message in self:
            truncated_text = self.env["ir.fields.converter"].text_from_html(
                message.body, 40, 100)

            url = None
            if message.res_id:
                url = '#id=%s&model=%s&view_type=form' % (
                    message.res_id,
                    message.model
                )

            about = message.about
            if url:
                about = '<a href="%s">%s</a>' % (url, about)

            message.short_description = "<h4 class \"oe_msg_title\">" + about + "</h4>" + u": " + truncated_text

    @api.multi
    @api.depends('res_id')
    def _get_model_url(self):
        res = {}
        for message in self:

            url = None
            if message.res_id:
                url = '#id=%s&model=%s&view_type=form' % (
                    message.res_id,
                    message.model
                )

                title = _("Associated Model: ")
                message.url = '<p><b>%s</b><a href="%s">%s</a></p>' % (title, url, message.record_name)

    @api.multi
    @api.depends('author_id')
    def _get_author(self):
        for message in self:
            author = message.author_id and message.author_id.name_get()[0][1]
            url = '#model=res.partner&amp;id={}'.format(message.author_id.id) if author else None
            image_src = '/web/binary/image?model=mail.message&amp;field=author_avatar&amp;id={}'.format(
                message.id)
            if author:
                message.author = '<a title={} href="{}"><img height="36px" src="{}"></a>'.format(author, url, image_src)
            else:
                message.author = message.email_from

    @api.multi
    @api.depends('author_id')
    def _get_about(self):
        for message in self:
            message.about = message.subject or message.record_name or 'UNDEFINED'

    short_description = fields.Char(string = "description", compute=_get_description_short, help='Message description: either the subject, or the beginning of the body', store=False)
    author = fields.Char(string="author", compute=_get_author, store=False)
    about = fields.Char(string="about", compute=_get_about, store=False)
    # url = fields.Char(string="url", compute=_get_model_url, store=False)
    mybody = fields.Html(string="Contents", help='Automatically sanitized HTML contents',
                         compute=_get_body, store=False)

    # todo date epoch arrondi sur le jour : pour groupby

#     @api.multi
#     @api.depends("to_read")
#     def _on_open_set_messages_read(self):
#         context = dict(self._context or {})
#         for message in self:
#             if message.parent_id.id:
#                 print (message.id, message.parent_id)
# #        self[0].set_message_read(True)  # only first not the parent (assume already be reed if parent)
# #        self.refresh()
#
#     on_open = fields.Integer(compute="_on_open_set_messages_read", store=False)

    @api.multi
    def toggle_messages_to_read(self):
        for message in self:
            to_read = message.to_read
            message.set_message_read(to_read)
            message.child_ids.set_message_read(to_read)
                # message.child_ids.refresh()
        # return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.multi
    def toggle_messages_starred(self):
        for message in self:
            message.set_message_starred(not message.starred)
        # return { 'type': 'ir.actions.client', 'tag': 'reload' }

    @api.multi
    def unset_messages_to_read(self):
        for message in self:
            message.set_message_read(False)
        #     message.child_ids.set_message_read(False)
        # return {'type': 'ir.actions.client', 'tag': 'reload'}
