# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ReportType(models.Model):
    """Configuration model for different report types."""
    _name = 'report.type'
    _description = 'Report Type Configuration'
    _order = 'menu_sequence, name'

    code = fields.Char(
        string='Technical Code',
        required=True,
        index=True,
        help='Technical identifier for this report type'
    )
    name = fields.Char(
        string='Display Name',
        required=True,
        help='User-friendly name for this report type'
    )
    csv_filename = fields.Char(
        string='CSV Filename',
        required=True,
        help='Expected CSV filename for this report type'
    )
    excel_template = fields.Text(
        string='Excel Template Configuration',
        help='JSON configuration for Excel formatting',
        default='{"headers": true, "autofit": true, "freeze_panes": "A2"}'
    )
    column_mappings = fields.Text(
        string='Column Mappings',
        help='JSON mapping of CSV columns to Excel columns',
        default='{"auto_map": true}'
    )
    validation_rules = fields.Text(
        string='Validation Rules',
        help='JSON configuration for data validation requirements',
        default='{"required_columns": [], "encoding": "utf-8"}'
    )
    menu_sequence = fields.Integer(
        string='Menu Order',
        default=10,
        help='Order in menu display'
    )

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Technical code must be unique'),
        ('csv_filename_unique', 'unique(csv_filename)', 'CSV filename must be unique'),
    ]

    @api.model
    def _setup_default_report_types(self):
        """Create default report type configurations."""
        default_types = [
            {
                'code': 'programs',
                'name': 'Educational Programs Report',
                'csv_filename': 'school_programs.csv',
                'menu_sequence': 10,
            },
            {
                'code': 'students',
                'name': 'Students Report',
                'csv_filename': 'school_students.csv',
                'menu_sequence': 20,
            },
            {
                'code': 'teachers',
                'name': 'Teachers Report',
                'csv_filename': 'school_teachers.csv',
                'menu_sequence': 30,
            },
            {
                'code': 'blocs',
                'name': 'Academic Blocs Report',
                'csv_filename': 'school_blocs.csv',
                'menu_sequence': 40,
            },
        ]

        for type_data in default_types:
            existing = self.search([('code', '=', type_data['code'])])
            if not existing:
                self.create(type_data)

    def get_report_config(self, report_code):
        """Get complete configuration for a report type."""
        report_type = self.search([('code', '=', report_code)], limit=1)
        if not report_type:
            return None

        return {
            'code': report_type.code,
            'name': report_type.name,
            'csv_filename': report_type.csv_filename,
            'excel_template': report_type.excel_template,
            'column_mappings': report_type.column_mappings,
            'validation_rules': report_type.validation_rules,
        }