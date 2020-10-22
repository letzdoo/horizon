# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2015 be-cloud.be
#                       Jerome Sonnet <jerome.sonnet@be-cloud.be>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
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

from openerp import api, fields, models, tools, _
from openerp.exceptions import UserError
from openerp.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class Program(models.Model):
    '''Program'''
    _name = 'school.program'
    _description = 'Program made of several Blocs'
    _inherit = ['mail.thread','school.year_sequence.mixin']
    
    @api.depends('bloc_ids')
    def _get_courses_total(self):
        for rec in self:
            total_hours = 0.0
            total_credits = 0.0
            for bloc in rec.bloc_ids:
                total_hours += bloc.total_hours
                total_credits += bloc.total_credits
            rec.total_hours = total_hours
            rec.total_credits = total_credits
    
    state = fields.Selection([
            ('draft','Draft'),
            ('published', 'Published'),
            ('archived', 'Archived'),
        ], string='Status', index=True, readonly=True, default='draft',
        #track_visibility='onchange', TODO : is this useful for this case ?
        copy=False,
        help=" * The 'Draft' status is used when a new program is created and not published yet.\n"
             " * The 'Published' status is when a program is published and available for use.\n"
             " * The 'Archived' status is used when a program is obsolete and not publihed anymore.")
    
    title = fields.Char(required=True, string='Title')
    name = fields.Char(string='Name', compute='compute_name', store=True)
    
    @api.depends('title','year_id')
    def compute_name(self):
        for course_g in self:
            course_g.name = "%s - %s" % (course_g.year_id.short_name, course_g.title)
    
    year_id = fields.Many2one('school.year', required=True, string="Year")
    
    description = fields.Text(string='Description')
        
    competency_ids = fields.Many2many('school.competency','school_competency_program_rel', 'program_id', 'competency_id', string='Competencies', ondelete='restrict')
    
    cycle_id = fields.Many2one('school.cycle', string='Cycle', required=True, domain=[('type', '!=', False)])
    
    speciality_id = fields.Many2one('school.speciality', string='Speciality')
    domain_id = fields.Many2one(related='speciality_id.domain_id', string='Domain',store=True)
    section_id = fields.Many2one(related='speciality_id.section_id', string='Section',store=True)
    track_id = fields.Many2one(related='speciality_id.track_id', string='Track',store=True)
    
    total_credits = fields.Integer(compute='_get_courses_total', string='Total Credits')
    total_hours = fields.Integer(compute='_get_courses_total', string='Total Hours')

    notes = fields.Text(string='Notes')
    
    bloc_ids = fields.One2many('school.bloc', 'program_id', string='Blocs', copy=True)
    
    course_group_ids = fields.One2many('school.course_group', string='Courses Groups',compute='_compute_course_group_ids')
    
    def _compute_course_group_ids(self):
        for rec in self:
            course_group_ids = False
            for bloc in rec.bloc_ids:
                if course_group_ids :
                    course_group_ids |= bloc.course_group_ids
                else :
                    course_group_ids = bloc.course_group_ids
            rec.course_group_ids = course_group_ids
        
    bloc1_title = fields.Text(compute='_compute_bloc_course_group_ids')
    bloc2_title = fields.Text(compute='_compute_bloc_course_group_ids')
    bloc3_title = fields.Text(compute='_compute_bloc_course_group_ids')
        
    bloc1_course_group_ids = fields.One2many('school.course_group', string='Courses Groups Bloc 1', compute='_compute_bloc_course_group_ids')
    bloc2_course_group_ids = fields.One2many('school.course_group', string='Courses Groups Bloc 2', compute='_compute_bloc_course_group_ids')
    bloc3_course_group_ids = fields.One2many('school.course_group', string='Courses Groups Bloc 3', compute='_compute_bloc_course_group_ids')
    
    def _compute_bloc_course_group_ids(self):
        for rec in self:
            if len(rec.bloc_ids) > 0 :
                rec.bloc1_title = rec.bloc_ids[0].name
                rec.bloc1_course_group_ids = rec.bloc_ids[0].course_group_ids
            if len(rec.bloc_ids) > 1 :
                rec.bloc2_title = rec.bloc_ids[1].name
                rec.bloc2_course_group_ids = rec.bloc_ids[1].course_group_ids
            if len(rec.bloc_ids) > 2 :
                rec.bloc3_title = rec.bloc_ids[2].name
                rec.bloc3_course_group_ids = rec.bloc_ids[2].course_group_ids
        
    
    def unpublish(self):
        return self.write({'state': 'draft'})
    
    
    def publish(self):
        return self.write({'state': 'published'})
    
    
    def archive(self):
        return self.write({'state': 'archived'})

