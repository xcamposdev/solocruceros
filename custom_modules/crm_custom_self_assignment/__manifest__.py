# -*- coding: utf-8 -*-
{
    'name': "crm_custom_auto_assignment",
    'version': '0.1',
    'author': "Develoop Software",
    'category': 'Uncategorized',
    'summary': 'Auto-asignación de cliente',
    'website': "https://www.develoop.net/",
    'description': """
        - Auto-asigna cuando no hay agentes logados, y cuando hay agentes logados
        """,
    'depends': ['base','crm', 'hr'],
    'data': [
        'views/crm_custom_auto_assignment.xml',
        'views/assets.xml',
    ],
    'qweb': [
        "static/src/xml/crm_custom_auto_assignment_qweb.xml",
    ],
    'demo': [],
    'installable': True,
}