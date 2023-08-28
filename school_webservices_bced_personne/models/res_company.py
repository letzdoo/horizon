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

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class ResUser(models.Model):
    _inherit = "res.users"

    national_id = fields.Char(string="National ID")


class Partner(models.Model):
    _inherit = "res.partner"

    inscription_ids = fields.One2many(
        "school.bced.inscription",
        "partner_id",
        string="BCED Inscriptions",
        ondelete="restrict",
    )
    inscription_count = fields.Integer(
        compute="_compute_inscription_count", string="BCED Inscription Count"
    )

    @api.depends("inscription_ids")
    def _compute_inscription_count(self):
        for rec in self:
            rec.inscription_count = len(
                rec.inscription_ids.filtered(
                    lambda inscription: inscription.reference != False
                )
            )

    def action_update_bced_personne(self):
        for rec in self:
            if rec.inscription_ids:
                ex = None
                for ins in rec.inscription_ids:
                    try:
                        # TODO : update contact information from BCED Web Service
                        ins.action_update_partner_information()
                        if (
                            self.env.context.get("params", {}).get("view_type")
                            == "list"
                        ):
                            next_action = {"type": "ir.actions.client", "tag": "reload"}
                        else:
                            next_action = {"type": "ir.actions.act_window_close"}
                        return {
                            "type": "ir.actions.client",
                            "tag": "display_notification",
                            "params": {
                                "type": "success",
                                "message": _("Information updated from BCED"),
                                "next": next_action,
                            },
                        }
                    except Exception as e:
                        ex = e
                _logger.error("Error while updating contact information : %s", ex)
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