class Bloc(models.Model):
    '''Bloc'''
    _name = 'school.bloc'
    _description = 'Program'
    _inherit = ['mail.thread','school.year_sequence.mixin']
    _order = 'program_id,sequence'
    
    @api.depends('course_group_ids')
    def _get_courses_total(self):
        for rec in self:
            total_hours = 0.0
            total_credits = 0.0
            total_weight = 0.0
            for course_group in rec.course_group_ids:
                total_hours += course_group.total_hours
                total_credits += course_group.total_credits
                total_weight += course_group.total_weight
            rec.total_hours = total_hours
            rec.total_credits = total_credits
            rec.total_weight = total_weight

    sequence = fields.Integer(string='Sequence')
    title = fields.Char(required=True, string='Title')
    year_id = fields.Many2one('school.year', string="Year", related='program_id.year_id', store=True)
    description = fields.Text(string='Description')
    
    cycle_id = fields.Many2one(related='program_id.cycle_id', string='Cycle',store=True)
    
    level = fields.Selection([('0','Free'),('1','Bac 1'),('2','Bac 2'),('3','Bac 3'),('4','Master 1'),('5','Master 2'),('6','Agregation'),],string='Level')
    
    speciality_id = fields.Many2one(related='program_id.speciality_id', string='Speciality',store=True)
    domain_id = fields.Many2one(related='program_id.domain_id', string='Domain',store=True)
    section_id = fields.Many2one(related='program_id.section_id', string='Section',store=True)
    track_id = fields.Many2one(related='program_id.track_id', string='Track',store=True)
    
    total_credits = fields.Integer(compute='_get_courses_total', string='Total Credits')
    total_hours = fields.Integer(compute='_get_courses_total', string='Total Hours')
    total_weight = fields.Float(compute='_get_courses_total', string='Total Weight')

    notes = fields.Text(string='Notes')
    
    program_id = fields.Many2one('school.program', string='Program', copy=True)

    name = fields.Char(string='Name', compute='compute_name', store=True)
    
    course_group_ids = fields.Many2many('school.course_group','school_bloc_course_group_rel', 'bloc_id', 'group_id',string='Course Groups', copy=True, domain=['|',('active','=',False),('active','=',True)])
    
    @api.depends('sequence','title')
    
    def compute_name(self):
        for bloc in self:
            bloc.name = "%s - %d" % (bloc.title,bloc.sequence)

    _sql_constraints = [
	        ('uniq_bloc', 'unique(program_id, sequence)', 'There shall be only one bloc with a given sequence within a program'),
    ]

