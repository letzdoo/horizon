import logging

from odoo import http
from odoo.http import Response, request

_logger = logging.getLogger(__name__)


class MesDonneesController(http.Controller):
    @http.route("/mes-donnees/mon-programme", type="http", auth="user", website=True)
    def responsive_blocs(self, debug=False, **k):
        if not (request.env.user.partner_id.student or request.env.is_admin()):
            return Response(template="website_school_portal.hz_page_403", status=403)
        values = {
            "user": request.env.user,
            "blocs": request.env["school.individual_bloc"]
            .sudo()
            .search(
                [
                    ("student_id", "=", request.env.user.partner_id.id),
                    ("year_id", "=", request.env.user.current_year_id.id),
                ]
            ),
            "display_results": request.env["ir.config_parameter"]
            .sudo()
            .get_param("school.display.results", "0"),
        }
        return request.render("website_school_portal.hz_blocs", values)

    @http.route("/mes-donnees/mes-documents", type="http", auth="user", website=True)
    def responsive_documents(self, debug=False, **k):
        if not (request.env.user.partner_id.student or request.env.is_admin()):
            return Response(template="website_school_portal.hz_page_403", status=403)
        user = request.env.user
        partner_id = user.partner_id
        values = {
            "user": user,
            "official_document_ids": partner_id.official_document_ids,
            "blocs": request.env["school.individual_bloc"]
            .sudo()
            .search(
                [
                    ("student_id", "=", request.env.user.partner_id.id),
                    ("year_id", "=", request.env.user.current_year_id.id),
                ]
            ),
        }
        return request.render("website_school_portal.hz_documents", values)
