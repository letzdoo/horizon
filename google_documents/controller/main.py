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

import io
import logging

import werkzeug.utils

from odoo import http
from odoo.http import Response, request

try:
    from werkzeug.utils import send_file
except ImportError:
    from odoo.tools._vendor.send_file import send_file

_logger = logging.getLogger(__name__)


class GoogleServiceController(http.Controller):
    @http.route("/google_documents/authorize", type="http", auth="user")
    def google_drive_service_authorize(
        self, state, code, scope, redirect=None, *args, **kw
    ):
        _logger.info("Authorize response : %s %s %s" % (state, code, scope))
        drive_service = request.env["google.drive.service"].browse(state)
        drive_service.drive_auth_code = code
        return werkzeug.utils.redirect(
            "/web#view_type=form&model=google.drive.service&id=%s" % state
        )

    @http.route("/google_documents/refresh_token", type="http", auth="user")
    def google_drive_service_refresh_token(self, redirect=None, *args, **kw):
        _logger.info("Refresh Token response : %s" % (request))
        return "done"

    @http.route(
        "/google_documents/view_file/<string:google_drive_file_id>",
        type="http",
        auth="user",
        website=True,
    )
    def google_drive_view_file(self, google_drive_file_id, redirect=None, **post):
        google_drive_file = (
            request.env["google_drive_file"]
            .sudo()
            .search([("googe_drive_id", "=", google_drive_file_id)])
        )  # WARNING TYPO "googe" !
        if google_drive_file:
            if not google_drive_file.check_access():
                _logger.error(
                    "Forbidden access to Google Drive file %s by user with ID %s"
                    % (google_drive_file.googe_drive_id, request.session.uid)
                )
                return Response(template="google_documents.file_404", status=404)
            google_service = request.env.company.google_drive_id
            try:
                google_drive_file_bytes = google_service.sudo().get_file(
                    google_drive_file
                )
                google_drive_file_content = io.BytesIO(google_drive_file_bytes)
            except:
                return Response(template="google_documents.file_404", status=404)
            if google_drive_file_content:
                return send_file(
                    google_drive_file_content,
                    request.httprequest.environ,
                    google_drive_file.mimeType,
                    False,
                    google_drive_file.name,
                )

        return Response(template="google_documents.file_404", status=404)
