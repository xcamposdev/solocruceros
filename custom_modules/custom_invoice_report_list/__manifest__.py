# -*- coding: utf-8 -*-
{
    'name': "Custom invoice report in list",
    'version': '1.0',
    'author': "Develoop Software",
    'category': 'Uncategorized',
    'summary': 'Agregar una nueva vista de tipo lista en reporte de facturas.',
    'website': "https://www.develoop.net/",
    'description': """
        Agregar una nueva vista de tipo lista en reporte de facturas.
        """,
    'depends': ['base','account'],
    'data': [
        'views/custom_invoice_report_list.xml',
        'report/invoice_report_list_print.xml',
        'report/invoice_list_template.xml',

    ],
    'qweb': [],
    'demo': [],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}