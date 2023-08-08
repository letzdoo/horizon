import re

from odoo import api, fields, models
from odoo.addons.http_routing.models.ir_http import slugify_one

from odoo.http import request
from werkzeug.urls import url_join
from odoo.addons.http_routing.models.ir_http import url_for

class ProgramWeb(models.Model):
    _inherit = 'school.program'

    year_name = fields.Char(related='year_id.name', string='Year Full Name',store=False)
    domain_slug = fields.Char(related='speciality_id.domain_id.slug', string='Domain Slug',store=False)
    track_slug = fields.Char(related='speciality_id.track_id.slug', string='Track Slug',store=False)
    track_name = fields.Char(related='speciality_id.track_id.name', string='Track Name',store=False) 
    speciality_slug = fields.Char(related='speciality_id.slug', string='Speciality Slug',store=False)
    speciality_name = fields.Char(related='speciality_id.name', string='Speciality Name',store=False) 
    cycle_grade_slug = fields.Char(related='cycle_id.slug_grade', string='Cycle Grade Slug',store=False)
    cycle_grade = fields.Char(related='cycle_id.grade', string='Cycle Grade',store=False)
    cycle_grade_order = fields.Integer(related='cycle_id.grade_order', string='Cycle Grade Order',store=True) # store=True : necessary for order by
    cycle_subtype_slug = fields.Char(related='cycle_id.slug_subtype', string='Cycle Sub-type Slug',store=False)
    cycle_subtype = fields.Char(related='cycle_id.subtype', string='Cycle Sub-type',store=True) # store=True : necessary for order by
    specialization = fields.Char(required=False, string='Specialization', size=40)
    specialization_slug = fields.Char(string='Specialization', compute='compute_specialization_slug', store=True) # store=True : necessary for search
    @api.depends('specialization')
    def compute_specialization_slug(self):
        for prog in self:
            if (prog.specialization):
                prog.specialization_slug = slugify_one(prog.specialization)
            else:
                prog.specialization_slug = None    
    
    @api.model
    def data_init(self):
        for prog in self.search([('specialization','=',None),('title','like','%(%)')]):
            match = re.match(r".*\((.*)\)$", prog.title)
            if match and match.group(1):
                prog.specialization = match.group(1).capitalize()

    def get_website_meta(self):
        company = request.website.company_id.sudo()
        img_field = 'social_default_image' if request.website.has_social_default_image else 'logo'
        if len(self) == 1:
            title = self.name
        else:
            title = "Programmes de cours"
        return {
            'opengraph_meta': {
                'og:type': 'website',
                'og:title': title,
                'og:site_name': company.name,
                'og:url': url_join(request.httprequest.url_root, url_for(request.httprequest.path)),
                'og:image': request.website.image_url(request.website, img_field),
            },
            'twitter_meta': {
                'twitter:card': 'summary_large_image',
                'twitter:title': title,
                'twitter:image': request.website.image_url(request.website, img_field, size='300x300'),
            },
            'meta_description': title
        }

class CycleWeb(models.Model):
    _inherit = 'school.cycle'

    grade_order = fields.Integer(string='Grade Order', compute='compute_grade_order', store=True)
    @api.depends('short_name')
    def compute_grade_order(self):
        for cycle in self:
            if (cycle.short_name == "B"):
                cycle.grade_order = 1
            elif (cycle.short_name == "M"):
                cycle.grade_order = 2
            elif (cycle.short_name == "AG"):    
                cycle.grade_order = 3

    slug_grade = fields.Char(string='Grade Slug', compute='compute_slug_grade', store=True)
    @api.depends('grade')
    def compute_slug_grade(self):
        for cycle in self:
            cycle.slug_grade = slugify_one(cycle.grade)

    subtype = fields.Char(required=False, string='Sub-type', size=40)
    slug_subtype = fields.Char(string='Sub-type Slug', compute='compute_slug_subtype', store=True)
    @api.depends('subtype')
    def compute_slug_subtype(self):
        for cycle in self:
            if (cycle.subtype):
                cycle.slug_subtype = slugify_one(cycle.subtype)
            else:
                cycle.slug_subtype = None

    @api.model
    def data_init(self):
        
        for cycle in self.search([('subtype','=',None),('name','ilike','%'+'générique')]):
            cycle.subtype = 'Générique'
        for cycle in self.search([('subtype','=',None),('name','ilike','%'+'approfondie')]):
            cycle.subtype = 'À finalité approfondie'
        for cycle in self.search([('subtype','=',None),('name','ilike','%'+'didactique%')]):
            cycle.subtype = 'À finalité didactique'
        for cycle in self.search([('subtype','=',None),('name','ilike','%'+'spécialisé%')]):
            cycle.subtype = 'À finalité spécialisée'  
    
class DomainWeb(models.Model):
    _inherit = 'school.domain'

    slug = fields.Char(string='Domain Slug', compute='compute_slug', store=True)
    @api.depends('name')
    def compute_slug(self):
        for dom in self:
            dom.slug = slugify_one(dom.name)

class TrackWeb(models.Model):
    _inherit = 'school.track'

    slug = fields.Char(string='Track Slug', compute='compute_slug', store=True)
    @api.depends('name')
    def compute_slug(self):
        for track in self:
            track.slug = slugify_one(track.name)

class SpecialityWeb(models.Model):
    _inherit = 'school.speciality'

    slug = fields.Char(string='Speciality Slug', compute='compute_slug', store=True)
    @api.depends('name')
    def compute_slug(self):
        for spec in self:
            spec.slug = slugify_one(spec.name)

class CourseWeb(models.Model):
    _inherit = 'school.course'

    def get_website_meta(self):
        company = request.website.company_id.sudo()
        img_field = 'social_default_image' if request.website.has_social_default_image else 'logo'
        if len(self) == 1:
            title = self.name
        else:
            title = "Cours"
        return {
            'opengraph_meta': {
                'og:type': 'website',
                'og:title': title,
                'og:site_name': company.name,
                'og:url': url_join(request.httprequest.url_root, url_for(request.httprequest.path)),
                'og:image': request.website.image_url(request.website, img_field),
            },
            'twitter_meta': {
                'twitter:card': 'summary_large_image',
                'twitter:title': title,
                'twitter:image': request.website.image_url(request.website, img_field, size='300x300'),
            },
            'meta_description': title
        }