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
import logging
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class IndividualBloc(models.Model):
    """Individual Bloc"""

    _inherit = "school.individual_bloc"

    student_signature = fields.Binary(string="Student Signature")

    student_signature_date = fields.Date(string="Student Signature Date")

    @api.onchange("student_signature")
    def onchange_student_signature(self):
        for rec in self:
            rec.student_signature_date = datetime.today()

    @api.onchange("course_group_ids")
    def on_change_course_group_ids(self):
        for rec in self:
            rec.student_signature = None
            rec.student_signature_date = None


class IndividualProgram(models.Model):
    """Individual Program"""

    _inherit = "school.individual_program"

    student_signature = fields.Binary(string="Student Signature", tracking=True)

    student_signature_date = fields.Date(string="Student Signature Date")

    @api.onchange("student_signature")
    def onchange_student_signature(self):
        for rec in self:
            rec.student_signature_date = datetime.today()

    def _assign_cg(self, new_pae):
        pass

        # TODO - Add 'Not Acquiered' cg automatic

        for group in new_pae.source_bloc_id.course_group_ids:
            # Check if cg already acquiered
            count = self.env["school.individual_course_group"].search_count(
                [
                    ("student_id", "=", self.student_id.id),
                    ("acquiered", "=", "A"),
                    ("source_course_group_id", "=", group.id),
                ]
            )
            if count == 0:
                _logger.info("Assign course groups : " + group.uid + " - " + group.name)
                cg = new_pae.course_group_ids.create(
                    {
                        "bloc_id": new_pae.id,
                        "source_course_group_id": group.id,
                        "acquiered": "NA",
                    }
                )
                courses = []
                for course in group.course_ids:
                    _logger.info("Assign course : " + course.name)
                    courses.append((0, 0, {"source_course_id": course.id}))
                cg.write({"course_ids": courses})
            else:
                _logger.info("Skip course groups : " + group.uid + " - " + group.name)

    def register_pae(self):
        self.ensure_one()
        context = dict(self._context or {})
        if not self.source_program_id:
            raise UserError(
                _("Pas de cycle théorique défini, impossible de proposer un PAE.")
            )

        if self.total_acquiered_credits < 45:
            # Register all UE from bloc 1 that are not yet acquiered
            new_pae = self.env["school.individual_bloc"].create(
                {
                    "student_id": context.get("default_student_id"),
                    "program_id": context.get("default_program_id"),
                    "year_id": self.env.user.current_year_id.id,
                    "source_bloc_id": self.source_program_id.bloc_ids[0].id,
                }
            )

            self._assign_cg(new_pae)

        elif (
            self.total_acquiered_credits < 110
            or len(self.source_program_id.bloc_ids) < 3
        ):
            # Register all UE that are not yet acquiered
            new_pae = self.env["school.individual_bloc"].create(
                {
                    "student_id": context.get("default_student_id"),
                    "program_id": context.get("default_program_id"),
                    "year_id": self.env.user.current_year_id.id,
                    "source_bloc_id": self.source_program_id.bloc_ids[1].id,
                }
            )

            self._assign_cg(new_pae)

        else:
            # Register all UE that are not yet acquiered
            new_pae = self.env["school.individual_bloc"].create(
                {
                    "student_id": context.get("default_student_id"),
                    "program_id": context.get("default_program_id"),
                    "year_id": self.env.user.current_year_id.id,
                    "source_bloc_id": self.source_program_id.bloc_ids[2].id,
                }
            )

            self._assign_cg(new_pae)

        value = {
            "domain": "[]",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "school.individual_bloc",
            "res_id": new_pae.id,
            "view_id": False,
            "context": context,
            "type": "ir.actions.act_window",
            "search_view_id": False,
        }
        return value
