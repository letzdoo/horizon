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

from odoo import api, models
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = "ir.http"

    @api.model
    def get_frontend_session_info(self):
        session_info = super(Http, self).get_frontend_session_info()

        all_forms_ids = (
            self.env["formio.form"]
            .sudo()
            .search([["user_id", "=", request.env.user.id]])
        )

        if request.env.user.partner_id.student:
            val = "student"
        elif request.env.user.partner_id.teacher:
            val = "teacher"
        elif request.env.user.partner_id.employee:
            val = "employee"
        elif all_forms_ids.filtered(
            lambda f: f.name == "new_contact" and f.state in ["DRAFT", "PENDING"]
        ):
            val = "info-form"
        elif all_forms_ids.filtered(
            lambda f: f.name == "new_contact" and f.state == "COMPLETE"
        ):
            val = "info-form-complete"
        else:
            val = "no-form"

        session_info.update(
            {
                "horizon_state": val,
                "horizon_user_forms": [
                    [f.id, f.name, f.state, f.uuid]
                    for f in all_forms_ids.filtered(lambda f: f.name == "new_contact")
                ],
            }
        )
        return session_info
