import werkzeug.exceptions

from odoo import models
from odoo.http import request

class View(models.Model):

    _name = "ir.ui.view"
    _inherit = "ir.ui.view"

    def _handle_visibility(self, do_raise=True):
        try:
            return super(View, self)._handle_visibility(do_raise)
        except werkzeug.exceptions.Forbidden as e:
            if request.website.is_public_user() and e.description != "website_visibility_password_required":
                # Si une page n'est pas visible alors que le visiteur n'est pas connecté, on lui propose d'abord de se connecter pour pouvoir juger ensuite de ses droits.
                redirect = request.redirect_query('/web/login', {'redirect': request.httprequest.full_path}, 302)
                werkzeug.exceptions.abort(redirect)
            else:
                raise
