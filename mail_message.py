# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tools import html2plaintext
from openerp import models, fields, api


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.multi
    @api.depends('body')
    def _get_description_short(self):
        res = {}
        for message in self:
            if message.subject:
                message.shortdescription = message.subject
            else:
                plaintext_ct = '' if not message.body else html2plaintext(message.body)
                message.shortdescription = plaintext_ct[:100] + '%s' % (' [...]' if len(plaintext_ct) >= 100 else '')

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