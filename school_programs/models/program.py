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
from openerp.exceptions import UserError, ValidationError
from openerp.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class school_year_sequence_mixin(models.AbstractModel):
    _name = "school.year_sequence.mixin"

    year_sequence = fields.Selection([
        ('current','Current'),
        ('previous','Previous'),
        ('next','Next'),
        ], string="Year Sequence", compute="_compute_year_sequence", search="_search_year_sequence")
        
    def _compute_year_sequence(self):
        for item in self:
            current_year_id = self.env.user.current_year_id
            if current_year_id.id == item.year_id.id:
                item.year_sequence = 'current'
            if current_year_id.previous.id == item.year_id.id:
                item.year_sequence = 'previous'
            if current_year_id.next.id == item.year_id.id:
                item.year_sequence = 'next'
        
    def _search_year_sequence(self, operator, value):
        current_year_id = self.env.user.current_year_id
        year_ids = []
        if 'current' in value:
            year_ids.append(current_year_id.id)
        if 'previous' in value:
            year_ids.append(current_year_id.previous.id)
        if 'next' in value:
            year_ids.append(current_year_id.next.id)
        return [('year_id','in',year_ids)]

class Program(models.Model):
    '''Program'''
    _name = 'school.program'
    _description = 'Program made of several Blocs'
    _inherit = ['mail.thread','school.year_sequence.mixin',"school.unique_identifier.mixin"]
    
    uid = fields.Char(string="UID", default=lambda self : self.env['ir.sequence'].next_by_code(self._name))
    
    @api.depends('bloc_ids')
    def _get_courses_total(self):
        for rec in self :
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
        for prog in self:
            prog.name = "%s - %s" % (prog.year_id.short_name, prog.title)
    
    domain = fields.Selection([
            ('musique','Musique'),
            ('theatre', 'Théatre')
        ], string='Domaine')
    
    year_id = fields.Many2one('school.year', required=True, string="Year")
    
    description = fields.Text(string='Description')
        
    cycle_id = fields.Many2one('school.cycle', string='Cycle', required=True, domain=[('type', '!=', False)])
    
    speciality_id = fields.Many2one('school.speciality', string='Speciality')
    
    total_credits = fields.Integer(compute='_get_courses_total', string='Total Credits')
    total_hours = fields.Integer(compute='_get_courses_total', string='Total Hours')

    notes = fields.Text(string='Notes')
    
    bloc_ids = fields.One2many('school.bloc', 'program_id', string='Blocs', copy=True)
    
    course_group_ids = fields.One2many('school.course_group', string='Courses Groups',compute='_compute_course_group_ids')
    
    def _compute_course_group_ids(self):
        for rec in self :
            rec.course_group_ids = rec.mapped(bloc_ids.course_group_ids)
        
    # bloc1_title = fields.Text(compute='_compute_bloc_course_group_ids')
    # bloc2_title = fields.Text(compute='_compute_bloc_course_group_ids')
    # bloc3_title = fields.Text(compute='_compute_bloc_course_group_ids')
        
    # bloc1_course_group_ids = fields.One2many('school.course_group', string='Courses Groups Bloc 1', compute='_compute_bloc_course_group_ids')
    # bloc2_course_group_ids = fields.One2many('school.course_group', string='Courses Groups Bloc 2', compute='_compute_bloc_course_group_ids')
    # bloc3_course_group_ids = fields.One2many('school.course_group', string='Courses Groups Bloc 3', compute='_compute_bloc_course_group_ids')
    
    # @api.one
    # def _compute_bloc_course_group_ids(self):
    #     if len(self.bloc_ids) > 0 :
    #         self.bloc1_title = self.bloc_ids[0].name
    #         self.bloc1_course_group_ids = self.bloc_ids[0].course_group_ids
    #     if len(self.bloc_ids) > 1 :
    #         self.bloc2_title = self.bloc_ids[1].name
    #         self.bloc2_course_group_ids = self.bloc_ids[1].course_group_ids
    #     if len(self.bloc_ids) > 2 :
    #         self.bloc3_title = self.bloc_ids[2].name
    #         self.bloc3_course_group_ids = self.bloc_ids[2].course_group_ids
        
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
    
    uid = fields.Char(string="UID", default=lambda self : self.env['ir.sequence'].next_by_code(self._name))
    
    @api.depends('course_group_ids')
    def _get_courses_total(self):
        for rec in self :
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
 
    domain = fields.Selection(related='program_id.domain', string='Domain',store=True)   
    speciality_id = fields.Many2one(related='program_id.speciality_id', string='Speciality',store=True)
 
    total_credits = fields.Integer(compute='_get_courses_total', string='Total Credits')
    total_hours = fields.Integer(compute='_get_courses_total', string='Total Hours')
    total_weight = fields.Float(compute='_get_courses_total', string='Total Weight')

    notes = fields.Text(string='Notes')
    
    program_id = fields.Many2one('school.program', string='Program', copy=True)

    name = fields.Char(string='Name', compute='compute_name', store=True)
    
    course_group_ids = fields.Many2many('school.course_group','school_bloc_course_group_rel', id1='bloc_id', id2='group_id',string='Course Groups', copy=True, domain=['|',('active','=',False),('active','=',True)])
    
    @api.depends('sequence','title')
    def compute_name(self):
        for bloc in self:
            bloc.name = "%s - %d" % (bloc.title,bloc.sequence)
            
    uid = fields.Char(string='UID', compute='compute_uid')
            
    def compute_uid(self):
        for bloc in self:
            bloc.uid = "BLOC-%s" % bloc.id

    _sql_constraints = [
	        ('uniq_bloc', 'unique(program_id, sequence)', 'There shall be only one bloc with a given sequence within a program'),
    ]
    
    def action_open_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _(self.name),
            'res_model': 'school.bloc',
            'res_id': self.id,
            'view_mode': 'form',
        }

