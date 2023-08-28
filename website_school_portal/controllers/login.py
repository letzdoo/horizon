from odoo.addons.website.controllers.main import Website

import logging

_logger = logging.getLogger(__name__)


class WebsiteMenuController(Website):
    def _login_redirect(self, uid, redirect=None):
        if not redirect:
            return super()._login_redirect(uid, "/my/home")
        else:
            return super()._login_redirect(uid, redirect)
