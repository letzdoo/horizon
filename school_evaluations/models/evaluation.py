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
import collections
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class IndividualProgram(models.Model):
    """Individual Program"""

    _inherit = "school.individual_program"

    def set_to_abandonned(self, context):
        # TODO use a workflow to make sure only valid changes are used.
        return self.write(
            {"state": "abandonned", "abandonned_date": fields.Date.today()}
        )

    @api.onchange("state")
    def _onchange_state(self):
        if self.state == "irregular":
            self.bloc_ids.write({"state": "irregular"})

    historical_bloc_1_eval = fields.Float(
        string="Hist Bloc 1 Eval", tracking=True, digits=dp.get_precision("Evaluation")
    )
    historical_bloc_1_credits = fields.Integer(string="Hist Bloc 1 ECTS", tracking=True)

    historical_bloc_2_eval = fields.Float(
        string="Hist Bloc 2 Eval", tracking=True, digits=dp.get_precision("Evaluation")
    )
    historical_bloc_2_credits = fields.Integer(string="Hist Bloc 2 ECTS", tracking=True)

    grade = fields.Selection(
        [
            ("without", "Without Grade"),
            ("satisfaction", "Satisfaction"),
            ("distinction", "Distinction"),
            ("second_class", "Second Class Honor"),
            ("first_class", "First Class Honor"),
        ],
        string="Grade",
        tracking=True,
    )

    grade_year_id = fields.Many2one(
        "school.year", string="Graduation year", tracking=True
    )

    graduation_date = fields.Date(string="Graduation Date", tracking=True)

    grade_comments = fields.Text(string="Grade Comments", tracking=True)

    evaluation = fields.Float(
        string="Evaluation",
        compute="_compute_evaluation",
        digits=dp.get_precision("Evaluation"),
        store=True,
    )

    total_registered_credits = fields.Integer(
        compute="_compute_total_acquiered_credits",
        string="Registered Credits",
        tracking=True,
        store=True,
    )
    total_acquiered_credits = fields.Integer(
        compute="_compute_total_acquiered_credits",
        string="Acquiered Credits",
        tracking=True,
        store=True,
    )

    program_completed = fields.Boolean(
        compute="_compute_total_acquiered_credits",
        string="Program Completed",
        tracking=True,
        store=True,
    )

    valuated_course_group_ids = fields.One2many(
        "school.individual_course_group",
        "valuated_program_id",
        string="Valuated Courses Groups",
        tracking=True,
    )

    total_valuated_credits = fields.Integer(
        compute="_compute_total_acquiered_credits",
        string="Valuated Credits",
        tracking=True,
        store=True,
    )

    @api.depends(
        "valuated_course_group_ids",
        "required_credits",
        "bloc_ids.state",
        "bloc_ids.total_acquiered_credits",
        "historical_bloc_1_credits",
        "historical_bloc_2_credits",
    )
    def _compute_total_acquiered_credits(self):
        for rec in self:
            _logger.debug(
                'Trigger "_compute_total_acquiered_credits" on Program %s' % rec.name
            )
            total = (
                sum(
                    cg.source_course_group_id.total_credits
                    for cg in rec.valuated_course_group_ids.filtered(
                        lambda vcg: vcg.state == "0_valuated"
                    )
                )
                + sum(
                    bloc_id.total_acquiered_credits
                    if bloc_id.state
                    in ["awarded_first_session", "awarded_second_session", "failed"]
                    else 0
                    for bloc_id in rec.bloc_ids
                )
                or 0
            )
            total_current = sum(
                bloc_id.total_credits
                if bloc_id.state in ["progress", "postponed"]
                else 0
                for bloc_id in rec.bloc_ids
            )
            rec.total_acquiered_credits = (
                total + rec.historical_bloc_1_credits + rec.historical_bloc_2_credits
            )
            rec.program_completed = (
                rec.required_credits > 0
                and rec.total_acquiered_credits >= rec.required_credits
            )
            rec.total_registered_credits = rec.total_acquiered_credits + total_current
            rec.program_completed = (
                rec.required_credits > 0
                and rec.total_acquiered_credits >= rec.required_credits
            )
            rec.total_valuated_credits = sum(
                cg.source_course_group_id.total_credits
                for cg in rec.valuated_course_group_ids
            )

    @api.depends(
        "valuated_course_group_ids",
        "bloc_ids.evaluation",
        "historical_bloc_1_eval",
        "historical_bloc_2_eval",
    )
    def _compute_evaluation(self):
        for rec in self:
            total = 0
            credit_count = 0
            for bloc in rec.bloc_ids:
                if bloc.evaluation > 0:  # if all is granted do not count
                    total += bloc.evaluation * bloc.total_credits
                    credit_count += bloc.total_credits
            if rec.historical_bloc_1_eval > 0:
                total += rec.historical_bloc_1_eval * rec.historical_bloc_1_credits
                credit_count += rec.historical_bloc_1_credits
            if rec.historical_bloc_2_eval > 0:
                total += rec.historical_bloc_2_eval * rec.historical_bloc_2_credits
                credit_count += rec.historical_bloc_2_credits
            if credit_count > 0:
                rec.evaluation = total / credit_count

    @api.depends(
        "valuated_course_group_ids",
        "bloc_ids.evaluation",
        "historical_bloc_1_eval",
        "historical_bloc_2_eval",
    )
    def _compute_evaluation_details(self):
        self.ensure_one()
        ret = [0, 0, 0, 0, 0, 0]
        if self.historical_bloc_1_eval > 0:
            ret[0] = self.historical_bloc_1_eval
        if self.historical_bloc_2_eval > 0:
            ret[1] = self.historical_bloc_2_eval
        for bloc in self.bloc_ids:
            ret[int(bloc.source_bloc_level) - 1] = bloc.evaluation
        return {"bloc_evaluations": ret}

    all_ind_course_group_ids = fields.One2many(
        "school.individual_course_group",
        string="All Courses Groups",
        compute="_compute_ind_course_group_ids_eval",
    )
    not_acquired_ind_course_group_ids = fields.One2many(
        "school.individual_course_group",
        string="Not Acquiered Courses Groups",
        compute="_compute_ind_course_group_ids_eval",
    )
    acquired_ind_course_group_ids = fields.One2many(
        "school.individual_course_group",
        string="Acquiered Courses Groups",
        compute="_compute_ind_course_group_ids_eval",
    )
    remaining_course_group_ids = fields.One2many(
        "school.course_group",
        string="Remaining Courses Groups",
        compute="_compute_ind_course_group_ids_eval",
    )
    remaining_not_planned_course_group_ids = fields.One2many(
        "school.course_group",
        string="Remaining and Not Planned Courses Groups",
        compute="_compute_ind_course_group_ids_eval",
    )

    def _compute_ind_course_group_ids_eval(self):
        for rec in self:
            rec.all_ind_course_group_ids = (
                rec.valuated_course_group_ids + rec.ind_course_group_ids
            )
            rec.not_acquired_ind_course_group_ids = rec.ind_course_group_ids.filtered(
                lambda ic: ic.acquiered == "NA"
            )
            rec.acquired_ind_course_group_ids = (
                rec.ind_course_group_ids.filtered(lambda ic: ic.acquiered == "A")
                + rec.valuated_course_group_ids
            )
            rec.remaining_course_group_ids = (
                rec.source_program_id.course_group_ids
                - rec.acquired_ind_course_group_ids.mapped("source_course_group_id")
            )
            if len(rec.bloc_ids) > 0:
                rec.remaining_not_planned_course_group_ids = (
                    rec.remaining_course_group_ids
                    - rec.bloc_ids[-1].course_group_ids.mapped("source_course_group_id")
                )
            else:
                rec.remaining_not_planned_course_group_ids = (
                    rec.remaining_course_group_ids
                )

    ##############################################################################
    #
    # Constraints
    #

    @api.constrains("valuated_course_group_ids")
    def _check_cycle(self):
        for rec in self:
            # Only previously failed CG can be valuated
            acq_scg_ids = list(
                map(
                    lambda cg: cg.source_course_group_id.uid,
                    rec.all_ind_course_group_ids.filtered(
                        lambda ic: ic.state != "7_failed"
                    ),
                )
            )
            val_scg_ids = list(
                map(
                    lambda cg: cg.source_course_group_id.uid,
                    rec.valuated_course_group_ids,
                )
            )
            duplicates = [
                item
                for item, count in collections.Counter(
                    acq_scg_ids.extend(val_scg_ids)
                ).items()
                if count > 1
            ]
            if len(duplicates) > 0:
                raise ValidationError(
                    _("Cannot have duplicated UE in a program : %s.")
                    % self.env["school.course_group"].browse(duplicates).mapped("uid")
                )


