# -*- coding: utf-8 -*-
{
    'name': "Cliente campo nuevo NIE",
    'version': "1",
    'author': "Develoop Software",
    'category': "Partner",
    'summary': "Añade un campo para DNI, Pasaporte o NIE",
    'website': "https://www.develoop.net/",
    'description': """
        Añade un campo para DNI, Pasaporte o NIE
    """,
    'depends': ['base'],
    'data': [
        'views/res_partner_custom.xml',
    ],
    'images': ['static/description/icon.png'],
    'demo': [], 
    'installable': True,
    'auto_install': False,
}
