# Copyright 2024 Neodiensis
#     License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models

# import logging
# from pprint import pprint
# _logger = logging.getLogger(__name__)


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    display_in_home_menu = fields.Boolean(
        string="Displayed in home menu",
        help="Menu to add in the Horizon Home menu.",
        default=False,
    )
    simulated_id = fields.Many2one(
        "ir.ui.menu",
        string="Simulated Menu",
        help="Already existing menu that this Home menu must simulate.",
        default=False,
        index=True,
        ondelete="restrict",
    )

    def load_web_menus(self, debug):
        web_menus = super().load_web_menus(debug)
        new_web_menus = {}  # dict
        selection = self.search([("display_in_home_menu", "=", True)])
        home_menus = selection.read(["id", "simulated_id"]) if selection else []

        for key, web_menu in web_menus.items():
            try:
                index = selection.ids.index(web_menu["id"])
                display_in_home_menu = True
                simulated_menu = home_menus[index]["simulated_id"]
                (simulated_id, simulated_label) = (
                    simulated_menu if simulated_menu else (web_menu["id"], "")
                )
            except ValueError:
                display_in_home_menu = False
                simulated_id = web_menu["id"]
            web_menu["displayInHomeMenu"] = display_in_home_menu
            web_menu["simulatedMenuID"] = simulated_id
            new_web_menus[key] = web_menu

        return new_web_menus
