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
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class AddBlocWizard(models.TransientModel):
    _name = "school.add_bloc_wizard"
    _description = "Add Bloc Wizard"

    individual_program_id = fields.Many2one(
        "school.individual_program", string="Target Program"
    )

    year_id = fields.Many2one("school.year", string="Year")

    source_bloc_id = fields.Many2one("school.bloc", string="Source Bloc")

    def on_confirm(self):
        self.ensure_one()
        self.env["school.individual_course_summary"]
        for cg in self.source_bloc_id.course_group_ids:
            course_group_summary = self.env["school.individual_course_summary"].create(
                {
                    "program_id": self.individual_program_id.id,
                    "course_group_id": cg.id,
                }
            )
        return {
            "warning": {
                "title": "Add Bloc Wizard completed",
                "message": "Program have been updated with all UE from %s."
                % (self.source_bloc_id.title),
            }
        }

    def on_cancel(self):
        self.ensure_one()
        self.target_first_course_group_id.unlink()
        self.target_second_course_group_id.unlink()
        return {"type": "ir.actions.act_window_close"}
