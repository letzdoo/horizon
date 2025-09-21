# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    csv_export_path = fields.Char(
        string='CSV Export Path',
        help='Directory path where CSV export files are stored',
        config_parameter='school_export_reports.csv_export_path'
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            csv_export_path=self.env['ir.config_parameter'].sudo().get_param(
                'school_export_reports.csv_export_path', '/tmp/odoo_exports'
            )
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'school_export_reports.csv_export_path',
            self.csv_export_path or '/tmp/odoo_exports'
        )