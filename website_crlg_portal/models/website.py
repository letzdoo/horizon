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

        # Default color palette
        url = "/website/static/src/scss/options/user_values.scss"
        selected_palette_name = "crlg"
        values = {"color-palettes-name": "'%s'" % selected_palette_name}
        self.env["web_editor.assets"].make_scss_customization(url, values)

        if isinstance(selected_palette_name, list):
            url = "/website/static/src/scss/options/colors/user_color_palette.scss"
            values = {
                f"o-color-{i}": color
                for i, color in enumerate(selected_palette_name, 1)
            }
            self.env["web_editor.assets"].make_scss_customization(url, values)
