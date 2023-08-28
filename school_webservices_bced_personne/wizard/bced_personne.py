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
import traceback

from odoo import _, fields, models
from odoo.tools import date_utils

import json
from zeep import helpers

_logger = logging.getLogger(__name__)


class BCEDPersonne(models.TransientModel):
    _name = "school.bced_personne_wizard"
    _description = "BCED Personne Wizard"

    student_id = fields.Many2one("res.partner", string="Student", required=True)

    student_name = fields.Char(related="student_id.name", string="Name", readonly=True)
    student_image_512 = fields.Binary(
        "Image", attachment=True, related="student_id.image_512", readonly=True
    )
    student_niss = fields.Char(
        related="student_id.reg_number", string="Niss", readonly=True
    )
    student_firstname = fields.Char(
        related="student_id.firstname", string="First Name", readonly=True
    )
    student_lastname = fields.Char(
        related="student_id.lastname", string="Last Name", readonly=True
    )
    student_birthdate_date = fields.Date(
        related="student_id.birthdate_date", string="Birth Date", readonly=True
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("no_bced", "No BCED"),
            ("candidate_bced", "Candidate BCED"),
            ("bced", "Has BCED"),
        ],
        string="State",
        default="draft",
    )

    candidate_person_ids = fields.One2many(
        "school.bced_personne_summary", "wizard_id", string="Candidate Persons"
    )

    selected_person_id = fields.Many2one(
        "school.bced_personne_summary", string="Selected Person"
    )

    legal_context = fields.Selection(
        [
            ("empty", "Please select a legal context"),
            ("student", "This partner applies to become a student"),
            ("teacher", "This partner applies to become a teacher"),
            ("employee", "This partner applies to become an employee"),
        ],
        required=True,
        string="Legal Context",
        default="empty",
    )

    def action_retrieve_bced_persons(self):
        self.ensure_one()
        ws = self.env["school.webservice"].search(
            [("name", "=", "bced_personne")], limit=1
        )
        data = ws.searchPersonByName(self.student_id)
        if data.status and data.status["code"] == "SOA0000000":
            self.state = "candidate_bced"
            if data.persons and data.persons.person:
                for person in data.persons.person:
                    self.candidate_person_ids |= self.candidate_person_ids.create(
                        {
                            "firstname": " ".join(person.name.firstName),
                            "lastname": " ".join(person.name.lastName),
                            # parse birthdate
                            "birthdate": fields.Date.to_date(
                                person.birth.officialBirthDate
                            ),
                            "niss": person.personNumber,
                            "wizard_id": self.id,
                            "data": json.dumps(
                                helpers.serialize_object(person, dict),
                                separators=(",", ":"),
                                default=date_utils.json_default,
                            ),
                        }
                    )
        else:
            self.state = "no_bced"
        return {
            "type": "ir.actions.act_window",
            "name": "BCED Personne",
            "view_mode": "form",
            "res_model": "school.bced_personne_wizard",
            "res_id": self.id,
            "target": "new",
        }

    def action_no_bced_personne(self):
        self.ensure_one()
        self.state = "no_bced"
        return {
            "type": "ir.actions.act_window",
            "name": "BCED Personne",
            "view_mode": "form",
            "res_model": "school.bced_personne_wizard",
            "res_id": self.id,
            "target": "new",
        }

    def action_link_bced_personne(self):
        self.ensure_one()
        try:
            current_inscr = self.env["school.bced.inscription"].search(
                [("partner_id", "=", self.student_id.id)]
            )
            if current_inscr:
                current_inscr.action_update_partner_information()
            else:
                new_inscription = self.env["school.bced.inscription"].create(
                    {
                        "partner_id": self.student_id.id,
                        "start_date": fields.Date.today(),
                        "legal_context": self.legal_context,
                    }
                )
                # We update based on information retrieved from BCED on search niss and gender
                new_inscription.update_partner_information(
                    self.student_id, json.loads(self.selected_person_id.data)
                )
                new_inscription.action_submit()
                new_inscription.action_update_partner_information()
        except Exception as e:
            _logger.error("Error while updating contact information : %s", e)
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "message": _(
                        "Error while updating contact information : %s"
                        % traceback.format_exc()
                    ),
                    "next": {"type": "ir.actions.act_window_close"},
                    "sticky": False,
                    "type": "warning",
                },
            }

    def action_create_bced_personne(self):
        self.ensure_one()
        try:
            ws = self.env["school.webservice"].search(
                [("name", "=", "bced_personne")], limit=1
            )
            bisNumber = ws.publishPerson(self.student_id)
            if bisNumber:
                self.student_id.reg_number = bisNumber
                new_inscription = self.env["school.bced.inscription"].create(
                    {
                        "partner_id": self.student_id.id,
                        "start_date": fields.Date.today(),
                        "legal_context": self.legal_context,
                    }
                )
                new_inscription.action_submit()
        except Exception as e:
            _logger.error("Error while creating a bis number : %s", e)
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "message": _(
                        "Error while creating a bis number : %s"
                        % traceback.format_exc()
                    ),
                    "next": {"type": "ir.actions.act_window_close"},
                    "sticky": False,
                    "type": "warning",
                },
            }


class BCEDPersonneSummary(models.TransientModel):
    _name = "school.bced_personne_summary"
    _description = "BCED Personne Summary"

    firstname = fields.Char(string="First Name")
    lastname = fields.Char(string="Last Name")
    birthdate = fields.Date(string="Birth Date")
    niss = fields.Char(string="Niss")

    data = fields.Text(string="Data")

    wizard_id = fields.Many2one("school.bced_personne_wizard", string="Wizard")

    def action_use_person(self):
        self.ensure_one()
        self.wizard_id.selected_person_id = self.id
        self.wizard_id.state = "bced"
        return {
            "type": "ir.actions.act_window",
            "name": "BCED Personne",
            "view_mode": "form",
            "res_model": "school.bced_personne_wizard",
            "res_id": self.wizard_id.id,
            "target": "new",
        }
