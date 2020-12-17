# -*- coding: utf-8 -*-
{
    'name': "Reporte Listado IVA",
    'version': '1.0.0.0',
    'author': "Develoop Software",
    'category': 'Uncategorized',
    'summary': 'Nuevo reporte listado IVA.',
    'website': "https://www.develoop.net/",
    'description': """
        - Nuevo reporte listado IVA
        """,
    'depends': ['base','account','sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/custom_report_list_iva.xml',
        'report/report_list_iva_print.xml',
        'report/list_iva_templates.xml',
    ],
    'demo': [],
    "images": ['static/description/icon.png'],
    "installable": True,
    "application": True,
    "auto_install": False,
}