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

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class IndividualCourseSummary(models.Model):
    """IndividualCourse Summary"""

    _inherit = "school.individual_course_summary"

    def action_open_form(self):
        self.ensure_one()
        for cg in self.ind_course_group_ids:
            if cg.state in ["2_candidate", "1_1_checked", "1_confirmed", "0_valuated"]:
                valuation_followup = self.env["school.valuation_followup"].search(
                    [("individual_course_group_id", "=", cg.id)]
                )
                if valuation_followup:
                    return {
                        "type": "ir.actions.act_window",
                        "name": _(valuation_followup.name),
                        "res_model": valuation_followup._name,
                        "res_id": valuation_followup.id,
                        "view_mode": "form",
                    }
        return {
            "type": "ir.actions.act_window",
            "name": _(self.name),
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
        }

    def action_reject_course_group(self):
        for rec in self:
            for cg in rec.individual_course_group.ids:
                if cg.state in ["2_candidate", "1_confirmed", "1_1_checked"]:
                    cg.write({"state", "3_rejected"})
        return {
            "type": "ir.actions.act_view_reload",
        }

    def action_candidate_valuate_course_group(self):
        for rec in self:
            valuated_cg = self.env["school.individual_course_group"].create(
                {
                    "valuated_program_id": rec.program_id.id,
                    "source_course_group_id": rec.course_group_id.id,
                    "state": "2_candidate",
                    "year_id": self.env.user.current_year_id.id,
                }
            )
            rec.program_id.valuated_course_group_ids |= valuated_cg
            self.env["school.valuation_followup"].create(
                {"individual_course_group_id": valuated_cg.id}
            )
        return {
            "type": "ir.actions.act_view_reload",
        }


class IndividualCourseGroup(models.Model):
    """Individual Course Group"""

    _inherit = "school.individual_course_group"

    valuation_followup = fields.Many2one(
        "school.valuation_followup",
        string="Valuation Followup",
        compute="_compute_valuation_followup",
    )

    def _compute_valuation_followup(self):
        for rec in self:
            followup_id = self.env["school.valuation_followup"].search(
                [
                    ("individual_course_group_id", "=", rec.id),
                    ("state", "=", "0_valuated"),
                ]
            )
            if followup_id:
                rec.valuation_followup = followup_id[0]
            else:
                rec.valuation_followup = False


class ValuationFollwup(models.Model):
    """Valuation Follow Up"""

    _name = "school.valuation_followup"
    _description = "Valuation Followup"
    _inherit = ["mail.thread", "school.uid.mixin"]

    active = fields.Boolean(
        string="Active",
        help="The active field allows you to hide the course group without removing it.",
        default=True,
        copy=False,
    )

    individual_course_group_id = fields.Many2one(
        "school.individual_course_group",
        string="Individual Course Group",
        delete="cascade",
    )

    @api.model
    def create(self, vals):
        self._update_create_write_vals(vals)
        return super().create(vals)

    def write(self, vals):
        self._update_create_write_vals(vals)
        return super().write(vals)

    def _update_create_write_vals(self, vals):
        pass
        # subscribe employee or department manager when equipment assign to employee or department.
        if vals.get("individual_course_group_id"):
            icg_id = self.env["school.individual_course_group"].browse(
                vals["individual_course_group_id"]
            )
            if icg_id:
                vals |= {
                    "name": icg_id.name,
                    "title": icg_id.title,
                    "student_id": icg_id.student_id.id,
                    "responsible_id": icg_id.responsible_id.id,
                    "program_id": icg_id.valuated_program_id.id,
                }
        return vals

    name = fields.Char(string="Name")
    title = fields.Char(string="Title")
    student_id = fields.Many2one("res.partner", string="Student")
    responsible_id = fields.Many2one("res.partner", string="Responsible")
    program_id = fields.Many2one(
        "school.individual_program", string="Individual Program"
    )

    image_1920 = fields.Binary(
        "Image", attachment=True, related="student_id.image_1920"
    )
    image_512 = fields.Binary("Image", attachment=True, related="student_id.image_512")
    image_128 = fields.Binary("Image", attachment=True, related="student_id.image_128")

    responsible_uid = fields.Many2one(
        "res.users", compute="_compute_responsible_uid", store=True
    )

    @api.depends("responsible_id")
    def _compute_responsible_uid(self):
        for rec in self:
            user_id = self.env["res.users"].search(
                [["partner_id", "=", rec.responsible_id.id]]
            )
            rec.responsible_uid = user_id

    valuation_type = fields.Selection(
        [("A", "Valuated based on experience"), ("C", "Valuated based on credits")],
        string="Valuation Type",
        default="C",
        tracking=True,
    )

    responsible_decision = fields.Selection(
        [("accept", "Accepted"), ("reject", "Rejected")],
        string="Responsible Decision",
        default="reject",
        tracking=True,
    )

    state = fields.Selection(
        [
            ("10_irregular", "Irregular"),
            ("9_draft", "Draft"),
            ("7_failed", "Failed"),
            ("6_success", "Success"),
            ("5_progress", "In Progress"),
            ("3_rejected", "Rejected"),
            ("2_candidate", "Candidate"),
            ("1_confirmed", "Confirmed"),
            ("1_1_checked", "Checked"),
            ("0_valuated", "Valuated"),
        ],
        string="Status",
        related="individual_course_group_id.state",
        tracking=True,
        store=True,
    )

    administration_comments = fields.Text(
        string="Administration Comments", tracking=True
    )

    responsible_comments = fields.Text(string="Responsible Comments", tracking=True)

    attachment_ids = fields.Many2many(
        "ir.attachment",
        "valuations_ir_attachment_rel",
        "valuation_id",
        "ir_attachment_id",
        "Attachments",
        tracking=True,
    )

    def action_revert_to_candidate(self):
        for rec in self:
            rec.individual_course_group_id.write({"state": "2_candidate"})

    def action_confirm_valuate_course_group(self):
        for rec in self:
            rec.individual_course_group_id.write({"state": "1_confirmed"})
            composer_form_view_id = self.env.ref(
                "mail.email_compose_message_wizard_form"
            ).id

            template_id = self.env.ref(
                "school_valuations.email_template_valuation_teacher"
            ).id

            return {
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": "mail.compose.message",
                "view_id": composer_form_view_id,
                "target": "new",
                "context": {
                    "default_composition_mode": "mass_mail"
                    if len(self.ids) > 1
                    else "comment",
                    "default_res_id": self.ids[0],
                    "default_model": self._name,
                    "default_use_template": bool(template_id),
                    "default_template_id": template_id,
                    "website_sale_send_recovery_email": True,
                    "active_ids": self.ids,
                },
            }

    def action_valuate_course_group(self):
        for rec in self:
            rec.individual_course_group_id.write({"state": "0_valuated"})

    def action_check_course_group(self):
        for rec in self:
            rec.individual_course_group_id.write({"state": "1_1_checked"})

    def action_reject_course_group(self):
        for rec in self:
            rec.individual_course_group_id.write({"state": "3_rejected"})

    def action_to_candidate_course_group(self):
        for rec in self:
            rec.individual_course_group_id.write({"state": "2_candidate"})

    def action_to_failed_course_group(self):
        for rec in self:
            rec.write({"active": False})
            rec.individual_course_group_id.unlink()
