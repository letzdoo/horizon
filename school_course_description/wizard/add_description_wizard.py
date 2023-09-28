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

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AddDescriptionWizard(models.TransientModel):
    _name = "school.add_description_wizard"
    _description = "Add Description Wizard"

    course_id = fields.Many2one("school.course", string="Course", required=True)

    author_id = fields.Many2one(
        "res.users",
        string="Author",
        default=lambda self: self.env.user.id,
    )

    filter_authors = fields.Boolean(
        string="Filter Authors",
        default=True,
    )

    @api.onchange("filter_authors")
    def onchange_filter_authors(self):
        if self.filter_authors:
            return {
                "domain": {"documentation_id": [("author_id", "=", self.author_id.id)]}
            }
        else:
            return {"domain": {"documentation_id": []}}

    documentation_id = fields.Many2one(
        "school.course_documentation", string="Use Existing Documentation"
    )

    def action_use_existing(self):
        if self.documentation_id:
            self.documentation_id.course_ids |= self.course_id
        return {
            "type": "ir.actions.act_window_close",
        }

    def action_create_new(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "school.course_documentation",
            "view_mode": "form",
            "target": "current",
            "flags": {"form": {"action_buttons": True}},
            "context": {"default_course_id": self.course_id.id},
        }