class IndividualCourseSummary(models.Model):
    """IndividualCourse Summary"""

    _inherit = "school.individual_course_summary"

    def _compute_ind_course_group_ids(self):
        ret = super(IndividualCourseSummary, self)._compute_ind_course_group_ids()
        for rec in self:
            rec.ind_course_group_ids |= (
                rec.program_id.valuated_course_group_ids.filtered(
                    lambda item: item.source_course_group_id.id
                    == rec.course_group_id.id  # noqa: disable=B023
                )
            )
        return ret

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
        compute="_compute_state",
    )

    trials = fields.Integer(string="Trials", compute="_compute_state")

    final_result_disp = fields.Char(
        string="Final Result Display", compute="_compute_state"
    )

    def _compute_state(self):
        for rec in self:
            all_rec = rec.ind_course_group_ids
            rec.trials = len(all_rec)
            if len(all_rec) > 0:
                rec.state = all_rec[-1].state
                rec.final_result_disp = all_rec[-1].final_result_disp
            else:
                rec.state = "9_draft"
                rec.final_result_disp = ""

    def action_valuate_course_group(self):
        for rec in self:
            self.env["school.individual_course_group"].search(
                [
                    ["valuated_program_id", "=", rec.program_id.id],
                    ["source_course_group_id", "=", rec.course_group_id.id],
                ]
            ).write({"state": "0_valuated"})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_confirm_valuate_course_group(self):
        for rec in self:
            self.env["school.individual_course_group"].search(
                [
                    ["valuated_program_id", "=", rec.program_id.id],
                    ["source_course_group_id", "=", rec.course_group_id.id],
                ]
            ).write({"state": "1_confirmed"})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_candidate_valuate_course_group(self):
        for rec in self:
            valuated_cg = self.env["school.individual_course_group"].create(
                {
                    "valuated_program_id": rec.program_id.id,
                    "source_course_group_id": rec.course_group_id.id,
                    "state": "2_candidate",
                }
            )
            rec.program_id.valuated_course_group_ids |= valuated_cg
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_delete_course_group(self):
        self.unlink()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


