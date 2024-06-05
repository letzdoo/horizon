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
import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class school_year_sequence_mixin(models.AbstractModel):
    _name = "school.year_sequence.mixin"

    year_sequence = fields.Selection(
        [
            ("current", "Current"),
            ("previous", "Previous"),
            ("next", "Next"),
        ],
        string="Year Sequence",
        compute="_compute_year_sequence",
        search="_search_year_sequence",
    )

    def _compute_year_sequence(self):
        for item in self:
            current_year_id = self.env.user.current_year_id
            item.year_sequence = False
            if current_year_id.id == item.year_id.id:
                item.year_sequence = "current"
            if current_year_id.previous.id == item.year_id.id:
                item.year_sequence = "previous"
            if current_year_id.next.id == item.year_id.id:
                item.year_sequence = "next"

    def _search_year_sequence(self, operator, value):
        current_year_id = self.env.user.current_year_id
        year_ids = []
        if "current" in value:
            year_ids.append(current_year_id.id)
        if "previous" in value:
            year_ids.append(current_year_id.previous.id)
        if "next" in value:
            year_ids.append(current_year_id.next.id)
        return [("year_id", "in", year_ids)]


class Year(models.Model):
    """Year"""

    _name = "school.year"
    _order = "name"
    name = fields.Char(required=True, string="Name", size=15)
    short_name = fields.Char(required=True, string="Short Name", size=5)

    previous = fields.Many2one("school.year", string="Previous Year")
    next = fields.Many2one("school.year", string="Next Year")

    startdate = fields.Date("Start date")
    enddate = fields.Date("End date")

    @api.model_create_multi
    def create(self, vals_list):
        years = super().create(vals_list)
        for year in years:
            if year.previous:
                year.previous.next = year
        return years


class Users(models.Model):
    """Users"""

    _inherit = ["res.users"]

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ["current_year_id"]

    current_year_id = fields.Many2one("school.year", string="Current Year")


class Partner(models.Model):
    """Partner"""

    _inherit = "res.partner"

    student = fields.Boolean("Student", default=False)
    teacher = fields.Boolean("Teacher", default=False)
    employee = fields.Boolean("Employee", default=False)

    initials = fields.Char("Initials")

    nationality_id = fields.Many2one("res.country", "Nationality")

    nationality_ids = fields.Many2many(
        "res.country",
        "res_partner_nationalities",
        "partner_id",
        "country_id",
        string="Nationalities",
    )

    @api.constrains("initials")
    def _check_initials(self):
        for rec in self:
            if rec.initials and not re.match(r"([A-Z]\.,)*([A-Z]\.)?", rec.initials):
                raise UserError(_("Please encode initials as eg X.,V.,T."))

    birthplace = fields.Char("Birthplace")
    birthcountry = fields.Many2one("res.country", "Birth Country", ondelete="restrict")
    phone2 = fields.Char("Phone2")
    marial_status = fields.Selection([("M", "Maried"), ("S", "Single")])
    registration_date = fields.Date("Registration Date")
    email_personnel = fields.Char("Email personnel")
    reg_number = fields.Char("Registration Number", size=11)
    mat_number = fields.Char("Matricule Number")

    student_program_ids = fields.One2many(
        "school.individual_program", "student_id", string="Programs"
    )
    student_bloc_ids = fields.One2many(
        "school.individual_bloc", "student_id", string="Programs"
    )

    # Secondary adress

    secondary_street = fields.Char("Street")
    secondary_street2 = fields.Char("Street2")
    secondary_zip = fields.Char("Zip", size=24, change_default=True)
    secondary_city = fields.Char("City")
    secondary_state_id = fields.Many2one(
        "res.country.state", "State", ondelete="restrict"
    )
    secondary_country_id = fields.Many2one(
        "res.country", "Country", ondelete="restrict"
    )

    year_sequence = fields.Selection(
        [
            ("current", "Current"),
            ("previous", "Previous"),
            ("next", "Next"),
            ("never", "Never"),
        ],
        string="Year Sequence",
        compute="_compute_year_sequence",
        search="_search_year_sequence",
    )

    def _compute_year_sequence(self):
        for item in self:
            current_year_id = self.env.user.current_year_id
            year_ids = item.student_bloc_ids.mapped("year_id.id")
            if current_year_id.id in year_ids:
                item.year_sequence = "current"
                return
            if current_year_id.previous.id in year_ids:
                item.year_sequence = "previous"
                return
            if current_year_id.next.id in year_ids:
                item.year_sequence = "next"
                return
            item.year_sequence = "never"

    def _search_year_sequence(self, operator, value):
        current_year_id = self.env.user.current_year_id
        year_ids = []
        if "never" in value:
            return [("student_bloc_ids", "=", False)]
        if "current" in value:
            year_ids.append(current_year_id.id)
        if "previous" in value:
            year_ids.append(current_year_id.previous.id)
        if "next" in value:
            year_ids.append(current_year_id.next.id)
        return [("student_bloc_ids.year_id", "in", year_ids)]

    student_current_block_name = fields.Char(
        "Current Bloc", compute="_compute_student_current_block_name"
    )

    student_current_course_ids = fields.One2many(
        "school.individual_course",
        compute="_compute_student_current_individual_course_ids",
        string="Courses",
    )
    student_course_ids = fields.One2many(
        "school.individual_course",
        "student_id",
        string="Courses",
        domain="[('year_id', '=', self.env.user.current_year_id.id)]",
    )

    teacher_current_course_ids = fields.One2many(
        "school.individual_course_proxy",
        compute="_compute_teacher_current_individual_course_ids",
        string="Current Courses",
    )
    teacher_course_ids = fields.One2many(
        "school.individual_course",
        "teacher_id",
        string="Courses",
        domain="[('year_id', '=', self.env.user.current_year_id.id)]",
    )

    teacher_curriculum_vitae = fields.Html("Curriculum Vitae")

    def _compute_student_current_block_name(self):
        for rec in self:
            blocs = self.env["school.individual_bloc"].search(
                [
                    ["year_id", "=", self.env.user.current_year_id.id],
                    ["student_id", "=", rec.id],
                ]
            )
            rec.student_current_block_name = ",".join(
                blocs.mapped("source_bloc_id.name")
            )

    def _compute_teacher_current_individual_course_ids(self):
        for rec in self:
            rec.teacher_current_course_ids = self.env[
                "school.individual_course_proxy"
            ].search(
                [
                    ["year_id", "=", self.env.user.current_year_id.id],
                    ["teacher_id", "=", rec.id],
                ]
            )

    def _compute_student_current_individual_course_ids(self):
        for rec in self:
            rec.teacher_current_course_ids = self.env[
                "school.individual_course_proxy"
            ].search(
                [
                    ["year_id", "=", self.env.user.current_year_id.id],
                    ["student_id", "=", rec.id],
                ]
            )

    def _get_teacher_current_course_session_ids(self):
        for rec in self:
            rec.teacher_current_assigment_ids = self.env[
                "school.course_session"
            ].search(
                [
                    ["year_id", "=", self.env.user.current_year_id.id],
                    ["teacher_id", "=", rec.id],
                ]
            )

    # custom_partner_fields

    second_first_name = fields.Char(string="Autre(s) prénom(s)")

    # Section Titre d'acces
    admission_exam_date = fields.Date(string="Examen d'admission")
    access_titles_ids = fields.One2many(
        "custom_partner_fields.access_title", "partner_id", string="Titres d'accès"
    )
    memoir_titles_ids = fields.One2many(
        "custom_partner_fields.memoir_title", "partner_id", string="Titres de mémoires"
    )
    internships_ids = fields.One2many(
        "custom_partner_fields.internship", "partner_id", string="Stage(s)"
    )
    erasmus_ids = fields.One2many(
        "custom_partner_fields.erasmus", "partner_id", string="Erasmus"
    )

    def check_access(self):
        # Override google_drive_folder.mixin.check_access()
        if self.env.user._is_admin():
            _logger.debug("check_access() : Administrator can access anyone's files")    
            return True

        current = self.env.user.partner_id
        if current == self:
            _logger.debug("check_access() : Partner can always access his own files")    
            return True

        if current.employee:
            _logger.debug("check_access() : Employee can access anyone's files")    
            return True
        
        _logger.debug("check_access() : No access is granted")
        return False

