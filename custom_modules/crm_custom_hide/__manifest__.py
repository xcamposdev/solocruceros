# -*- coding: utf-8 -*-
{
    'name': "crm_custom_hide",
    'version': "1",
    'author': "Develoop Software",
    'category': "CRM",
    'summary': "Remover la opción de 'Fusionar con oportunidad existente'",
    'website': "https://www.develoop.net/",
    'description': """
        - Se quitar la opción de 'Fusionar con oportunidad existente' al convertir una iniciativa en Oportunidad
    """,
    'depends': ['base','crm'],
    'data': [
        'views/crm_custom_hide.xml',
    ],
    'images': ['static/description/icon.png'],
    'demo': [], 
    'installable': True,
    'application': True,
    'auto_install': False,
}
