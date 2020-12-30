# -*- coding: utf-8 -*-
{
    'name': "im livechat custom web",
    'version': '0.1',
    'author': "Develoop Software",
    'category': 'Uncategorized',
    'summary': 'Live chat custom',
    'website': "https://www.develoop.net/",
    'description': """
        - Se modifica carga de librerias para que pueda integrarse con solo cruceros
        """,
    'depends': ['im_livechat', 'mail'],
    'data': [
        'views/im_livechat_template_custom.xml',
    ],
    'qweb': [
        "views/im_livechat_x_custom.xml",
    ],
    'demo': [],
    'installable': True,
}