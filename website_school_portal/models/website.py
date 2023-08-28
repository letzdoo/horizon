import base64
import logging

_logger = logging.getLogger(__name__)

from odoo import api, models, tools
from odoo.modules.module import get_resource_path


class WebsiteHorizon(models.Model):
    _inherit = "website"

    @api.model
    def init_horizon(self):
        _logger.info("Init Horizon...")
        website = self.get_current_website()
        # Default site name
        website.name = "Horizon"
        # Default logo and icon
        logo_path = get_resource_path("website_school_portal", "static/img/logo.png")
        with tools.file_open(logo_path, "rb") as f:  # Same as "try with ressource"
            content = base64.b64encode(f.read())
        if content:
            website.logo = content
            website.favicon = content

        # To switch view to active/inactive based on key
        def toggle_view(viewkey: str, active: bool, like: bool = False):
            View = self.env["ir.ui.view"].sudo().with_context(active_test=False)
            if like:
                views = View.search([("key", "like", viewkey)])
            else:
                views = View.search([("key", "=", viewkey)])
            if not active:
                views.reset_arch(mode="hard")
            views.write({"active": active})

        # Default header and footer - Customized by Horizon
        toggle_view("website.template_footer%", False, True)
        toggle_view("website.footer_custom", True)
        toggle_view("website.template_header%", False, True)
        toggle_view("website.template_header_default", True)
        # No call to action
        toggle_view("website.header_call_to_action", False)
        # ScrollToTop
        toggle_view("website.option_footer_scrolltop", True)
        # Language Selector
        toggle_view("website.header_language_selector", True)

    # is_crm_installed = self.pool.get('ir.module.module').search(cr,uid,[('state','=','installed'), ('name','=','crm'])
    # _logger.info('CTA : %s' % cta.key)

    def _search_get_details(self, search_type, order, options):
        result = []
        result.append(
            self.env["school.program"]._search_get_detail(self, order, options)
        )
        if search_type in ["pages", "all"]:
            result.append(
                self.env["website.page"]._search_get_detail(self, order, options)
            )
        return result