class CourseGroup(models.Model):
    '''Courses Group'''
    _name = 'school.course_group'
    _description = 'Courses Group'
    _inherit = ['mail.thread']
    _order = 'sequence'

    uid = fields.Char(string="UID", default=lambda self : self.env['ir.sequence'].next_by_code(self._name))

    sequence = fields.Integer(string='Sequence')
    
    active = fields.Boolean(string='Active', help="The active field allows you to hide the course group without removing it.", default=True, copy=False)
    
    title = fields.Char(required=True, string='Title')
  
    level = fields.Integer(string='Level')
    
    period = fields.Selection([('0','Annual'),('1','Q1'),('2','Q2'),('3','Q1 and/or Q2'),('4','Q1 and/or Q2 and/or Q3'),],string='Period')
    
    mandatory = fields.Boolean(string='Mandatory', default=True)
    
    description = fields.Text(string='Description')
    
    responsible_id = fields.Many2one('res.partner',string='Responsible teacher',domain="[('teacher', '=', '1')]", copy=True)
    
    course_ids = fields.One2many('school.course', 'course_group_id', domain=['|',('active','=',False),('active','=',True)], string='Courses', copy=True, ondelete="cascade")

    bloc_ids = fields.Many2many('school.bloc','school_bloc_course_group_rel', id1='group_id', id2='bloc_id', string='Blocs', copy=False)
    
    name = fields.Char(string='Name', compute='compute_ue_name', store=True)
    
    @api.depends('title','level')
    def compute_ue_name(self):
        for course_g in self:
            if course_g.level:
                course_g.name = "%s - %s" % (course_g.title, course_g.level)
            else:
                course_g.name = course_g.title
            
    uid = fields.Char(string='UID', compute='compute_uid')
            
    def compute_uid(self):
        for cg in self:
            cg.uid = "UE-%s" % cg.id
            
    total_credits = fields.Integer(compute='_get_courses_total', string='Total Credits')
    total_hours = fields.Integer(compute='_get_courses_total', string='Total Hours')
    total_weight = fields.Float(compute='_get_courses_total', string='Total Weight')

    weight = fields.Integer(string='Weight')

    @api.depends('course_ids')
    def _get_courses_total(self):
        for rec in self :
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
        self.ensure_one()
        for bloc_id in self.bloc_ids:
            if bloc_id.program_id.state in ('published','archived') and not self.env.user._is_admin() :
                raise UserError('Cannot change credits or hours of courses used in an active or archived program : %s in %s' % (course_id.name, bloc_id.name))
    
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if name :
                args = ['|'] + (args or []) + [('uid', 'ilike', name)]
        return super(CourseGroup, self).name_search(name=name, args=args, operator=operator, limit=limit)
        
        
    def action_open_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _(self.name),
            'res_model': 'school.course_group',
            'res_id': self.id,
            'view_mode': 'form',
        }
    
