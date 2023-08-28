# -*- coding: utf-8 -*-
{
    'name': "Custom Partner Fields",
    'summary': """Custom Partner Fields""",
    
    'author': "Deuse",
    'website': "https://github.com/ito-invest-lu/horizon",
    'version': '16.0.1.0.1',

    'depends': ['base', 'school_management'],

    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
    ],
    'images': ['static/description/icon.png'],

    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
