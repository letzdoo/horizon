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
import json
import logging

import requests
from requests.exceptions import Timeout

from odoo import fields, models, tools

_logger = logging.getLogger(__name__)


class Registration(models.Model):
    """Registration"""

    _name = "school.registration"
    _description = "Registration of new/existing students"
    _inherit = [
        "mail.thread",
        "school.uid.mixin",
        "school.year_sequence.mixin",
        "school.open.form.mixin",
    ]

    year_id = fields.Many2one("school.year", required=True, string="Year")

    student_id = fields.Many2one("res.partner", string="Student")
    student_user_id = fields.Many2one(
        "res.users", string="Student User", compute="_compute_student_user_id"
    )

    def _compute_student_user_id(self):
        for rec in self:
            self.env["res.users"].search(["partner_id", "=", rec.id])

    name = fields.Char(related="student_id.name")
    email = fields.Char(related="student_id.email")
    email_personnel = fields.Char(related="student_id.email_personnel")

    image_1920 = fields.Binary(
        "Image", attachment=True, related="student_id.image_1920"
    )
    image_128 = fields.Binary("Image", attachment=True, related="student_id.image_128")

    kanban_state = fields.Selection(
        [("normal", "In Progress"), ("done", "Ready"), ("blocked", "Blocked")],
        string="Status",
        copy=False,
        default="blocked",
        required=True,
        readonly=False,
        store=True,
        tracking=True,
    )

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
        copy=False,
        help=" * The 'Draft' status is used when a new registration is created and not running yet.\n"
        " * The 'Active' status is when a registration is ready to be processed.\n"
        " * The 'Archived' status is used when a registration is obsolete and shall be archived.",
        tracking=True,
    )

    contact_form_id = fields.Many2one(
        "formio.form",
        string="Contact Form",
        tracking=True,
        domain="[['submission_partner_id','=',student_id],['name','=','new_contact']]",
    )

    contact_form_data = fields.Text(related="contact_form_id.submission_data")

    contact_form_uuid = fields.Char(related="contact_form_id.uuid")

    contact_form_data_pretty = fields.Text(
        related="contact_form_id.submission_data_pretty"
    )

    contact_form_iframe = fields.Html(compute="_compute_form_iframe", sanitize=False)

    registration_form_id = fields.Many2one(
        "formio.form",
        string="Registration Form",
        tracking=True,
        domain="[['submission_partner_id','=',student_id],['name','=','new_registration']]",
    )

    registration_form_data = fields.Text(related="registration_form_id.submission_data")

    registration_form_uuid = fields.Char(related="registration_form_id.uuid")

    registration_form_data_pretty = fields.Text(
        related="registration_form_id.submission_data_pretty"
    )

    registration_form_iframe = fields.Html(
        compute="_compute_form_iframe", sanitize=False
    )

    def _compute_form_iframe(self):
        for rec in self:
            if rec.contact_form_id:
                rec.contact_form_iframe = f"""<iframe src='/formio/form/{rec.contact_form_uuid}'
                                                   style="display: block;       /* iframes are inline by default */
                                                          background: #fff;
                                                          border: none;         /* Reset default border */
                                                          width: 100%;
                                                          height: 1200px;" title="Contact Form"></iframe>"""
            else:
                rec.contact_form_iframe = """<h4>No contact form</h4>"""
            if rec.registration_form_id:
                rec.registration_form_iframe = f"""<iframe src='/formio/form/{rec.registration_form_uuid}'
                                                   style="display: block;       /* iframes are inline by default */
                                                          background: #fff;
                                                          border: none;         /* Reset default border */
                                                          width: 100%;
                                                          height: 1200px;" title="Contact Form"></iframe>"""
            else:
                rec.registration_form_iframe = """<h4>No registration form</h4>"""

    program_id = fields.Many2one(
        "school.program", string="Program", domain="[['year_id','=',year_id]]"
    )

    speciality_id = speciality_id = fields.Many2one(
        "school.speciality",
        related="program_id.speciality_id",
        string="Speciality",
        store=True,
        readonly=True,
    )

    forms_attachment_ids = fields.Many2many(
        "ir.attachment", string="Attachments", compute="_compute_forms_attachment_ids"
    )

    def _compute_forms_attachment_ids(self):
        for rec in self:
            rec.forms_attachment_ids = self.env["ir.attachment"].search(
                [
                    ["res_model", "=", "formio.form"],
                    [
                        "res_id",
                        "in",
                        [rec.contact_form_id.id, rec.registration_form_id.id],
                    ],
                ]
            )

    def action_view_contact_formio(self):
        self.ensure_one()
        action = self.contact_form_id.action_view_formio()
        action["target"] = "new"
        return action

    def action_view_registration_formio(self):
        self.ensure_one()
        action = self.registration_form_id.action_view_formio()
        action["target"] = "new"
        return action

    def to_draft(self):
        return self.write({"state": "draft"})

    def activate(self):
        return self.write({"state": "active"})

    def archive(self):
        return self.write({"state": "archived"})

    def _format_date(self, date_str):
        day, month, year = date_str.split("/")
        return f"{year}-{month}-{day}"

    def _extract_base64_data_from_url(self, url, timeout=10):
        try:
            # Retrieve the image from the URL with a timeout
            response = requests.get(url, timeout=timeout)
            if response and response.ok:
                return tools.image_process(response.content)
            else:
                return False
        except Timeout:
            _logger.debug("Request timed out.")
            return False

    def _extract_base64_data_from_data_url(self, data_url):
        # split the data URL into its components
        parts = data_url.split(",")
        # extract the base64-encoded data from the URL
        base64_data = parts[1]
        return base64_data

    def action_fill_program_data(self):
        for rec in self:
            rec.sudo().message_post(
                body=f"Update Program Information by {self.env.user.name}"
            )
            if rec.registration_form_id.program_id:
                rec.program_id = rec.registration_form_id.program_id

    def action_fill_partner_data(self):
        for rec in self:
            rec.sudo().message_post(
                body=f"Update Contact Information by {self.env.user.name}"
            )
            contact_data = json.loads(rec.contact_form_data)
            student_id = rec.student_id
            student_id.lastname = contact_data.get("nom", False)
            student_id.firstname = contact_data.get("prenom", False)
            student_id.gender = contact_data.get("sexe", False)
            if contact_data.get("dateDeNaissance", False):
                student_id.birthdate_date = fields.Datetime.from_string(
                    rec._format_date(contact_data.get("dateDeNaissance"))
                )
            student_id.birthplace = contact_data.get("lieuDeNaiss", False)
            student_id.lastname = contact_data.get("nom", False)
            if contact_data.get("brith_country", False):
                student_id.birthcountry = self.env["res.country"].browse(
                    contact_data.get("brith_country")
                )
            # student_id.nationalites
            try:
                if contact_data.get("photo", False):
                    url = contact_data.get("photo")[0]["url"]
                    if url.startswith("data"):
                        student_id.image_1920 = rec._extract_base64_data_from_data_url(
                            url
                        )
                    else:
                        attachment_id = contact_data.get("photo")[0]["data"]["id"]
                        if attachment_id:
                            attachment = self.env["ir.attachment"].browse(attachment_id)
                            if attachment and attachment.type == "binary":
                                student_id.image_1920 = attachment.datas
            except BaseException as e:
                # We do our best here
                _logger.info("Error while updating photo %s" % e)
            student_id.street = contact_data.get("adresseLigne", False)
            student_id.city = contact_data.get("ville", False)
            student_id.zip = contact_data.get("codePostal", False)
            if contact_data.get("country", False):
                student_id.country_id = self.env["res.country"].browse(
                    contact_data.get("country")
                )
            student_id.secondary_street = contact_data.get("adresseLigne1", False)
            student_id.secondary_city = contact_data.get("ville1", False)
            student_id.secondary_zip = contact_data.get("codePostal1", False)
            if contact_data.get("country1", False):
                student_id.secondary_country_id = self.env["res.country"].browse(
                    contact_data.get("country1")
                )
            student_id.phone = contact_data.get("telephonePortab", False)
            student_id.email_personnel = contact_data.get("email", False)
            student_id.reg_number = contact_data.get("numeroDeRegistreNational", False)

    def action_open_student(self):
        self.ensure_one()
        return {
            "name": "Student",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "res.partner",
            "res_id": self.student_id.id,
            "type": "ir.actions.act_window",
            "target": "current",
        }

    _sql_constraints = [
        (
            "registration_uniq",
            "unique (registration_form_id)",
            "Registration already exists for that registration !",
        ),
    ]