class Company(models.Model):
    _inherit = "res.company"

    director_signature = fields.Binary(string="Director Signature")

    secretary_signature = fields.Binary(string="Secretarty Signature")


class Country(models.Model):
    """Country"""

    _inherit = "res.country"

    nis_code = fields.Char(string="NIS-code")

    in_use = fields.Boolean(string="In Use")


# custom_partner_fields


class TitleAccess(models.Model):
    _name = "custom_partner_fields.access_title"
    _description = "Title Access"

    name = fields.Char(
        string="Name of the access title",
        help="e.g.: Titre d'accès 1er cycle (art. 107)",
    )
    title = fields.Char(string="Intitulé")
    establishment = fields.Char(string="Etablissement")
    city = fields.Char(string="Ville")
    country_id = fields.Many2one("res.country", "Pays", ondelete="restrict")
    country = fields.Char(string="Pays (Ancien champ)", readonly=True)
    date = fields.Date(string="Date")

    partner_id = fields.Many2one("res.partner", string="Contact")

    type = fields.Selection(
        [
            ("mastery_of_french", "Mastery of French"),
            ("cess", "CESS"),
            ("bachelor", "Bachelor"),
        ],
        string="Type",
        tracking=True,
    )


class Erasmus(models.Model):
    _name = "custom_partner_fields.erasmus"
    _description = "Erasmus"

    establishment = fields.Char(string="Etablissement")
    city = fields.Char(string="Ville")
    country_id = fields.Many2one("res.country", "Pays", ondelete="restrict")
    country = fields.Char(string="Pays (Ancien champ)", readonly=True)

    start_date = fields.Date(string="Date de début")
    end_date = fields.Date(string="Date de fin")

    language = fields.Char(string="Langue")

    partner_id = fields.Many2one("res.partner", string="Contact")


class Internship(models.Model):
    _name = "custom_partner_fields.internship"
    _description = "Internship"

    establishment = fields.Char(string="Etablissement")
    city = fields.Char(string="Ville")
    country_id = fields.Many2one("res.country", "Pays", ondelete="restrict")
    country = fields.Char(string="Pays (Ancien champ)", readonly=True)

    start_date = fields.Date(string="Date de début")
    end_date = fields.Date(string="Date de fin")

    partner_id = fields.Many2one("res.partner", string="Contact")


class MemoirTitle(models.Model):
    _name = "custom_partner_fields.memoir_title"
    _description = "Memoir Title"

    name = fields.Char(string="Titre du mémoire/TFE")
    partner_id = fields.Many2one("res.partner", string="Contact")
