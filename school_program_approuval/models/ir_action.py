from odoo import fields, models


class ActWindowView(models.Model):
    _inherit = "ir.actions.act_window.view"

    view_mode = fields.Selection(
        selection_add=[("program_approuval", "Program Approuval")],
        ondelete={"program_approuval": "cascade"},
    )