class IndividualBloc(models.Model):
    """Individual Bloc"""

    _inherit = "school.individual_bloc"

    total_acquiered_credits = fields.Integer(
        compute="_compute_credits", string="Acquiered Credits", store=True
    )
    total_acquiered_hours = fields.Integer(
        compute="_compute_credits", string="Acquiered Hours", store=True
    )
    total_not_acquiered_credits = fields.Integer(
        compute="_compute_credits", string="Not Acquiered Credits", store=True
    )
    total_not_acquiered_hours = fields.Integer(
        compute="_compute_credits", string="Not Acquiered Hours", store=True
    )

    evaluation = fields.Float(
        string="Evaluation",
        compute="_compute_evaluation",
        digits=dp.get_precision("Evaluation"),
        store=True,
    )
    decision = fields.Text(
        compute="_compute_credits", string="Decision", tracking=True, store=True
    )

    first_session_result = fields.Float(
        string="Evaluation",
        compute="_compute_evaluation",
        digits=dp.get_precision("Evaluation"),
        store=True,
    )
    second_session_result = fields.Float(
        string="Evaluation",
        compute="_compute_evaluation",
        digits=dp.get_precision("Evaluation"),
        store=True,
    )

    @api.onchange("state")
    def _onchange_state(self):
        if self.state == "draft":
            self.course_group_ids.write({"state": "9_draft"})
        elif self.state == "progress":
            self.course_group_ids.write({"state": "5_progress"})
        elif self.state == "irregular":
            self.course_group_ids.write({"state": "10_irregular"})
        # elif self.state == 'postponed' :
        #    self.course_group_ids.write({'state': '5_progress'})
        # else :
        #    self.course_group_ids.write({'state': 'confirmed'})

    def set_to_draft(self, context=None):
        # TODO use a workflow to make sure only valid changes are used.
        self.course_group_ids.write({"state": "9_draft"})
        self.course_group_ids._compute_average_results()
        return self.write({"state": "draft"})

    def set_to_progress(self, context=None):
        # TODO use a workflow to make sure only valid changes are used.
        self.course_group_ids.write({"state": "5_progress"})
        self.course_group_ids._compute_average_results()
        return self.write({"state": "progress"})

    def set_to_postponed(self, decision=None, context=None):
        # TODO use a workflow to make sure only valid changes are used.
        if isinstance(decision, dict):
            decision = None
        self._deliberate_cg(self.course_group_ids)
        return self.write({"state": "postponed", "decision": decision})

    def set_to_awarded_first_session(self, decision=None, context=None):
        # TODO use a workflow to make sure only valid changes are used.
        if isinstance(decision, dict):
            decision = None
        self._deliberate_cg(self.course_group_ids)
        return self.write({"state": "awarded_first_session", "decision": decision})

    def set_to_awarded_second_session(self, decision=None, context=None):
        # TODO use a workflow to make sure only valid changes are used.
        if isinstance(decision, dict):
            decision = None
        self._deliberate_cg(self.course_group_ids)
        return self.write({"state": "awarded_second_session", "decision": decision})

    def set_to_failed(self, decision=None, context=None):
        # TODO use a workflow to make sure only valid changes are used.
        if isinstance(decision, dict):
            decision = None
        self._deliberate_cg(self.course_group_ids)
        return self.write({"state": "failed", "decision": decision})

    def _deliberate_cg(self, cgs):
        if self.state == "draft":
            cgs.write({"state": "9_draft"})
        elif self.state == "progress":
            cgs.write({"state": "5_progress"})
        elif self.state == "postponed":
            for cg in cgs:
                if cg.acquiered == "A":
                    cg.write({"state": "6_success"})
                else:
                    cg.write({"state": "5_progress"})
        elif self.state == "abandoned":
            cgs.write({"state": "7_failed"})
        else:
            for cg in cgs:
                if cg.acquiered == "A":
                    cg.write({"state": "6_success"})
                else:
                    cg.write({"state": "7_failed"})

    def set_to_abandoned(self, decision=None, context=None):
        return self.write({"state": "abandoned", "decision": None})

    def report_send(self):
        """Open a window to compose an email, with the default template
        message loaded by default
        """
        self.ensure_one()
        template = self.env.ref(
            "school_evaluations.email_template_success_certificate", False
        )
        compose_form = self.env.ref("mail.email_compose_message_wizard_form", False)
        ctx = dict(
            default_model="school.individual_bloc",
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode="comment",
            mark_invoice_as_sent=True,
        )
        return {
            "name": _("Compose Email"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form.id, "form")],
            "view_id": compose_form.id,
            "target": "new",
            "context": ctx,
        }

    @api.depends(
        "course_group_ids.total_credits",
        "course_group_ids.total_hours",
        "course_group_ids.acquiered",
        "course_group_ids.first_session_computed_result_bool",
        "course_group_ids.is_ghost_cg",
    )
    def _compute_credits(self):
        for rec in self:
            rec.total_acquiered_credits = sum(
                [
                    icg.total_credits
                    for icg in rec.course_group_ids
                    if icg.acquiered == "A" and not icg.is_ghost_cg
                ]
            )
            rec.total_acquiered_hours = sum(
                [
                    icg.total_hours
                    for icg in rec.course_group_ids
                    if icg.acquiered == "A" and not icg.is_ghost_cg
                ]
            )
            rec.total_not_acquiered_credits = (
                rec.total_credits - rec.total_acquiered_credits
            )
            rec.total_not_acquiered_hours = rec.total_hours - rec.total_acquiered_hours
            if rec.level == "1A1C":
                if rec.total_acquiered_credits == rec.total_credits:
                    rec.decision = "A validé tous les ECTS et est autorisé(e) à poursuivre son parcours sans restriction."
                elif (
                    rec.total_acquiered_credits < 45
                    and rec.total_acquiered_credits >= 30
                ):
                    rec.decision = "A validé au moins de 30 ECTS mais moins de 45. Peut compléter son programme ou non avec accord du jury."
                elif rec.total_acquiered_credits < 30:
                    rec.decision = "A validé moins de 30 ECTS. N’a pas rempli les conditions de réussite de son programme."
                else:
                    rec.decision = "A validé au moins 45 ECTS et est autorisé à poursuivre son parcours tout en représentant les UE non validées."
            else:
                rec.decision = "Cycle en cours."

    @api.depends(
        "course_group_ids.final_result",
        "course_group_ids.total_weight",
        "course_group_ids.acquiered",
        "course_group_ids.is_ghost_cg",
    )
    def _compute_evaluation(self):
        for rec in self:
            total = 0
            total_first = 0
            total_second = 0
            total_weight = 0
            for icg in rec.course_group_ids:
                if icg.acquiered == "A":
                    total += icg.final_result * icg.total_weight
                    total_first += icg.first_session_result * icg.total_weight
                    total_second += icg.second_session_result * icg.total_weight
                    total_weight += icg.total_weight
            if total_weight > 0:
                rec.evaluation = total / total_weight
                rec.first_session_result = total_first / total_weight
                rec.second_session_result = total_second / total_weight
            else:
                _logger.debug("total_weight is 0 on Bloc %s" % rec.name)
                rec.evaluation = None


