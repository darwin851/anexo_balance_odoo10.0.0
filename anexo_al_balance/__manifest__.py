# -*- coding: utf-8 -*-
{
    'name': "anexo_al_balance",

    'summary': """
        Reporte Anexos Al Balance Por NIF
    """,

    'description': """
        Reporte Anexos Al Balance Por NIF
    """,

    'author': "Ceiba - Cier",
    'website': "https://efossils.somxslibres.net/fossil/user/bit4bit/repository/odoo10_addons",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/report_partner_trial_balance.xml',
        'wizard/report_partner_trial_balance_view.xml',
        'views/report.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
