import logging

_logger = logging.getLogger(__name__)

from odoo import api, fields, models


class Menu(models.Model):
    _inherit = "website.menu"

    public = fields.Boolean("Public", default=True)
    student = fields.Boolean("Student", default=False)
    teacher = fields.Boolean("Teacher", default=False)
    employee = fields.Boolean("Employee", default=False)

    @api.model
    def init_school_portal_menu(self):
        _logger.info("Init school portal menu")

        website_id = self.env["website"].get_current_website().id
        reservation_menus = self.env["website.menu"].search(
            [
                ("url", "=", "/reservations/mes-reservations"),
                ("website_id", "=", website_id),
            ]
        )

        # Ajout des points de menu des réservations
        if len(reservation_menus) == 0:
            default_main_menu_id = (
                self.env["website.menu"]
                .search([("parent_id", "=", None), ("website_id", "=", website_id)])
                .id
            )

            parent = self.env["website.menu"].create(
                {
                    "name": "Réservations",
                    "url": None,
                    "page_id": None,
                    "parent_id": default_main_menu_id,
                    "website_id": website_id,
                    "public": False,
                    "student": True,
                    "teacher": True,
                    "employee": True,
                }
            )

            self.env["website.menu"].create(
                {
                    "name": "Mes réservations",
                    "url": "/reservations/mes-reservations",
                    "page_id": None,
                    "parent_id": parent.id,
                    "website_id": website_id,
                    "public": False,
                    "student": True,
                    "teacher": True,
                    "employee": True,
                }
            )

            self.env["website.menu"].create(
                {
                    "name": "Réserver une salle",
                    "url": "/reservations/creation",
                    "page_id": None,
                    "parent_id": parent.id,
                    "website_id": website_id,
                    "public": False,
                    "student": True,
                    "teacher": True,
                    "employee": True,
                }
            )

            self.env.cr.commit()

        # Suppression des points de menu Accueil et Contactez-nous
        self.env["website.menu"].search([("url", "=", "/")]).unlink()
        self.env["website.menu"].search([("url", "=", "/contactus")]).unlink()
        self.env.cr.commit()

    def contains(self, list, filter):
        for x in list:
            if filter(x):
                return True
        return False
