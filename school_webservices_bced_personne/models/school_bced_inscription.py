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
import logging.config

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# logging.config.dictConfig({
#     'version': 1,
#     'formatters': {
#         'verbose': {
#             'format': '%(name)s: %(message)s'
#         }
#     },
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'verbose',
#         },
#     },
#     'loggers': {
#         'zeep.transports': {
#             'level': 'DEBUG',
#             'propagate': True,
#             'handlers': ['console'],
#         },
#     }
# })


def getFRDescription(value):
    for x in value["description"]:
        if x["language"] == "fr":
            return x["_value_1"]
        else:
            ret = x["_value_1"]
    return ret


class BCEDInscription(models.Model):
    _name = "school.bced.inscription"
    _description = "BCED Inscription"

    partner_id = fields.Many2one(
        "res.partner", string="Partner", required=True, ondelete="restrict"
    )
    reference = fields.Char(string="Reference")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

    legal_context = fields.Selection(
        [
            ("student", "This partner applies to become a student"),
            ("teacher", "This partner applies to become a teacher"),
            ("employee", "This partner applies to become an employee"),
        ],
        required=True,
        string="Legal Context",
    )

    def action_submit(self):
        ws = self.env["school.webservice"].search(
            [("name", "=", "bced_inscription")], limit=1
        )
        for rec in self:
            res = ws.publishInscription(rec)
            if res:
                rec.reference = res["inscriptionReference"]

    def action_revoke(self):
        ws = self.env["school.webservice"].search(
            [("name", "=", "bced_inscription")], limit=1
        )
        for rec in self:
            res = ws.closeInscription(rec)
            if res:
                rec.end_date = fields.Date.today()

    def action_extend(self):
        ws = self.env["school.webservice"].search(
            [("name", "=", "bced_inscription")], limit=1
        )
        for rec in self:
            res = ws.extendInscription(rec)
            if res:
                rec.end_date = fields.date.strftime(
                    res["inscription"]["period"]["endDate"], "%Y-%m-%d"
                )

    @api.model
    def update_partner_information(self, partner_id, data):
        partner_id.reg_number = data["personNumber"]
        partner_id.firstname = data["name"]["firstName"][0]
        partner_id.lastname = " ".join(data["name"]["lastName"])
        if len(data["name"]["firstName"]) > 1:
            partner_id.initials = ",".join(
                map(lambda x: x[0], data["name"]["firstName"][1:])
            )
        else:
            partner_id.initials = ""
        if data["gender"]:
            partner_id.gender = (
                "male" if data["gender"]["code"]["_value_1"] == "M" else "female"
            )
        if data["nationalities"]:
            partner_id.nationality_ids = self.env["res.country"].search(
                [
                    (
                        "code",
                        "in",
                        [
                            x["code"]["_value_1"]
                            for x in data["nationalities"]["nationality"]
                        ],
                    )
                ]
            )
        if data["addresses"]:
            for address in data["addresses"]["address"]:
                # Diplomatic is for foreigner
                if address["addressType"] == "Diplomatic":
                    partner_id.street = address["plainText"][0]["_value_1"]
                    partner_id.street2 = ""
                    partner_id.zip = ""
                    partner_id.city = ""
                    partner_id.state_id = False
                    partner_id.country_id = (
                        self.env["res.country"]
                        .search(
                            [("code", "=", address["country"][0]["code"]["_value_1"])],
                            limit=1,
                        )
                        .id
                    )
                if address["addressType"] == "Residential":
                    street_name = getFRDescription(address["street"])
                    if address["boxNumber"]:
                        partner_id.street = " ".join(
                            [street_name, address["houseNumber"], address["boxNumber"]]
                        )
                    else:
                        partner_id.street = " ".join(
                            [street_name, address["houseNumber"]]
                        )
                    partner_id.street2 = ""
                    partner_id.zip = address["postCode"]["code"]["_value_1"]
                    partner_id.city = getFRDescription(address["municipality"])
                    partner_id.state_id = False
                    partner_id.country_id = (
                        self.env["res.country"]
                        .search(
                            [("code", "=", address["country"][0]["code"]["_value_1"])],
                            limit=1,
                        )
                        .id
                    )
                elif address["addressType"] == "PostAddress":
                    street_name = getFRDescription(address["street"])
                    if address["boxNumber"]:
                        partner_id.secondary_street = " ".join(
                            [street_name, address["houseNumber"], address["boxNumber"]]
                        )
                    else:
                        partner_id.secondary_street = " ".join(
                            [street_name, address["houseNumber"]]
                        )
                    partner_id.secondary_street2 = ""
                    partner_id.secondary_zip = address["postCode"]["code"]["_value_1"]
                    partner_id.secondary_city = getFRDescription(
                        address["municipality"]
                    )
                    partner_id.secondary_state_id = False
                    partner_id.secondary_country_id = (
                        self.env["res.country"]
                        .search(
                            [("code", "=", address["country"][0]["code"]["_value_1"])],
                            limit=1,
                        )
                        .id
                    )
        partner_id.birthdate_date = fields.Date.to_date(
            data["birth"]["officialBirthDate"]
        )
        if data["birth"]["birthPlace"]:
            partner_id.birthplace = getFRDescription(data["birth"]["birthPlace"])

    def action_update_partner_information(self):
        ws = self.env["school.webservice"].search(
            [("name", "=", "bced_personne")], limit=1
        )
        for rec in self:
            if not rec.reference:
                raise UserError(
                    _(
                        "No reference found for this partner, please submit first to BCDE service."
                    )
                )
            # We are registered so we can proceed with data usage
            data = ws.getPerson(rec.partner_id.reg_number)
            if data:
                self.update_partner_information(self.partner_id, data)
