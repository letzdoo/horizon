import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class Menu(models.Model):
    _inherit = "website.menu"

    @api.model
    def init_crlg_menu(self):
        _logger.info("Init crlg menu")
        self.env["website.menu"].search([])

        website_id = self.env["website"].get_current_website().id
        valves_menus = self.env["website.menu"].search(
            [("url", "=", "/etudiants-info"), ("website_id", "=", website_id)]
        )

        # Ajout des points de menu des valves
        if len(valves_menus) == 0:
            default_main_menu_id = (
                self.env["website.menu"]
                .search([("parent_id", "=", None), ("website_id", "=", website_id)])
                .id
            )

            self.env["website.menu"].create(
                {
                    "name": "Valves étudiants",
                    "url": "/etudiants-info",
                    "page_id": None,
                    "parent_id": default_main_menu_id,
                    "website_id": website_id,
                    "sequence": 30,
                    "public": False,
                    "student": True,
                    "teacher": True,
                    "employee": True,
                }
            )

            self.env["website.menu"].create(
                {
                    "name": "Valves professeurs",
                    "url": "/professeurs-info",
                    "page_id": None,
                    "parent_id": default_main_menu_id,
                    "website_id": website_id,
                    "sequence": 40,
                    "public": False,
                    "student": False,
                    "teacher": True,
                    "employee": True,
                }
            )
