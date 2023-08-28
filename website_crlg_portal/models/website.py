import base64

from odoo import api, models, tools
from odoo.modules.module import get_resource_path


class WebsiteCRLG(models.Model):
    _inherit = "website"

    @api.model
    def init_crlg(self):
        website = self.get_current_website()
        # Default site name
        website.name = "Espace CRLG"
        # Default logo and icon
        logo_path = get_resource_path("website_crlg_portal", "static/img/logo.png")
        with tools.file_open(logo_path, "rb") as f:  # Same as "try with ressource"
            content = base64.b64encode(f.read())
        if content:
            website.logo = content
            website.favicon = content