class Form(models.Model):
    """Form"""

    _inherit = "formio.form"

    registration_id = fields.Many2one("school.registration", string="Registration")

    submission_data_pretty = fields.Text(
        string="Data Pretty Print", compute="_compute_submission_data_pretty"
    )

    def action_open_form(self):
        self.ensure_one()
        action = self.action_view_formio()
        action["target"] = "new"
        return action

    def _compute_submission_data_pretty(self):
        for rec in self:
            if rec.submission_data:
                json_object = json.loads(rec.submission_data)
                json_formatted_str = json.dumps(json_object, indent=2)
                rec.submission_data_pretty = json_formatted_str
            else:
                rec.submission_data_pretty = False

    def write(self, vals):
        res = super(Form, self).write(vals)
        if (
            "submission_data" in vals
            and "state" in vals
            and vals["state"] == "COMPLETE"
        ):
            self._create_or_update_registration()
        return res

    def _create_or_update_registration(self):
        registration_open_year_id = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("school.registration_open_year_id", "0")
        )
        for rec in self:
            if rec.name == "new_contact" and rec.submission_partner_id:
                reg = self.env["school.registration"].search(
                    [
                        ["year_id", "=", registration_open_year_id],
                        ["student_id", "=", rec.submission_partner_id.id],
                    ]
                )
                if reg:
                    reg.contact_form_id = rec
                else:
                    self.env["school.registration"].create(
                        {
                            "year_id": registration_open_year_id,
                            "student_id": rec.submission_partner_id.id,
                            "contact_form_id": rec.id,
                        }
                    )
            if rec.name == "new_registration" and rec.submission_partner_id:
                reg = self.env["school.registration"].search(
                    [
                        ["year_id", "=", registration_open_year_id],
                        ["student_id", "=", rec.submission_partner_id.id],
                        ["registration_form_id", "=", False],
                    ]
                )
                if reg:
                    reg.registration_form_id = rec.id
                    rec.registration_id = reg.id
                else:
                    reg = self.env["school.registration"].search(
                        [
                            ["year_id", "=", registration_open_year_id],
                            ["student_id", "=", rec.submission_partner_id.id],
                            ["registration_form_id", "=", rec.id],
                        ]
                    )
                    if not reg:
                        contact_form_ids = rec.search(
                            [
                                ["name", "=", "new_contact"],
                                [
                                    "submission_partner_id",
                                    "=",
                                    rec.submission_partner_id.id,
                                ],
                                ["state", "=", "COMPLETE"],
                            ]
                        )
                        reg = self.env["school.registration"].create(
                            {
                                "year_id": registration_open_year_id,
                                "student_id": rec.submission_partner_id.id,
                                "contact_form_id": max(contact_form_ids.ids)
                                if contact_form_ids
                                else False,
                                "registration_form_id": rec.id,
                            }
                        )
                        rec.registration_id = reg.id

    # Fields for registrations forms

    program_id = fields.Many2one(
        "school.program", string="Program", compute="_compute_program_id"
    )

    def _compute_program_id(self):
        for rec in self:
            if rec.name == "new_registration" and rec.submission_data:
                data = json.loads(rec.submission_data)
                if data.get("choixDuCycle") or data.get("choixDuCycle1"):
                    program_id = int(
                        data.get("choixDuCycle") or data.get("choixDuCycle1")
                    )
                    if program_id:
                        rec.program_id = self.env["school.program"].browse(program_id)
                    else:
                        rec.program_id = False
                else:
                    rec.program_id = False
