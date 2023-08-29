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

from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal

_logger = logging.getLogger(__name__)


class CustomerPortal(CustomerPortal):
    @http.route(["/confirm_registration"], type="http", auth="user", website=True)
    def portal_order_page(self, **kw):
        partner_id = request.env.user.partner_id

        request.env.ref("school_registration.res_partner_category_registration_request")

        partner_id.write(
            {
                "category_id": [
                    (
                        4,
                        request.env.ref(
                            "school_registration.res_partner_category_registration_request"
                        ).id,
                    )
                ]
            }
        )

        values = {
            "partner_id": partner_id,
        }

        return request.render(
            "school_registration.registration_request_confirmation_template", values
        )
