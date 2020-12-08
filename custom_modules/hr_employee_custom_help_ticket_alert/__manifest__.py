# -*- coding: utf-8 -*-
{
    'name': "Alerta de ticket",
    'version': '1.0',
    'author': "Develoop Software",
    'category': 'Uncategorized',
    'summary': 'Alerta de ticket no respondido.',
    'website': "https://www.develoop.net/",
    'description': """
        - Alerta a un agente de que tiene un ticket de ayuda sin cambiar de estado por 10 o mas dias
        """,
    'depends': ['base','helpdesk','hr_attendance', 'mail'],
    'data': [
        'views/hr_employee_custom_help_ticket_alert.xml',
    ],
    'demo': [],
    "images": ['static/description/icon.png'],
    "installable": True,
    "application": True,
    "auto_install": False,
}