class IndividualCourseGroup(models.Model):
    """Individual Course Group"""

    _inherit = "school.individual_course_group"

    def set_to_draft(self, context=None):
        return self.write({"state": "9_draft"})

    def set_to_progress(self, context=None):
        return self.write({"state": "5_progress"})

    def set_to_confirmed(self, context=None):
        return self.write({"state": "1_confirmed"})

    def set_to_success(self, context=None):
        return self.write({"state": "6_success"})

    def set_to_failed(self, context=None):
        return self.write({"state": "7_failed"})

    def set_to_valuated(self, context=None):
        return self.write({"state": "0_valuated"})

    # Override
    def _domain_source_course_group_id(self):
        if self.env.context.get("default_bloc_id"):
            bloc_id = self.env["school.individual_bloc"].browse(
                self.env.context.get("default_bloc_id")
            )
            cgs = self.env["school.individual_course_summary"].search(
                [
                    ("id", "in", bloc_id.program_id.course_group_summaries.ids),
                    ("state", "in", ("9_draft", "7_failed")),
                ]
            )
            return [("id", "in", cgs.course_group_id.ids)]
        else:
            return []

    valuated_program_id = fields.Many2one(
        "school.individual_program", string="Program", ondelete="cascade", readonly=True
    )

    @api.depends("bloc_id.student_id", "valuated_program_id.student_id")
    def _compute_student_id(self):
        for rec in self:
            if rec.valuated_program_id:
                rec.student_id = rec.valuated_program_id.student_id
            else:
                rec.student_id = rec.bloc_id.student_id

    @api.constrains("bloc_id", "valuated_program_id")
    def _check_bloc_id_constrains(self):
        if self.bloc_id and self.valuated_program_id:
            raise UserError(
                _(
                    "A Course Group cannot be valuated in a program and in a bloc at the same time."
                )
            )

    # Actions

    def set_deliberated_to_ten(self, session=1, message=""):
        for rec in self:
            if session == 1:
                rec.write(
                    {
                        "first_session_deliberated_result": max(
                            rec.first_session_computed_result, 10
                        ),
                        "first_session_deliberated_result_bool": True,
                        "first_session_note": message,
                    }
                )
            else:
                rec.write(
                    {
                        "second_session_deliberated_result": max(
                            rec.second_session_computed_result, 10
                        )
                        if rec.second_session_computed_result_bool
                        else max(rec.first_session_computed_result, 10),
                        "second_session_deliberated_result_bool": True,
                        "second_session_note": message,
                    }
                )

    # First Session

    first_session_computed_exception = fields.Selection(
        ([("NP", "NP"), ("AB", "AB"), ("TP", "TP")]),
        compute="_compute_average_results",
        string="First Session Computed Exception",
        store=True,
    )
    first_session_computed_result = fields.Float(
        compute="_compute_average_results",
        string="First Session Computed Result",
        store=True,
        digits=dp.get_precision("Evaluation"),
    )
    first_session_computed_result_bool = fields.Boolean(
        compute="_compute_average_results",
        string="First Session Computed Active",
        store=True,
    )

    first_session_deliberated_result = fields.Char(
        string="First Session Deliberated Result", tracking=True
    )
    first_session_deliberated_result_bool = fields.Boolean(
        string="First Session Deliberated Active", tracking=True
    )

    first_session_exception = fields.Selection(
        ([("NP", "NP"), ("AB", "AB"), ("TP", "TP")]),
        compute="_compute_first_session_results",
        string="First Session Exception",
        store=True,
    )
    first_session_result = fields.Float(
        compute="_compute_first_session_results",
        string="First Session Result",
        store=True,
        digits=dp.get_precision("Evaluation"),
    )
    first_session_result_bool = fields.Boolean(
        compute="_compute_first_session_results",
        string="First Session Active",
        store=True,
    )
    first_session_result_disp = fields.Char(
        string="First Session Result Display", compute="_compute_results_disp"
    )

    first_session_note = fields.Text(string="First Session Notes")

    # Second Session

    second_session_computed_exception = fields.Selection(
        ([("NP", "NP"), ("AB", "AB"), ("TP", "TP")]),
        compute="_compute_average_results",
        string="Second Session Computed Exception",
        store=True,
    )
    second_session_computed_result = fields.Float(
        compute="_compute_average_results",
        string="Second Session Computed Result",
        store=True,
        digits=dp.get_precision("Evaluation"),
    )
    second_session_computed_result_bool = fields.Boolean(
        compute="_compute_average_results",
        string="Second Session Computed Active",
        store=True,
    )

    second_session_deliberated_result = fields.Char(
        string="Second Session Deliberated Result", digits=(5, 2), tracking=True
    )
    second_session_deliberated_result_bool = fields.Boolean(
        string="Second Session Deliberated Active", tracking=True
    )

    second_session_exception = fields.Selection(
        ([("NP", "NP"), ("AB", "AB"), ("TP", "TP")]),
        compute="_compute_second_session_results",
        string="Second Session Exception",
        store=True,
    )
    second_session_result = fields.Float(
        compute="_compute_second_session_results",
        string="Second Session Result",
        store=True,
        digits=dp.get_precision("Evaluation"),
    )
    second_session_result_bool = fields.Boolean(
        compute="_compute_second_session_results",
        string="Second Session Active",
        store=True,
    )
    second_session_result_disp = fields.Char(
        string="Second Session Result Display", compute="_compute_results_disp"
    )

    second_session_note = fields.Text(string="Second Session Notes")

    # Final

    final_result_exception = fields.Selection(
        ([("NP", "NP"), ("AB", "AB"), ("TP", "TP")]),
        compute="_compute_final_results",
        string="Final Exception",
        store=True,
        tracking=True,
    )
    final_result = fields.Float(
        compute="_compute_final_results",
        string="Final Result",
        store=True,
        digits=dp.get_precision("Evaluation"),
        tracking=True,
    )
    final_result_bool = fields.Boolean(
        compute="_compute_final_results", string="Final Active", store=True
    )
    final_result_disp = fields.Char(
        string="Final Result Display", compute="_compute_results_disp"
    )

    acquiered = fields.Selection(
        ([("A", "Acquiered"), ("NA", "Not Acquiered")]),
        compute="_compute_final_results",
        string="Acquired Credits",
        store=True,
        tracking=True,
        default="NA",
    )

    final_note = fields.Text(string="Final Notes")

    def _compute_results_disp(self):
        for rec in self:
            if not rec.first_session_result_bool:
                rec.first_session_result_disp = ""
            elif rec.first_session_exception:
                rec.first_session_result_disp = rec.first_session_exception
            else:
                rec.first_session_result_disp = "%.2f" % rec.first_session_result

            if not rec.second_session_result_bool:
                rec.second_session_result_disp = ""
            elif rec.second_session_exception:
                rec.second_session_result_disp = rec.second_session_exception
            else:
                rec.second_session_result_disp = "%.2f" % rec.second_session_result

            if not rec.final_result_bool:
                rec.final_result_disp = ""
            elif rec.final_result_exception:
                rec.final_result_disp = rec.final_result_exception
            else:
                rec.final_result_disp = "%.2f" % rec.final_result

    def _parse_result(self, input_value):
        f = float(input_value)
        if f < 0 or f > 20:
            raise ValidationError(_("Evaluation shall be between 0 and 20"))
        else:
            return f

    @api.onchange("first_session_deliberated_result_bool")
    def _onchange_first_session_deliberated_result_bool(self):
        self.first_session_deliberated_result = False

    @api.onchange("second_session_deliberated_result_bool")
    def _onchange_second_session_deliberated_result_bool(self):
        self.second_session_deliberated_result = False

    @api.depends(
        "course_ids.first_session_result_bool",
        "course_ids.first_session_result",
        "course_ids.first_session_exception",
        "course_ids.second_session_result_bool",
        "course_ids.second_session_result",
        "course_ids.second_session_exception",
        "course_ids.weight",
    )
    def _compute_average_results(self, force=False):
        for (
            rec
        ) in (
            self
        ):  # .filtered(lambda r: force or r.state in ['7_failed','5_progress']) :
            _logger.debug(
                'Trigger "_compute_average_results" on Course Group %s' % rec.uid
            )
            # Compute Weighted Average
            running_first_session_result = 0
            running_second_session_result = 0
            rec.first_session_computed_result_bool = False
            rec.first_session_computed_result = 0
            rec.second_session_computed_result_bool = False
            rec.second_session_computed_result = 0

            shall_compute_second_session = False

            for ic in rec.course_ids:
                if ic.second_session_result_bool:
                    shall_compute_second_session = True

            for ic in rec.course_ids:
                # Compute First Session
                if ic.first_session_result_bool:
                    running_first_session_result += ic.first_session_result * ic.weight
                    rec.first_session_computed_result_bool = True
                # Compute Second Session if required
                if shall_compute_second_session:
                    if ic.second_session_result_bool:
                        running_second_session_result += (
                            ic.second_session_result * ic.weight
                        )
                    else:
                        running_second_session_result += (
                            ic.first_session_result * ic.weight
                        )
                    rec.second_session_computed_result_bool = True

            if rec.first_session_computed_result_bool:
                if rec.total_weight > 0:
                    rec.first_session_computed_result = (
                        running_first_session_result / rec.total_weight
                    )
            if rec.second_session_computed_result_bool:
                if rec.total_weight > 0:
                    rec.second_session_computed_result = (
                        running_second_session_result / rec.total_weight
                    )

            rec.first_session_computed_exception = False

            for ic in rec.course_ids:
                if ic.first_session_exception:
                    rec.first_session_computed_result = 0
                    rec.first_session_computed_exception = ic.first_session_exception
                    rec.first_session_computed_result_bool = True
                    break

            rec.second_session_computed_exception = False

            for ic in rec.course_ids:
                if ic.second_session_exception:
                    rec.second_session_computed_result = 0
                    rec.second_session_computed_exception = ic.second_session_exception
                    rec.second_session_computed_result_bool = True
                    break

            rec._compute_first_session_results(force)
            rec._compute_second_session_results(force)

    @api.depends(
        "first_session_deliberated_result_bool",
        "first_session_deliberated_result",
        "first_session_computed_result_bool",
        "first_session_computed_result",
        "first_session_computed_exception",
    )
    def _compute_first_session_results(self, force=False):
        for (
            rec
        ) in (
            self
        ):  # .filtered(lambda r: force or r.state in ['7_failed','5_progress']) :
            _logger.debug(
                'Trigger "_compute_first_session_results" on Course Group %s' % rec.uid
            )
            # Compute Session Results
            if rec.first_session_deliberated_result_bool:
                try:
                    f = rec._parse_result(rec.first_session_deliberated_result)
                except ValueError as error:
                    rec.write("first_session_deliberated_result", None)
                    raise UserError(
                        _(
                            'Cannot decode %s, please encode a Float eg "12.00".'
                            % rec.first_session_deliberated_result
                        )
                    ) from error
                if f and f < rec.first_session_computed_result:
                    # TODO : take care of this - removed due to Cours artistiques B - Art dramatique - 2 - 2015-2016 - VALERIO Maddy
                    raise ValidationError(
                        _(
                            f"Deliberated result must be above computed result, i.e. {rec.first_session_deliberated_result} > {rec.first_session_computed_result} in {rec.uid}."
                        )
                    )
                else:
                    rec.first_session_exception = None
                    rec.first_session_result = f
                rec.first_session_result_bool = True
            elif rec.first_session_computed_exception:
                rec.first_session_exception = rec.first_session_computed_exception
                rec.first_session_result = 0
                rec.first_session_result_bool = True
            elif rec.first_session_computed_result_bool:
                rec.first_session_exception = None
                rec.first_session_computed_exception = None
                rec.first_session_result = rec.first_session_computed_result
                rec.first_session_result_bool = True
            else:
                rec.first_session_exception = None
                rec.first_session_computed_exception = None
                rec.first_session_result = 0
                rec.first_session_result_bool = False
            rec._compute_final_results(force)

    @api.depends(
        "second_session_deliberated_result_bool",
        "second_session_deliberated_result",
        "second_session_computed_result_bool",
        "second_session_computed_result",
        "second_session_computed_exception",
    )
    def _compute_second_session_results(self, force=False):
        for (
            rec
        ) in (
            self
        ):  # .filtered(lambda r: force or r.state in ['7_failed','5_progress']) :
            _logger.debug(
                'Trigger "_compute_second_session_results" on Course Group %s' % rec.uid
            )
            if rec.second_session_deliberated_result_bool:
                try:
                    f = rec._parse_result(rec.second_session_deliberated_result)
                except ValueError as error:
                    rec.write("second_session_deliberated_result", None)
                    raise UserError(
                        _(
                            'Cannot decode %s, please encode a Float eg "12.00".'
                            % rec.second_session_deliberated_result
                        )
                    ) from error
                if f < rec.second_session_computed_result:
                    raise ValidationError(
                        _(
                            f"Deliberated result must be above computed result, i.e. {rec.second_session_deliberated_result} > {rec.second_session_computed_result} in {rec.uid}."
                        )
                    )
                else:
                    rec.second_session_exception = None
                    rec.second_session_result = f
                rec.second_session_exception = None
                rec.second_session_result_bool = True
            elif rec.second_session_computed_exception:
                rec.second_session_exception = rec.second_session_computed_exception
                rec.second_session_result = 0
                rec.second_session_result_bool = True
            elif rec.second_session_computed_result_bool:
                rec.second_session_exception = None
                rec.second_session_computed_exception = None
                rec.second_session_result = rec.second_session_computed_result
                rec.second_session_result_bool = True
            else:
                rec.second_session_exception = None
                rec.second_session_computed_exception = None
                rec.second_session_result = 0
                rec.second_session_result_bool = False
            rec._compute_final_results(force)

    @api.depends(
        "second_session_result_bool",
        "second_session_exception",
        "second_session_result",
        "first_session_result_bool",
        "first_session_exception",
        "first_session_result",
    )
    def _compute_final_results(self, force=False):
        for (
            rec
        ) in (
            self
        ):  # .filtered(lambda r: force or r.state in ['7_failed','5_progress']) :
            _logger.debug(
                'Trigger "_compute_final_results" on Course Group %s' % rec.uid
            )
            # Compute Final Results
            if rec.second_session_result_bool:
                if rec.second_session_exception:
                    rec.final_result_exception = rec.second_session_exception
                    rec.final_result = 0
                    rec.final_result_bool = True
                else:
                    rec.final_result_exception = None
                    rec.final_result = rec.second_session_result
                    rec.final_result_bool = True
            elif rec.first_session_result_bool:
                if rec.first_session_exception:
                    rec.final_result_exception = rec.first_session_exception
                    rec.final_result = 0
                    rec.final_result_bool = True
                else:
                    rec.final_result_exception = None
                    rec.final_result = rec.first_session_result
                    rec.final_result_bool = True
            else:
                rec.final_result_exception = None
                rec.final_result = 0
                rec.final_result_bool = False
            if rec.final_result >= 10:
                rec.acquiered = "A"
            else:
                rec.acquiered = "NA"


