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

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ProgramApprouval(models.Model):
    """Deliberation"""

    _name = "school.program_approuval"
    _description = "Manage PAE approuval process"
    _inherit = ["school.year_sequence.mixin"]

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("archived", "Archived"),
        ],
        string="Status",
        index=True,
        readonly=True,
        default="draft",
        # tracking=True, TODO : is this useful for this case ?
        copy=False,
        help=" * The 'Draft' status is used when a new deliberation is created and not running yet.\n"
        " * The 'Active' status is when a deliberation is ready to be processed.\n"
        " * The 'Archived' status is used when a deliberation is obsolete and shall be archived.",
    )

    year_id = fields.Many2one("school.year", required=True, string="Year")

    date = fields.Date(required=True, string="Date")

    name = fields.Char(required=True, string="Title")

    secretary_id = fields.Many2one(
        "res.partner", required=True, domain=[("employee", "=", True)]
    )

    valuation_followup_ids = fields.Many2many(
        "school.valuation_followup",
        "school_valuation_approuval_rel",
        "approuval_id",
        "valuation_id",
        string="Valuations",
    )

    valuation_followup_count = fields.Integer(
        string="Valuations Count", compute="_compute_counts"
    )

    individual_bloc_ids = fields.Many2many(
        "school.individual_bloc",
        "school_approuval_bloc_rel",
        "approuval_id",
        "bloc_id",
        string="Blocs",
        domain="[('year_id', '=?', year_id)]",
    )

    individual_bloc_count = fields.Integer(
        string="Blocs Count", compute="_compute_counts"
    )

    participant_ids = fields.Many2many(
        "res.partner",
        "school_approuval_participants_rel",
        "approuval_id",
        "partner_id",
        string="Particpants",
    )

    @api.onchange("individual_bloc_ids")
    def _on_update_individual_bloc_ids(self):
        for rec in self:
            all_program_ids = rec.individual_bloc_ids.mapped("program_id")
            rec.valuation_followup_ids = self.env["school.valuation_followup"].search(
                [
                    ["individual_program_id", "in", all_program_ids.ids],
                    ["state", "!=", "0_valuated"],
                ]
            )

    def _compute_counts(self):
        for rec in self:
            rec.valuation_followup_count = len(rec.valuation_followup_ids)
            rec.individual_bloc_count = len(rec.individual_bloc_ids)

    def to_draft(self):
        return self.write({"state": "draft"})

    def activate(self):
        return self.write({"state": "active"})

    def archive(self):
        return self.write({"state": "archived"})

    def action_open_approuve_valuations(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Approuve Valuations",
            "res_model": "school.valuation_followup",
            "domain": [("approuval_ids", "in", self.id)],
            "view_mode": "kanban,form",
            "search_view_id": (
                self.env.ref(
                    "school_program_approuval.view_approuve_valuations_filter"
                ).id,
            ),
            "views": [
                [
                    self.env.ref(
                        "school_program_approuval.approuve_valuations_kanban_view"
                    ).id,
                    "kanban",
                ],
                [self.env.ref("school_valuations.valuation_form").id, "form"],
            ],
            "context": {"approuval_id": self.id},
        }

    def action_open_approuve_bloc(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Approuve Blocs",
            "res_model": "school.individual_bloc",
            "domain": [("approuval_ids", "in", self.id)],
            "view_mode": "kanban,form",
            "search_view_id": (
                self.env.ref("school_program_approuval.view_approuve_blocs_filter").id,
            ),
            "views": [
                [
                    self.env.ref(
                        "school_program_approuval.approuve_blocs_kanban_view"
                    ).id,
                    "kanban",
                ],
                [self.env.ref("school_management.individual_bloc_form").id, "form"],
            ],
            "context": {"approuval_id": self.id},
        }


class ValuationFollwup(models.Model):
    """Valuation Follwup"""

    _inherit = "school.valuation_followup"

    approuval_ids = fields.Many2many(
        "school.program_approuval",
        "school_valuation_approuval_rel",
        "valuation_id",
        "approuval_id",
        string="Approuvals",
        readonly=True,
    )


class IndividualBloc(models.Model):
    """Individual Bloc"""

    _inherit = "school.individual_bloc"

    approuval_ids = fields.Many2many(
        "school.program_approuval",
        "school_approuval_bloc_rel",
        "bloc_id",
        "approuval_id",
        string="Approuvals",
        readonly=True,
    )

    def action_add_comment_approuve_bloc(self):
        self.ensure_one()
        comments = self.env["school.bloc_approuval"].search(
            [
                ["approuval_id", "=", self._context.get("approuval_id")],
                ["bloc_id", "=", self.id],
            ]
        )
        if comments:
            pass
        else:
            return {
                "type": "ir.actions.act_window",
                "name": "Approuve Blocs",
                "res_model": "school.individual_bloc",
                "domain": [("approuval_ids", "in", self.id)],
                "view_mode": "form",
                "search_view_id": (
                    self.env.ref(
                        "school_program_approuval.view_approuve_blocs_filter"
                    ).id,
                ),
                "views": [
                    [
                        self.env.ref("school_program_approuval.bloc_approuval_form").id,
                        "form",
                    ]
                ],
                "context": {"approuval_id": self.id},
            }


class BlocApprouval(models.Model):
    """Program Deliberation"""

    _name = "school.bloc_approuval"
    _description = "Manage approuval of a bloc"

    approuval_id = fields.Many2one("school.program_approuval", required=True)

    bloc_id = fields.Many2one("school.individual_bloc", required=True)

    image_1920 = fields.Binary(
        "Image", attachment=True, related="bloc_id.student_id.image_1920"
    )

    image_128 = fields.Binary(
        "Image", attachment=True, related="bloc_id.student_id.image_128"
    )

    name = fields.Char(string="Name", related="bloc_id.name")

    student_name = fields.Char(string="Student", related="bloc_id.student_id.name")

    public_comments = fields.Char(string="Public Comments")

    private_comments = fields.Char(string="Private Comments")
