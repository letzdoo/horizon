import logging
from datetime import datetime, timedelta

import werkzeug.utils

from odoo import fields, http
from odoo.http import request

_logger = logging.getLogger(__name__)


# Gestion des différentes routes pour les programmes de cours
class ReservationsController(http.Controller):
    @http.route("/reservations/creation", type="http", auth="user", website=True)
    def responsive_booking_new(self, debug=False, **k):

        from_hours = []
        to_hours = []

        to_hours.append("08:30")
        to_hours.append("08:45")

        for i in range(8, 23):
            from_hours.append(str(i).zfill(2) + ":00")
            if i < 22:
                from_hours.append(str(i).zfill(2) + ":15")
                from_hours.append(str(i).zfill(2) + ":30")
                from_hours.append(str(i).zfill(2) + ":45")

            to_hours.append(str(i + 1).zfill(2) + ":00")
            to_hours.append(str(i + 1).zfill(2) + ":15")
            to_hours.append(str(i + 1).zfill(2) + ":30")
            to_hours.append(str(i + 1).zfill(2) + ":45")

        values = {
            "user": request.env.user,
            "today": datetime.today(),
            "tomorrow": datetime.today() + timedelta(days=1),
            "from_hours": from_hours,
            "to_hours": to_hours,
        }
        return request.render("website_school_portal.hz_booking_new", values)

    @http.route("/reservations/recherche", type="http", auth="user", website=True)
    def responsive_booking_search(self, debug=False, **k):
        values = {
            "user": request.env.user,
            "today": fields.Datetime.to_string(datetime.today()),
            "tomorrow": fields.Datetime.to_string(datetime.today() + timedelta(days=1)),
        }
        return request.render("website_school_portal.hz_booking_search", values)

    @http.route(
        "/reservations/mes-reservations", type="http", auth="user", website=True
    )
    def responsive_bookings(self, debug=False, **k):
        start = fields.Datetime.to_string(
            datetime.today().replace(hour=0, minute=0, second=0)
        )
        end = fields.Datetime.to_string(
            datetime.today().replace(hour=23, minute=59, second=59)
        )
        domain = [
            ("start", "<=", end),
            ("stop", ">=", start),
            ("user_id", "=", request.uid),
        ]
        domain_next = [
            (
                "start",
                "<=",
                fields.Datetime.to_string(
                    datetime.today().replace(hour=23, minute=59, second=59)
                    + timedelta(days=1)
                ),
            ),
            (
                "stop",
                ">=",
                fields.Datetime.to_string(
                    datetime.today().replace(hour=0, minute=0, second=0)
                    + timedelta(days=1)
                ),
            ),
            ("user_id", "=", request.uid),
        ]
        values = {
            "user": request.env.user,
            "bookings": request.env["calendar.event"]
            .sudo()
            .with_context(virtual_id=True, tz=request.env.user.tz)
            .search(domain, order="start asc"),
            "bookings_next": request.env["calendar.event"]
            .sudo()
            .with_context(virtual_id=True, tz=request.env.user.tz)
            .search(domain_next, order="start asc"),
        }
        return request.render("website_school_portal.hz_bookings", values)

    @http.route(
        "/reservations/suppression/<int:booking_id>",
        type="http",
        auth="user",
        website=True,
    )
    def responsive_delete_booking(self, booking_id, debug=False, **k):
        booking = request.env["calendar.event"].browse(booking_id)
        booking.unlink()
        return werkzeug.utils.redirect("/reservations/mes-reservations")