class IndividualCourse(models.Model):
    """Individual Course"""

    _inherit = "school.individual_course"

    type = fields.Selection(
        ([("S", "Simple"), ("C", "Complex"), ("D", "Deferred")]),
        string="Type",
        readonly=True,
    )  # Kept for archiving purpose

    ann_result = fields.Char(
        string="Annual Result", readonly=True
    )  # Kept for archiving purpose
    jan_result = fields.Char(
        string="January Result", readonly=True
    )  # Kept for archiving purpose
    jun_result = fields.Char(
        string="June Result", readonly=True
    )  # Kept for archiving purpose
    sept_result = fields.Char(
        string="September Result", readonly=True
    )  # Kept for archiving purpose

    open_partial_result = fields.Boolean(
        string="Partial Result", compute="_compute_open_evaluations"
    )
    open_final_result = fields.Boolean(
        string="Final Result", compute="_compute_open_evaluations"
    )
    open_second_result = fields.Boolean(
        string="Second Result", compute="_compute_open_evaluations"
    )

    partial_result = fields.Char(string="Partial Result", tracking=True)
    final_result = fields.Char(string="Final Result", tracking=True)
    second_result = fields.Char(string="Second Result", tracking=True)

    is_annual = fields.Boolean(
        string="Is Annual", related="source_course_id.is_annual", readonly=True
    )

    # First Session

    first_session_exception = fields.Selection(
        ([("NP", "NP"), ("AB", "AB"), ("TP", "TP")]),
        compute="_compute_results",
        string="First Session Exception",
        store=True,
    )
    first_session_result = fields.Float(
        compute="_compute_results",
        string="First Session Result",
        store=True,
        group_operator="avg",
        digits=dp.get_precision("Evaluation"),
    )
    first_session_result_bool = fields.Boolean(
        compute="_compute_results", string="First Session Active", store=True
    )
    first_session_note = fields.Text(string="First Session Notes")

    first_session_result_disp = fields.Char(
        string="First Session Result Display", compute="_compute_session_result_disp"
    )

    # Second Session

    second_session_exception = fields.Selection(
        ([("NP", "NP"), ("AB", "AB"), ("TP", "TP")]),
        compute="_compute_results",
        string="Second Session Exception",
        store=True,
    )
    second_session_result = fields.Float(
        compute="_compute_results",
        string="Second Session Result",
        store=True,
        group_operator="avg",
        digits=dp.get_precision("Evaluation"),
    )
    second_session_result_bool = fields.Boolean(
        compute="_compute_results", string="Second Session Active", store=True
    )
    second_session_note = fields.Text(string="Second Session Notes")

    second_session_result_disp = fields.Char(
        string="Second Session Result Display", compute="_compute_session_result_disp"
    )

    final_result_disp = fields.Char(
        string="Final Result Display", compute="_compute_session_result_disp"
    )

    is_danger = fields.Boolean(compute="_compute_results", store=True)

    def _compute_session_result_disp(self):
        for rec in self:
            if not rec.first_session_result_bool:
                rec.first_session_result_disp = ""
            elif rec.first_session_exception:
                rec.first_session_result_disp = rec.first_session_exception
            else:
                rec.first_session_result_disp = "%.2f" % rec.first_session_result

            if not rec.second_session_result_bool:
                rec.second_session_result_disp = ""
            elif rec.second_session_exception:
                rec.second_session_result_disp = rec.second_session_exception
            else:
                rec.second_session_result_disp = "%.2f" % rec.second_session_result

            if rec.second_session_result_bool:
                rec.final_result_disp = rec.second_session_result_disp
            else:
                rec.final_result_disp = rec.first_session_result_disp

    def _compute_open_evaluations(self):
        evaluation_open_year_id = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("school.evaluation_open_year_id", "0")
        )
        evaluation_open_session = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("school.evaluation_open_session", "none")
        )

        open_recs = self.filtered(
            lambda r: r.year_id.id == int(evaluation_open_year_id)
        )
        if evaluation_open_session == "part":
            open_recs.open_partial_result = True
            open_recs.open_final_result = False
            open_recs.open_second_result = False
        elif evaluation_open_session == "fin":
            open_recs.open_partial_result = False
            open_recs.open_final_result = True
            open_recs.open_second_result = False
        elif evaluation_open_session == "sec":
            open_recs.open_partial_result = False
            open_recs.open_final_result = False
            open_recs.open_second_result = True
        else:
            open_recs.open_partial_result = False
            open_recs.open_final_result = False
            open_recs.open_second_result = False

        closed_recs = self.filtered(
            lambda r: r.year_id.id != int(evaluation_open_year_id)
        )
        closed_recs.open_partial_result = False
        closed_recs.open_final_result = False
        closed_recs.open_second_result = False

    @api.depends("partial_result", "final_result", "second_result")
    def _compute_results(self):  # noqa: C901
        for (
            rec
        ) in (
            self
        ):  # .filtered(lambda r: r.course_group_id.state in ['7_failed','5_progress']) :
            rec.first_session_result = 0
            rec.first_session_result_bool = False
            rec.first_session_exception = False
            rec.second_session_result = 0
            rec.second_session_result_bool = False
            rec.second_session_exception = False
            if rec.partial_result:
                try:
                    if rec.partial_result == "NP":
                        pass
                    elif rec.partial_result == "AB":
                        pass
                    elif rec.partial_result == "TP":
                        pass
                    else:
                        f = float(rec.partial_result)
                        rec.partial_result = format(f, ".2f")
                        if f < 0 or f > 20:
                            raise ValidationError(
                                _("Evaluation shall be between 0 and 20")
                            )
                        else:
                            pass
                except ValueError as error:
                    raise UserError(
                        _(
                            f'Cannot decode {rec.partial_result} in June Result, please encode a Float eg "12.00" or "NP" or "AB" or "TP".'
                        )
                    ) from error

            if rec.final_result:
                try:
                    if rec.final_result == "NP":
                        rec.first_session_result = 0
                        rec.first_session_exception = "NP"
                        rec.first_session_result_bool = True
                        rec.is_danger = True
                    elif rec.final_result == "AB":
                        rec.first_session_result = 0
                        rec.first_session_exception = "AB"
                        rec.first_session_result_bool = True
                        rec.is_danger = True
                    elif rec.final_result == "TP":
                        rec.first_session_result = 0
                        rec.first_session_exception = "TP"
                        rec.first_session_result_bool = True
                        rec.is_danger = True
                    else:
                        f = float(rec.final_result)
                        if f < 0 or f > 20:
                            raise ValidationError(
                                _("Evaluation shall be between 0 and 20")
                            )
                        else:
                            rec.final_result = format(f, ".2f")
                            rec.first_session_result = f
                            rec.first_session_exception = None
                            rec.first_session_result_bool = True
                            if f < 10:
                                rec.is_danger = True
                            else:
                                rec.is_danger = False
                except ValueError as error:
                    rec.first_session_result = 0
                    rec.first_session_exception = None
                    rec.first_session_result_bool = False
                    raise UserError(
                        _(
                            f'Cannot decode {rec.jun_result} in June Result, please encode a Float eg "12.00" or "NP" or "AB" or "TP".'
                        )
                    ) from error

            if rec.second_result:
                try:
                    if rec.second_result == "NP":
                        rec.second_session_exception = "NP"
                        rec.second_session_result = 0
                        rec.second_session_result_bool = True
                        rec.is_danger = True
                    elif rec.second_result == "AB":
                        rec.second_session_exception = "AB"
                        rec.second_session_result = 0
                        rec.second_session_result_bool = True
                        rec.is_danger = True
                    elif rec.second_result == "TP":
                        rec.second_session_exception = "TP"
                        rec.second_session_result = 0
                        rec.second_session_result_bool = True
                        rec.is_danger = True
                    else:
                        f = float(rec.second_result)
                        if f < 0 or f > 20:
                            raise ValidationError(
                                _("Evaluation shall be between 0 and 20")
                            )
                        else:
                            rec.second_result = format(f, ".2f")
                            rec.second_session_result = f
                            rec.second_session_exception = None
                            rec.second_session_result_bool = True
                            if f < 10:
                                rec.is_danger = True
                            else:
                                rec.is_danger = False
                except ValueError as error:
                    rec.second_session_result = 0
                    rec.second_session_exception = None
                    rec.second_session_result_bool = False
                    raise UserError(
                        _(
                            f'Cannot decode {rec.sept_result} in September Result, please encode a Float eg "12.00" or "NP" or "AB" or "TP".'
                        )
                    ) from error
