# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2023 ito-invest.lu
#                       Jerome Sonnet <jerome.sonnet@ito-invest.lu>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    registration_open_year_id = fields.Many2one(
        comodel_name="school.year",
        string="Current Year for Registrations",
        readonly=False,
        help="Only registration in selected year is allowed.",
        config_parameter="school.registration_open_year_id",
    )

    registration_employee_id = fields.Many2one(
        comodel_name="res.partner",
        string="Employee Managing Registrations",
        readonly=False,
        help="The employee that manage/dispatch registrations.",
        config_parameter="school.registration_employee_id",
    )