class CourseGroup(models.Model):
    '''Courses Group'''
    _name = 'school.course_group'
    _description = 'Courses Group'
    _inherit = ['mail.thread']
    _order = 'sequence'
    
    sequence = fields.Integer(string='Sequence', required=True)
    
    active = fields.Boolean(string='Active', help="The active field allows you to hide the course group without removing it.", default=True, copy=False)
    
    title = fields.Char(required=True, string='Title')
    
    speciality_id = fields.Many2one('school.speciality', string='Speciality')
    domain_id = fields.Many2one(related='speciality_id.domain_id', string='Domain',store=True)
    section_id = fields.Many2one(related='speciality_id.section_id', string='Section',store=True)
    track_id = fields.Many2one(related='speciality_id.track_id', string='Track',store=True)
    
    cycle_id = fields.Many2one('school.cycle', string='Cycle')
    
    level = fields.Integer(string='Level')
    
    period = fields.Selection([('0','Annual'),('1','Q1'),('2','Q2'),('3','Q1 and/or Q2'),('4','Q1 and/or Q2 and/or Q3'),],string='Period')
    
    mandatory = fields.Boolean(string='Mandatory', default=True)
    
    description = fields.Text(string='Description')
    
    teacher_id = fields.Many2one('res.partner',string='Teacher',domain="[('teacher', '=', '1')]", copy=True)
    
    course_ids = fields.One2many('school.course', 'course_group_id', domain=['|',('active','=',False),('active','=',True)], string='Courses', copy=True, ondelete="cascade")

    bloc_ids = fields.Many2many('school.bloc','school_bloc_course_group_rel', 'group_id', 'bloc_id',string='Blocs', copy=False)
    
    name = fields.Char(string='Name', compute='compute_ue_name', store=True)
    ue_id = fields.Char(string="UE Id", compute='compute_ue_name', store=True)
    
    @api.depends('title','level','speciality_id.name', 'cycle_id.short_name')
    
    def compute_ue_name(self):
        for course_g in self:
            if course_g.level:
                course_g.name = "%s - %s - %s%s" % (course_g.title, course_g.speciality_id.name, course_g.cycle_id.short_name, course_g.level)
            else:
                course_g.name = "%s - %s - %s" % (course_g.title, course_g.speciality_id.name, course_g.cycle_id.short_name)
            course_g.ue_id = "UE-%s" % course_g.id
            
    total_credits = fields.Integer(compute='_get_courses_total', string='Total Credits')
    total_hours = fields.Integer(compute='_get_courses_total', string='Total Hours')
    total_weight = fields.Float(compute='_get_courses_total', string='Total Weight')

    weight = fields.Integer(string='Weight')

    @api.depends('course_ids')
    def _get_courses_total(self):
        for rec in self:
            total_hours = 0.0
            total_credits = 0.0
            total_weight = 0.0
            for course in rec.course_ids:
                total_hours += course.hours
                total_credits += course.credits
                total_weight += course.weight
            rec.total_hours = total_hours
            rec.total_credits = total_credits
            rec.total_weight = total_weight
    
    notes = fields.Text(string='Notes')
    
    def onchange_check_programs(self, course_id):
        for rec in self:
            for bloc_id in rec.bloc_ids:
                if bloc_id.program_id.state in ('published','archived') and not self.env.user._is_admin() :
                    raise UserError('Cannot change credits or hours of courses used in an active or archived program : %s in %s' % (course_id.name, bloc_id.name))
    
    
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if name :
                args = ['|'] + (args or []) + [('ue_id', 'ilike', name)]
        return super(CourseGroup, self).name_search(name=name, args=args, operator=operator, limit=limit)
    
