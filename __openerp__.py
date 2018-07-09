# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Emails Inbox In Tree View',
    'version': '1.0',
    'summary': 'Emails Inbox In Tree View',
    'category': 'Social',
    'description':
        """
Emails Tree View
================

Emails Inbox In Tree View.
        """,
    'author': 'Michel Rheault, Osha',
    'website': "http://www.yourcompany.com",
    'license': 'AGPL-3',
    'depends' : ['mail', 'mail_full_expand', 'mail_forward', 'html_text'],
    'data' : [
        'views/assets.xml',
        'views/mail_message_view.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
}