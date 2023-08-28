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

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class CourseGroup(models.Model):
    """Course Group"""

    _inherit = "school.course_group"

    type = fields.Selection(
        [
            ("CHOIX", "CHOIX"),
            ("ORI1", "ORI1"),
            ("ORI2", "ORI2"),
            ("OBLIGATOIRE", "OBLIGATOIRE"),
        ],
        string="Type",
    )

    is_choice_course_group = fields.Boolean(
        string="Is Choice Course Group", default=False
    )

    total_credits_to_select = fields.Integer(string="Total Credits to Select")
    total_hours_to_select = fields.Integer(string="Total Hours to Select")
    total_weight_to_select = fields.Integer(string="Total Weight to Select")

    @api.depends(
        "course_ids",
        "is_choice_course_group",
        "total_credits_to_select",
        "total_hours_to_select",
        "total_weight_to_select",
    )
    def _get_courses_total(self):
        for rec in self:
            if rec.is_choice_course_group:
                rec.total_hours = rec.total_hours_to_select
                rec.total_credits = rec.total_credits_to_select
                rec.total_weight = rec.total_weight_to_select
            else:
                super(CourseGroup, rec)._get_courses_total()


class IndividualBloc(models.Model):
    """Individual Bloc"""

    _inherit = "school.individual_bloc"

    def action_select_choice_cg(self):
        pass


class Bloc(models.Model):
    """Bloc"""

    _inherit = "school.bloc"

    @api.depends(
        "course_group_ids.total_hours",
        "course_group_ids.total_credits",
        "course_group_ids.total_weight",
        "course_group_ids.type",
    )
    def _get_courses_total(self):
        for rec in self:
            total_hours = 0.0
            total_credits = 0.0
            total_weight = 0.0
            has_sum_type = []
            for course_group in rec.course_group_ids:
                if course_group.type == "OBLIGATOIRE":
                    total_hours += course_group.total_hours
                    total_credits += course_group.total_credits
                    total_weight += course_group.total_weight
                elif course_group.type == "CHOIX":
                    if course_group.type in has_sum_type:
                        pass
                    else:
                        # Need to select two of those course groups
                        has_sum_type.append(course_group.type)
                        total_hours += 60
                        total_credits += 6
                        total_weight += 2
                elif course_group.type == "ORI1":
                    if course_group.type in has_sum_type:
                        pass
                    else:
                        # Need to select two of those course groups
                        has_sum_type.append(course_group.type)
                        total_hours += 60
                        total_credits += 10
                        total_weight += 4
                else:
                    if course_group.type in has_sum_type:
                        pass
                    else:
                        # Need to select two of those course groups
                        has_sum_type.append(course_group.type)
                        total_hours += 30
                        total_credits += 4
                        total_weight += 2
            rec.total_hours = total_hours
            rec.total_credits = total_credits
            rec.total_weight = total_weight