class Course(models.Model):
    '''Course'''
    _name = 'school.course'
    _description = 'Course'
    _inherit = ['mail.thread']
    _order = 'sequence'
    
    sequence = fields.Integer(string='Sequence')
    
    active = fields.Boolean(related="course_group_id.active", store=True, readonly=True)
    
    title = fields.Char(required=True, string='Title')
    
    description = fields.Text(string='Description')
    
    url_ref = fields.Char(string='Url Reference')
    
    course_group_id = fields.Many2one('school.course_group', string='Course Group')
    
    level = fields.Integer(related='course_group_id.level',string='Level', readonly=True)
    
    cycle_id = fields.Many2one(related='course_group_id.cycle_id', string='Cycle',store=True, readonly=True)
    
    speciality_id = fields.Many2one(related='course_group_id.speciality_id', string='Speciality',store=True, readonly=True)
    domain_id = fields.Many2one(related='course_group_id.domain_id', string='Domain',store=True, readonly=True)
    section_id = fields.Many2one(related='course_group_id.section_id', string='Section',store=True, readonly=True)
    track_id = fields.Many2one(related='course_group_id.track_id', string='Track',store=True, readonly=True)
    
    hours = fields.Integer(string = 'Hours')
    credits = fields.Integer(string = 'Credits')
    weight =  fields.Float(string = 'Weight',digits=(6,2))
    
    notes = fields.Text(string='Notes')
    
    name = fields.Char(string='Name', compute='compute_name', store=True)
    
    has_second_session = fields.Boolean(string="Has a second session", default=True)
    
    @api.depends('title','level','speciality_id.name', 'cycle_id.short_name', 'course_group_id.level')
    
    def compute_name(self):
        for course in self:
            if course.level:
                course.name = "%s - %s - %s%s" % (course.title, course.speciality_id.name, course.cycle_id.short_name, course.level)
            else:
                course.name = "%s - %s - %s" % (course.title, course.speciality_id.name, course.cycle_id.short_name)
    
    teacher_ids = fields.Many2many('res.partner','course_id','teacher_id',string='Teachers',domain="[('teacher', '=', '1')]")
    
    @api.onchange('hours','credits')
    def onchange_check_programs(self):
        for rec in self:
            rec.course_group_id.onchange_check_programs(rec)
        

class ReportProgram(models.AbstractModel):
    _name = 'report.school_management.report_program'

    
    def render_html(self, data):
        _logger.info('render_html')
        docargs = {
            'doc_ids': data['id'],
            'doc_model': 'school.program',
            'docs': self.env['school.program'].browse(data['id']),
        }
        return self.env['report'].render('school.report_program', docargs)

class Competency(models.Model):
    '''Competency'''
    _order = 'name'
    _name = 'school.competency'
    _order = 'sequence asc'
    sequence = fields.Integer(string='Sequence')
    description = fields.Text(string='Description')
    
    program_ids = fields.Many2many('school.program','school_competency_program_rel', 'competency_id', 'program_id', string='Programs', ondelete='restrict')
    
class Domain(models.Model):
    '''Domain'''
    _order = 'name'
    _name = 'school.domain'
    name = fields.Char(required=True, string='Name', size=40)
    description = fields.Text(string='Description')
    long_name = fields.Char(required=True, string='Long Name', size=40)
    
class Cycle(models.Model):
    '''Cycle'''
    _order = 'name'
    _name = 'school.cycle'
    
    name = fields.Char(required=True, string='Name', size=60)
    short_name = fields.Char(string='Short Name', size=2)
    description = fields.Text(string='Description')
    required_credits = fields.Integer(string='Required Credits')
    type = fields.Selection([
            ('long','Long'),
            ('short', 'Short'),
        ], string='Type')
    grade = fields.Char(required=True, string='Grade', size=60)
    
class Section(models.Model):
    '''Section'''
    _order = 'name'
    _name = 'school.section'
    name = fields.Char(required=True, string='Name', size=40)
    description = fields.Text(string='Description')
    
class Track(models.Model):
    '''Track'''
    _order = 'name'
    _name = 'school.track'
    name = fields.Char(required=True, string='Name', size=40)
    description = fields.Text(string='Description')
    
class Speciality(models.Model):
    '''Speciality'''
    _name = 'school.speciality'
    _order = 'name'
    name = fields.Char(required=True, string='Name', size=40)
    description = fields.Text(string='Description')
    domain_id = fields.Many2one('school.domain', string='Domain')
    section_id = fields.Many2one('school.section', string='Section')
    track_id = fields.Many2one('school.track', string='Track')
    
    _sql_constraints = [
	        ('uniq_speciality', 'unique(domain_id, name)', 'There shall be only one speciality in a domain'),
    ]