class Course(models.Model):
    '''Course'''
    _name = 'school.course'
    _description = 'Course'
    _inherit = ['mail.thread']
    _order = 'sequence'

    uid = fields.Char(string="UID", default=lambda self : self.env['ir.sequence'].next_by_code(self._name))

    sequence = fields.Integer(string='Sequence')
    
    active = fields.Boolean(related="course_group_id.active", store=True, readonly=True)
    
    title = fields.Char(required=True, string='Title')
    
    description = fields.Text(string='Description')
    
    url_ref = fields.Char(string='Url Reference')
    
    course_group_id = fields.Many2one('school.course_group', string='Course Group')
    
    level = fields.Integer(related='course_group_id.level',string='Level', readonly=True)
    
    hours = fields.Integer(string = 'Hours')
    credits = fields.Integer(string = 'Credits')
    weight =  fields.Float(string = 'Weight',digits=(6,2))
    
    notes = fields.Text(string='Notes')
    
    name = fields.Char(string='Name', compute='compute_name', store=True)
    
    has_second_session = fields.Boolean(string="Has a second session", default=True)
    
    @api.depends('title','level')
    def compute_name(self):
        for course in self:
            if course.level:
                course.name = "%s - %s" % (course.title, course.level)
            else:
                course.name = course.title
                
    uid = fields.Char(string='UID', compute='compute_uid')
            
    def compute_uid(self):
        for c in self:
            c.uid = "AA-%s" % c.id
    
    teacher_ids = fields.Many2many('res.partner','course_id','teacher_id',string='Teachers',domain="[('teacher', '=', '1')]")
    
    @api.onchange('hours','credits')
    def onchange_check_programs(self):
        for rec in self :
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
    
class Speciality(models.Model):
    '''Speciality'''
    _name = 'school.speciality'
    _order = 'name'
    name = fields.Char(required=True, string='Name', size=40)
    description = fields.Text(string='Description')
    saturn_code = fields.Text(string='Saturn Code')
    
    domain = fields.Selection([
            ('musique','Musique'),
            ('theatre', 'Théatre')
        ], string='Domaine')
             
    section = fields.Selection([
            ('artdram','Art dramatique'),
            ('ecriture','Écritures et théorie musicale'),
            ('instrument','Formation instrumentale'),
            ('vocale','Formation vocale'),
            ('general','Cours généraux')
        ], string='Section')
        
    track = fields.Selection([
            ('artdram','Art Dramatique'),
            ('chant','Chant'),
            ('clavier','Clavier'),
            ('composition','Composition'),
            ('cordes','Cordes'),
            ('direction','Direction'),
            ('formation','Formation musicale'),
            ('percussion','Percussions'),
            ('vents','Vents'),
            ('theatre','Formation théatrale')
        ], string='Option')
    
    _sql_constraints = [
	        ('uniq_speciality', 'unique(domain, name)', 'There shall be only one speciality in a domain'),
    ]

    
class Year(models.Model):
    '''Year'''
    _name = 'school.year'
    _order = 'name'
    name = fields.Char(required=True, string='Name', size=15)
    short_name = fields.Char(required=True, string='Short Name', size=5)
    
    previous = fields.Many2one('school.year', string='Previous Year')
    next = fields.Many2one('school.year', string='Next Year')
    
class Users(models.Model):
    '''Users'''
    _inherit = ['res.users']
    
    def __init__(self, pool, cr):
        """ Override of __init__ to add access rights on notification_email_send
            and alias fields. Access rights are disabled by default, but allowed
            on some specific fields defined in self.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        init_res = super(Users, self).__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        self.SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        self.SELF_WRITEABLE_FIELDS.extend(['current_year_id'])
        # duplicate list to avoid modifying the original reference
        self.SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS)
        self.SELF_READABLE_FIELDS.extend(['current_year_id'])
    
    current_year_id = fields.Many2one('school.year', string="Current Year", required=True, ondelete="restrict", default=1)