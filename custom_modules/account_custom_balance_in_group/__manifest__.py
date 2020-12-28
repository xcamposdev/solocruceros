# -*- coding: utf-8 -*-
{
    'name': "Agrupar cuentas en balance",
    'version': '1.0',
    'author': "Develoop Software",
    'category': 'Uncategorized',
    'summary': 'Agrupar cuentas en listado de balance.',
    'website': "https://www.develoop.net/",
    'description': """
        - Agrupar cuentas en listado de balance
        """,
    'depends': ['base','account_reports','account_accountant', 'account'],
    'data': [
        'views/account_custom_balance_in_group.xml',
        'views/assets.xml',
        "static/src/xml/qweb.xml",
    ],
    'demo': [],
    "images": ['static/description/icon.png'],
    "installable": True,
    "application": True,
    "auto_install": False,
}