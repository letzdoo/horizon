##############################################################################
#
#    Copyright (c) 2023 ito-invest.lu
#                       Jerome Sonnet <jerome.sonnet@ito-invest.lu>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging

from odoo import _, api, fields, models, tools

_logger = logging.getLogger(__name__)


class Asset(models.Model):
    """School Asset"""

    _name = "school.asset"
    _description = "School Asset"
    _inherit = ["mail.thread", "image.mixin"]
    _order = "sequence"

    booking_policy = fields.Selection(
        [
            ("available", "Available"),
            ("preserved", "Preserved"),
            ("out", "Out"),
        ],
        string="Booking policy",
        index=True,
        default="available",
        copy=False,
        help=" * The 'Available' available to all users.\n"
        " * The 'Preserved' only employee can book.\n"
        " * The 'Out' no one can book.\n",
        tracking=True,
    )

    abandonned_date = fields.Date("Abandonned Date")

    def set_to_draft(self, context):
        # TODO use a workflow to make sure only valid changes are used.
        return self.write({"state": "draft"})

    def set_to_progress(self, context):
        # TODO use a workflow to make sure only valid changes are used.
        return self.write({"state": "progress"})

    sequence = fields.Integer(string="Sequence")
    name = fields.Char(required=True, translate=True)
    short_name = fields.Char(required=True, translate=True)
    active = fields.Boolean(name="Active", default=True)
    asset_type_id = fields.Many2one("school.asset_type", string="Asset Type")
    building_id = fields.Many2one("school.building", string="Building")
    tag_ids = fields.Many2many(
        "school.asset.tag",
        "school_asset_tag_rel",
        "asset_id",
        "tag_id",
        string="Tags",
        copy=True,
    )
    category_id = fields.Many2one("school.asset.category", string="Category")

    description = fields.Html("Description")

    require_validation = fields.Boolean(related="asset_type_id.require_validation")
    has_responsible = fields.Boolean(related="asset_type_id.has_responsible")
    responsible_id = fields.Many2one(
        "res.partner",
        string="Responsible",
        domain="[('type','=','contact')]",
        required=True,
        default=lambda self: self.env.user.partner_id,
    )
    linked_to_room = fields.Boolean(
        related="asset_type_id.linked_to_room", default=False
    )
    is_room = fields.Boolean(related="asset_type_id.is_room", store=True)
    room_id = fields.Many2one(
        "school.asset", string="Linked Room", domain="[('is_room','=',True)]"
    )


class AssetCategory(models.Model):
    _name = "school.asset.category"
    _description = "Asset Category"
    _order = "sequence, name"
    _inherit = ["image.mixin"]

    @api.constrains("parent_id")
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValueError(_("Error ! You cannot create recursive categories."))

    name = fields.Char(required=True, translate=True)
    parent_id = fields.Many2one(
        "school.asset.category", string="Parent Category", index=True
    )
    child_ids = fields.One2many(
        "school.asset.category", "parent_id", string="Children Categories"
    )
    is_leaf = fields.Boolean("Is Leaf", compute="_compute_is_leaf")
    sequence = fields.Integer(
        help="Gives the sequence order when displaying a list of asset categories."
    )

    def _compute_is_leaf(self):
        for rec in self:
            rec.is_leaf = len(rec.child_ids) == 0

    def name_get(self):
        def get_names(cat):
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.parent_id
            return res

        return [(cat.id, " / ".join(reversed(get_names(cat)))) for cat in self]


class AssetTag(models.Model):
    _name = "school.asset.tag"
    _description = "Asset Tags"
    name = fields.Char(string="Asset Tag", index=True, required=True)
    color = fields.Integer("Color Index")

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Tag name already exists !"),
    ]


class AssetType(models.Model):
    """Asset Type"""

    _name = "school.asset_type"
    _description = "Asset Type"
    _inherit = ["image.mixin"]

    name = fields.Char("Name", required=True, translate=True)
    require_validation = fields.Boolean(string="Require validation")

    has_responsible = fields.Boolean(string="Has a responsible")
    is_room = fields.Boolean(string="Is a room")
    linked_to_room = fields.Boolean(string="Is linked to a room")

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Type name already exists !"),
    ]


class Building(models.Model):
    """Asset Type"""

    _name = "school.building"
    _description = "Building"
    _inherit = ["image.mixin"]

    name = fields.Char("Name", required=True, translate=True)
    location = fields.Char("Location", translate=True)

    monday = fields.Boolean(string="Monday", default=True)
    monday_from = fields.Float(string="Monday From", default=8.0)
    monday_to = fields.Float(string="Monday From", default=17.0)

    tuesday = fields.Boolean(string="Tuesday", default=True)
    tuesday_from = fields.Float(string="Tuesday From", default=8.0)
    tuesday_to = fields.Float(string="Tuesday From", default=17.0)

    wednesday = fields.Boolean(string="Wednesday", default=True)
    wednesday_from = fields.Float(string="Wednesday From", default=8.0)
    wednesday_to = fields.Float(string="Wednesday From", default=17.0)

    thursday = fields.Boolean(string="Thursday", default=True)
    thursday_from = fields.Float(string="Thursday From", default=8.0)
    thursday_to = fields.Float(string="Thursday From", default=17.0)

    friday = fields.Boolean(string="Friday", default=True)
    friday_from = fields.Float(string="Friday From", default=8.0)
    friday_to = fields.Float(string="Friday From", default=17.0)

    saturday = fields.Boolean(string="Saturday", default=False)
    saturday_from = fields.Float(string="Saturday From", default=0.0)
    saturday_to = fields.Float(string="Saturday From", default=0.0)

    sunday = fields.Boolean(string="Sunday", default=False)
    sunday_from = fields.Float(string="Sunday From", default=0.0)
    sunday_to = fields.Float(string="Sunday From", default=0.0)
