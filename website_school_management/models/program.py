import re

from werkzeug.urls import url_join

from odoo import api, fields, models
from odoo.http import request

from odoo.addons.http_routing.models.ir_http import slugify_one, url_for


class ProgramWeb(models.Model):
    _inherit = "school.program"

    year_name = fields.Char(
        related="year_id.name", string="Year Full Name", store=False
    )
    domain_slug = fields.Char(
        related="speciality_id.domain_id.slug", string="Domain Slug", store=False
    )
    track_slug = fields.Char(
        related="speciality_id.track_id.slug", string="Track Slug", store=False
    )
    track_name = fields.Char(
        related="speciality_id.track_id.name", string="Track Name", store=False
    )
    speciality_slug = fields.Char(
        related="speciality_id.slug", string="Speciality Slug", store=False
    )
    speciality_name = fields.Char(
        related="speciality_id.name", string="Speciality Name", store=False
    )
    cycle_grade_slug = fields.Char(
        related="cycle_id.slug_grade", string="Cycle Grade Slug", store=False
    )
    cycle_grade = fields.Char(
        related="cycle_id.grade", string="Cycle Grade", store=False
    )
    cycle_sequence = fields.Integer(
        related="cycle_id.sequence", string="Cycle Grade Order", store=True
    )  # store=True : necessary for order by
    cycle_subtype_slug = fields.Char(
        related="cycle_id.slug_subtype", string="Cycle Sub-type Slug", store=False
    )
    cycle_subtype = fields.Char(
        related="cycle_id.subtype", string="Cycle Sub-type", store=True
    )  # store=True : necessary for order by
    specialization = fields.Char(required=False, string="Specialization", size=40)
    specialization_slug = fields.Char(
        string="Specialization", compute="_compute_specialization_slug", store=True
    )  # store=True : necessary for search

    @api.depends("specialization")
    def _compute_specialization_slug(self):
        for prog in self:
            if prog.specialization:
                prog.specialization_slug = slugify_one(prog.specialization)
            else:
                prog.specialization_slug = None

    @api.model
    def data_init(self):
        for prog in self.search(
            [("specialization", "=", None), ("title", "like", "%(%)")]
        ):
            match = re.match(r".*\((.*)\)$", prog.title)
            if match and match.group(1):
                prog.specialization = match.group(1).capitalize()

    def get_website_meta(self):
        company = request.website.company_id.sudo()
        img_field = (
            "social_default_image"
            if request.website.has_social_default_image
            else "logo"
        )
        if len(self) == 1:
            title = self.title
            description = "%s - Programme de cours" % self.name
        else:
            title = "Programmes de cours"
            description = "Programmes de cours - Recherche - %s résultats" % len(self)
        return {
            "opengraph_meta": {
                "og:type": "website",
                "og:title": title,
                "og:description": description,
                "og:site_name": company.name,
                "og:url": url_join(
                    request.httprequest.url_root, url_for(request.httprequest.path)
                ),
                "og:image": request.website.image_url(request.website, img_field),
            },
            "twitter_meta": {
                "twitter:card": "summary_large_image",
                "twitter:title": title,
                "twitter:description": description,
                "twitter:image": request.website.image_url(
                    request.website, img_field, size="300x300"
                ),
            },
            "meta_description": description,
        }


