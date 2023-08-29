import logging

from odoo.addons.http_routing.models.ir_http import slug

_logger = logging.getLogger(__name__)

from odoo import api, models


class Program(models.Model):
    _inherit = ["school.program", "website.searchable.mixin"]
    _name = "school.program"

    @api.model
    def _search_get_detail(self, website, order, options):

        domain = []
        domain.append([("state", "=", "published")])

        return {
            "model": "school.program",
            "base_domain": domain,
            "search_fields": ["name", "domain_name", "specialization"],
            "fetch_fields": ["name", "id"],
            "mapping": {
                "name": {"name": "name", "type": "text", "match": True},
                "website_url": {"name": "url", "type": "text", "truncate": False},
            },
            "icon": "fa-folder-o",
            "order": "name asc, id desc",
        }

    def _search_render_results(self, fetch_fields, mapping, icon, limit):
        results_data = super()._search_render_results(
            fetch_fields, mapping, icon, limit
        )
        for data in results_data:
            data["url"] = "/programme/%s" % slug(self.browse(data["id"]))
        return results_data
