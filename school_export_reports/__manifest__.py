# -*- coding: utf-8 -*-
{
    'name': 'School Export Reports',
    'version': '16.0.1.0.0',
    'category': 'Education',
    'summary': 'Generate Excel reports from CSV export data',
    'description': """
School Export Reports Addon
============================

This module generates Excel reports from existing CSV export files:
- school_programs.csv → Educational Programs Report
- school_students.csv → Students Report
- school_teachers.csv → Teachers Report
- school_blocs.csv → Academic Blocs Report

Features:
- CSV file validation with fail-fast error handling
- French character support (UTF-8 encoding)
- Excel report generation using xlsxwriter
- Report generation history and audit trail
- Menu integration with Odoo interface

Dependencies:
- school_management: Provides base educational data models
- report_xlsx: Enables Excel report generation framework
- xlsxwriter: Python library for Excel file creation
    """,
    'author': 'School Management Team',
    'website': '',
    'depends': ['base', 'school_management', 'report_xlsx'],
    'external_dependencies': {
        'python': ['xlsxwriter'],
    },
    'data': [
        'security/ir.model.access.csv',
        'data/system_parameters.xml',
        'data/ir_actions_report.xml',
        'views/export_report_views.xml',
        'views/res_config_settings_views.xml',
        'views/school_export_reports_menu.xml',
    ],
    'demo': [
        'demo/demo_reports.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}