class CycleWeb(models.Model):
    _inherit = "school.cycle"

    sequence = fields.Integer(
        string="Sequence", required=True, store=True
    )

    slug_grade = fields.Char(
        string="Grade Slug", compute="_compute_slug_grade", store=True
    )

    @api.depends("grade")
    def _compute_slug_grade(self):
        for cycle in self:
            cycle.slug_grade = slugify_one(cycle.grade)

    subtype = fields.Char(required=False, string="Sub-type", size=40)
    slug_subtype = fields.Char(
        string="Sub-type Slug", compute="_compute_slug_subtype", store=True
    )

    @api.depends("subtype")
    def _compute_slug_subtype(self):
        for cycle in self:
            if cycle.subtype:
                cycle.slug_subtype = slugify_one(cycle.subtype)
            else:
                cycle.slug_subtype = None

    @api.model
    def data_init(self):

        for cycle in self.search(
            [("subtype", "=", None), ("name", "ilike", "%" + "générique")]
        ):
            cycle.subtype = "Générique"
        for cycle in self.search(
            [("subtype", "=", None), ("name", "ilike", "%" + "approfondie")]
        ):
            cycle.subtype = "À finalité approfondie"
        for cycle in self.search(
            [("subtype", "=", None), ("name", "ilike", "%" + "didactique%")]
        ):
            cycle.subtype = "À finalité didactique"
        for cycle in self.search(
            [("subtype", "=", None), ("name", "ilike", "%" + "spécialisé%")]
        ):
            cycle.subtype = "À finalité spécialisée"

        # Bachelier
        for cycle in self.search([("name", "ilike", "1er cycle - BACHELIER")]):
            cycle.sequence = 10
        for cycle in self.search([("name", "ilike", "%" + "Bachelier professionnalisant%")]):
            cycle.sequence = 11
        for cycle in self.search([("name", "ilike", "%" + 'BACHELIER DIT "DE QUALIFICATION"%')]):
            cycle.sequence = 12
        for cycle in self.search(["|", ("name", "ilike", "%" + "Bachelier de transition%"), ("name", "ilike", "%" + 'BACHELIER DIT "DE TRANSITION"%')]):
            cycle.sequence = 13

        # Master
        for cycle in self.search(["|", ("name", "ilike", "2ème cycle - MASTER"), ("name", "ilike", "MASTER")]):
            cycle.sequence = 20
        for cycle in self.search([("name", "ilike", "%" + "Master générique%")]):
            cycle.sequence = 21
        for cycle in self.search([("name", "ilike", "%" + "Master (60)%")]):
            cycle.sequence = 22
        for cycle in self.search([("name", "ilike", "%" + "Master à finalité approfondie%")]):
            cycle.sequence = 23
        for cycle in self.search(["|", ("name", "ilike", "%" + "Master à finalité didactique%"), ("name", "ilike", "%" + 'MASTER DIT "DIDACTIQUE%"')]):
            cycle.sequence = 24
        for cycle in self.search([("name", "ilike", "%" + "Master à finalité spécialisée%")]):
            cycle.sequence = 25
        for cycle in self.search([("name", "ilike", "%" + "MASTER ART DRAMATIQUE%")]):
            cycle.sequence = 26
        for cycle in self.search([("name", "ilike", "%" + "MASTER BOLOGNE DIDACTIQUE%")]):
            cycle.sequence = 27
        for cycle in self.search([("name", "ilike", "%" + "MASTER BOLOGNE SPECIALISE%")]):
            cycle.sequence = 28
        for cycle in self.search([("name", "ilike", "%" + "MASTER SANS FINALITE%")]):
            cycle.sequence = 29

        # Agrégation
        for cycle in self.search([("name", "ilike", "Agrégation")]):
            cycle.sequence = 30
        for cycle in self.search([("name", "ilike", "%" + "Agrégation de l'enseignement supérieur%")]):
            cycle.sequence = 31

        # Autre
        for cycle in self.search([("name", "ilike", "%" + "Aide à la réussite%")]):
            cycle.sequence = 40
        for cycle in self.search([("name", "ilike", "%" + "ERASMUS%")]):
            cycle.sequence = 41
        for cycle in self.search([("name", "ilike", "Formation")]):
            cycle.sequence = 42
        for cycle in self.search([("name", "ilike", "Jeune Talent")]):
            cycle.sequence = 43
        for cycle in self.search([("name", "ilike", "ÉLÈVE LIBRE")]):
            cycle.sequence = 44


class DomainWeb(models.Model):
    _inherit = "school.domain"

    slug = fields.Char(string="Domain Slug", compute="_compute_slug", store=True)

    @api.depends("name")
    def _compute_slug(self):
        for dom in self:
            dom.slug = slugify_one(dom.name)


class TrackWeb(models.Model):
    _inherit = "school.track"

    slug = fields.Char(string="Track Slug", compute="_compute_slug", store=True)

    @api.depends("name")
    def _compute_slug(self):
        for track in self:
            track.slug = slugify_one(track.name)


class SpecialityWeb(models.Model):
    _inherit = "school.speciality"

    slug = fields.Char(string="Speciality Slug", compute="_compute_slug", store=True)

    @api.depends("name")
    def _compute_slug(self):
        for spec in self:
            spec.slug = slugify_one(spec.name)


class CourseWeb(models.Model):
    _inherit = "school.course"

    def get_website_meta(self):
        company = request.website.company_id.sudo()
        img_field = (
            "social_default_image"
            if request.website.has_social_default_image
            else "logo"
        )
        if len(self) == 1:
            title = self.name
            description = "%s (%s - %s)" % (
                self.name,
                self.cycle_id.name,
                self.course_group_id.name,
            )
        else:
            title = "Cours"
            description = "Cours - Recherche - %s résultats" % len(self)
        return {
            "opengraph_meta": {
                "og:type": "website",
                "og:title": title,
                "og:description": description,
                "og:site_name": company.name,
                "og:url": url_join(
                    request.httprequest.url_root, url_for(request.httprequest.path)
                ),
                "og:image": request.website.image_url(request.website, img_field),
            },
            "twitter_meta": {
                "twitter:card": "summary_large_image",
                "twitter:title": title,
                "twitter:description": description,
                "twitter:image": request.website.image_url(
                    request.website, img_field, size="300x300"
                ),
            },
            "meta_description": description,
        }
