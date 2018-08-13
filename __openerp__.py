# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Emails In Tree View',
    'version': '1.0',
    'summary': 'Emails In Tree View',
    'category': 'Social',
    'description':
        """
Emails Tree View
================

Emails in Tree View, so we can group by author.

        """,
    'author': 'Michel Rheault, Osha',
    'license': 'AGPL-3',
    'depends' : [
        'base',
        'mail',
        'mail_extend',
        'mail_full_expand',
        'mail_forward',
        'html_text',
        'web_list_html_widget'
    ],
    'data' : [
        'views/assets.xml',
        'views/mail_message_view.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': True,
}