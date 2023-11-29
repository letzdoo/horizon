# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2023 ito-invest.lu
#                       Jerome Sonnet <jerome.sonnet@ito-invest.lu>
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
import collections

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, AccessError

_logger = logging.getLogger(__name__)

from odoo.exceptions import ValidationError

class IndividualProgram(models.Model):
    '''Individual Program'''
    _name='school.individual_program'
    _description='Individual Program'
    _inherit = ['mail.thread','school.uid.mixin','school.open.form.mixin']
    
    _order = 'name'

    active = fields.Boolean(string='Active', help="The active field allows you to hide the course group without removing it.", default=True, copy=False)

    state = fields.Selection([
            ('draft','Draft'),
            ('progress','In Progress'),
            ('awarded', 'Awarded'),
            ('abandonned', 'Abandonned'),
            ('irregular', 'Irregular'),
        ], string='Status', index=True, default='draft',copy=False,
        help=" * The 'Draft' status is used when results are not confirmed yet.\n"
             " * The 'In Progress' status is used during the cycle.\n"
             " * The 'Awarded' status is used when the cycle is awarded.\n"
             " * The 'Abandonned' status is used if a student leave the program.\n"
             " * The 'Irregular' status is used if a student is in an irreular administrative state.\n"
             ,track_visibility='onchange')
    
    abandonned_date = fields.Date('Abandonned Date')
    
    def set_to_draft(self):
        # TODO use a workflow to make sure only valid changes are used.
        return self.write({'state': 'draft'})
    
    
    def set_to_progress(self):
        # TODO use a workflow to make sure only valid changes are used.
        return self.write({'state': 'progress'})
    
    
    def set_to_awarded(self, grade_year_id=None, grade=None, grade_comments=None):
        # TODO use a workflow to make sure only valid changes are used.
        if(grade):
            self.write({'state': 'awarded',
                           'grade' : grade,
                           'grade_year_id' : grade_year_id or self.env.user.current_year_id,
                           'grade_comments' : grade_comments,
                           'graduation_date' : fields.Date.today(),
            })
        else:
            self.write({'state': 'awarded',
                        'grade_year_id' : grade_year_id or self.env.user.current_year_id,
                        'graduation_date' : fields.Date.today(),
            })
            
    def set_to_irregular(self):
        # TODO use a workflow to make sure only valid changes are used.
        return self.write({'state': 'irregular'})

    name = fields.Char(compute='_compute_name',string='Name', readonly=True, store=True)
    
    year_id = fields.Many2one('school.year', string='Registration Year', default=lambda self: self.env.user.current_year_id, readonly=True, states={'draft': [('readonly', False)]})
    
    student_id = fields.Many2one('res.partner', string='Student', domain="[('student', '=', '1')]", required=True)
    student_name = fields.Char(related='student_id.name', string="Student Name", readonly=True, store=True)
    
    image_1920 = fields.Binary('Image', attachment=True, related='student_id.image_1920')
    image_512= fields.Binary('Image', attachment=True, related='student_id.image_512')
    image_128= fields.Binary('Image', attachment=True, related='student_id.image_128')
    
    source_program_id = fields.Many2one('school.program', string="Source Program", ondelete="restrict", readonly=True, states={'draft': [('readonly', False)]}, domain="[('year_id', '=', year_id)]")
    
    cycle_id = fields.Many2one('school.cycle', related='source_program_id.cycle_id', string='Cycle', store=True, readonly=True)
    
    speciality_id = fields.Many2one('school.speciality', related='source_program_id.speciality_id', string='Speciality', store=True, readonly=True)
    domain_id = fields.Many2one(related='speciality_id.domain_id', string='Domain',store=True)
    section_id = fields.Many2one(related='speciality_id.section_id', string='Section',store=True)
    track_id = fields.Many2one(related='speciality_id.track_id', string='Track',store=True)
    
    required_credits = fields.Integer(related='cycle_id.required_credits',string='Requiered Credits')

    course_group_summaries = fields.One2many('school.individual_course_summary', 'program_id', string='Courses Group Summaries', readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    
    @api.onchange('source_program_id')
    def _on_change_source_program_id(self):
        self.ensure_one()
        summaries = self.env['school.individual_course_summary']
        self.env['school.individual_course_summary'].search([('program_id','=',self.id)]).unlink()
        for cg in self.source_program_id.course_group_ids:
            course_group_summary = self.env['school.individual_course_summary'].create({
                'program_id' : self.id,
                'course_group_id' : cg.id,
            })
            
    ind_course_group_ids = fields.One2many('school.individual_course_group', string='Ind Courses Groups', compute='_compute_ind_course_group_ids')
    
    def _compute_ind_course_group_ids(self):
        for rec in self:
            rec.ind_course_group_ids = self.env['school.individual_course_group'].search([('bloc_id','in',rec.bloc_ids.ids)])
    
    @api.depends('cycle_id.name','speciality_id.name','student_id.name')
    def _compute_name(self):
        for rec in self:
            rec.name = "%s - %s - %s" % (rec.student_id.name,rec.cycle_id.name,rec.speciality_id.name)
        
    bloc_ids = fields.One2many('school.individual_bloc', 'program_id', string='Individual Blocs')
    
    def get_all_tearchers(self):
        return self.bloc_ids.course_group_ids.course_ids.teacher_id
        
    def get_all_responsibles(self):
        return self.bloc_ids.course_group_ids.source_course_group_responsible_id

class IndividualCourseSummary(models.Model):
    '''IndividualCourse Summary'''
    _name='school.individual_course_summary'
    _inherit = ['school.open.form.mixin']
    
    program_id = fields.Many2one('school.individual_program', string='Individual Program')
    
    image_1920 = fields.Binary('Image', attachment=True, related='program_id.student_id.image_1920')
    image_512= fields.Binary('Image', attachment=True, related='program_id.student_id.image_512')
    image_128 = fields.Binary('Image', attachment=True, related='program_id.student_id.image_128')
    
    course_group_id = fields.Many2one('school.course_group', string='Course Group')
    
    uid = fields.Char(string="UID",related="course_group_id.uid")
    name = fields.Char(string="Name",related="course_group_id.name")
    responsible_id = fields.Many2one('res.partner', string="Name",related="course_group_id.responsible_id")
    total_hours = fields.Integer(string="Credits",related="course_group_id.total_hours")
    total_credits = fields.Integer(string="Hours",related="course_group_id.total_credits")
    sequence = fields.Integer(string="Sequence",related="course_group_id.sequence")
    level = fields.Integer(string="Level",related="course_group_id.level")
    
    ind_course_group_ids = fields.One2many('school.individual_course_group', string='Courses Groups', compute="_compute_ind_course_group_ids")
    
    def _compute_ind_course_group_ids(self):
        for rec in self:
            rec.ind_course_group_ids = self.env['school.individual_course_group'].search([('bloc_id','in',self.program_id.bloc_ids.ids),('source_course_group_id','=',rec.course_group_id.id)])
    
class IndividualBloc(models.Model):
    '''Individual Bloc'''
    _name='school.individual_bloc'
    _description='Individual Bloc'
    _inherit = ['mail.thread','school.year_sequence.mixin','school.uid.mixin','school.open.form.mixin']
    
    _order = 'year_id, name'
    
    active = fields.Boolean(string='Active', help="The active field allows you to hide the course group without removing it.", default=True, copy=False)
    
    name = fields.Char(compute='_compute_name',string='Name', readonly=True, store=True)
    
    state = fields.Selection([
            ('irregular','Irregular'),
            ('draft','Draft'),
            ('progress','In Progress'),
            ('postponed', 'Postponed'),
            ('awarded_first_session', 'Awarded in First Session'),
            ('awarded_second_session', 'Awarded in Second Session'),
            ('failed', 'Failed'),
            ('abandoned','Abandoned'),
        ], string='Status', index=True, default='draft',
        copy=False,
        help=" * The 'Draft' status is used when results are not confirmed yet.\n"
             " * The 'In Progress' status is used during the courses.\n"
             " * The 'Postponed' status is used when a second session is required.\n"
             " * The 'Awarded' status is used when the bloc is awarded in either first or second session.\n"
             " * The 'Failed' status is used when the bloc is definitively considered as failed.\n"
             " * The 'Abandoned' status is when the student abandoned his bloc.\n"
             ,tracking=True)
    
    program_id = fields.Many2one('school.individual_program', string='Individual Program', required=True)
    
    year_id = fields.Many2one('school.year', string='Year')
    
    level = fields.Selection(
        [
            ('1A1C','Bac 1'),
            ('>45','Bac 2'),
            ('DC1C','Bac 3'),
            ('1A2C','Master 1'),
            ('DC2C','Master 2'),
            ('AG','Agregation'),
            ('JT','Jeune talent'),
            ('EL','Elève libre'),
        ], string='Level', index=True, default='1A1C',
        tracking=True,
        copy=False,
        help=
        " * Agregation: Agregation.\n"
        " * Master 2:DC2C (Derniers crédits de deuxième cycle).\n"
        " * Master 1:1A2C (Premiers année de deuxième cycle).\n"
        " * Bac 3:DC1C (Derniers crédits de premier cycle).\n"
        " * Bac 2:>45 (Poursuite d'études).\n"
        " * Jeune talent:Jeune talent.\n"
        " * Bac 1:1A1C (Première année de premier cycle).\n"
        " * Elève libre:Elève libre.\n"
    )
    
    is_final_bloc = fields.Boolean(string='Is final bloc',tracking=True)
    
    is_light_bloc = fields.Boolean(string='Is a light bloc',tracking=True)
    
    tag_ids = fields.Many2many('school.individual_bloc.tag', 'school_individual_bloc_tag_rel', 'individual_bloc_id', 'tag_id', string='Tags', copy=False)
    
    student_id = fields.Many2one(related='program_id.student_id', string='Student', domain="[('student', '=', '1')]", readonly=True, store=True)
    student_name = fields.Char(related='student_id.name', string="Student Name", readonly=True, store=True)
    
    source_bloc_id = fields.Many2one('school.bloc', string="Source Bloc", ondelete="restrict")
    source_bloc_name = fields.Char(related='source_bloc_id.name', string="Source Bloc Name", readonly=True, store=True)
    source_bloc_title = fields.Char(related='source_bloc_id.title', string="Source Bloc Title", readonly=True, store=True)
    source_bloc_level = fields.Selection([('0','Free'),('1','Bac 1'),('2','Bac 2'),('3','Bac 3'),('4','Master 1'),('5','Master 2'),('6','Agregation'),],related='source_bloc_id.level', string="Source Bloc Level", readonly=True, store=True)
    
    source_bloc_domain_id = fields.Many2one('school.domain',compute='compute_speciality', string='Domain', readonly=True, store=True)
    source_bloc_speciality_id = fields.Many2one('school.speciality',compute='compute_speciality', string='Speciality', readonly=True, store=True)
    source_bloc_section_id = fields.Many2one('school.section',compute='compute_speciality', string='Section', readonly=True, store=True)
    source_bloc_track_id = fields.Many2one('school.track',compute='compute_speciality', string='Track', readonly=True, store=True)
    source_bloc_cycle_id = fields.Many2one('school.cycle',compute='compute_speciality', string='Cycle', readonly=True, store=True)
    
    @api.onchange('source_bloc_id')
    def onchange_source_bloc_id(self):
        self.ensure_one()
        self.course_group_ids.unlink()
        for group in self.source_bloc_id.course_group_ids:
            _logger.debug('Assign course groups : ' + group.uid + ' - ' +group.name)
            cg = self.course_group_ids.create({'bloc_id': self.id,'source_course_group_id': group.id, 'acquiered' : 'NA'})
            courses = []
            for course in group.course_ids:
                _logger.debug('Assign course : ' + course.name)
                courses.append((0,0,{'source_course_id': course.id}))
            cg.write({'course_ids': courses})
    
    @api.depends('source_bloc_id.speciality_id','program_id.speciality_id')
    def compute_speciality(self):
        for bloc in self:
            if bloc.source_bloc_id.speciality_id :
                bloc.source_bloc_speciality_id = bloc.source_bloc_id.speciality_id
                bloc.source_bloc_domain_id = bloc.source_bloc_id.speciality_id.domain_id
                bloc.source_bloc_section_id = bloc.source_bloc_id.speciality_id.section_id
                bloc.source_bloc_track_id = bloc.source_bloc_id.speciality_id.track_id
            elif bloc.program_id.speciality_id :
                bloc.source_bloc_speciality_id = bloc.program_id.speciality_id
                bloc.source_bloc_domain_id = bloc.program_id.speciality_id.domain_id
                bloc.source_bloc_section_id = bloc.program_id.speciality_id.section_id
                bloc.source_bloc_track_id = bloc.program_id.speciality_id.track_id
    
    image_1920 = fields.Binary('Image', attachment=True, related='student_id.image_1920')
    image_512= fields.Binary('Image', attachment=True, related='student_id.image_512')
    image_128 = fields.Binary('Image', attachment=True, related='student_id.image_128')
    
    course_group_ids = fields.One2many('school.individual_course_group', 'bloc_id', string='Courses Groups', tracking=True)
    
    total_credits = fields.Integer(compute='_get_courses_total', string='Credits', store=True)
    total_hours = fields.Integer(compute='_get_courses_total', string='Hours', store=True)
    total_weight = fields.Float(compute='_get_courses_total', string='Weight', store=True)

    @api.depends('course_group_ids.total_hours','course_group_ids.total_credits','course_group_ids.total_weight','course_group_ids.is_ghost_cg')
    def _get_courses_total(self):
        for rec in self:
            _logger.debug('Trigger "_get_courses_total" on Course Group %s' % rec.name)
            rec.total_hours = sum(course_group.total_hours for course_group in rec.course_group_ids if not course_group.is_ghost_cg)
            rec.total_credits = sum(course_group.total_credits for course_group in rec.course_group_ids if not course_group.is_ghost_cg)
            rec.total_weight = sum(course_group.total_weight for course_group in rec.course_group_ids if not course_group.is_ghost_cg)

    @api.depends('year_id.name','student_id.name')
    def _compute_name(self):
        for rec in self:
            rec.name = "%s - %s" % (rec.year_id.name,rec.student_id.name)
    
    _sql_constraints = [
	        ('uniq_student_bloc', 'unique(year_id, student_id, source_bloc_id)', 'This individual bloc already exists.'),
    ]
    
    
    def message_get_suggested_recipients(self):
        recipients = super(IndividualBloc, self).message_get_suggested_recipients()
        try:
            for bloc in self:
                if bloc.student_id:
                    bloc._message_add_suggested_recipient(recipients, partner=bloc.student_id, reason=_('Student'))
        except AccessError:  # no read access rights -> just ignore suggested recipients because this imply modifying followers
            pass
        return recipients
          
    course_count = fields.Integer(compute='_compute_course_count', string="Course")

    def _compute_course_count(self):
        for bloc in self:
            bloc.course_count = self.env['school.individual_course'].search_count([('bloc_id', '=', bloc.id)])

    
    def open_courses(self):
        """ Utility method used to add an "Open Courses" button in bloc views """
        self.ensure_one()
        return {
            'name': _('Courses'),
            'domain': [('bloc_id', '=', self.id)],
            'res_model': 'school.individual_course',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
        }

    def get_all_tearchers(self):
        return self.course_group_ids.course_ids.teacher_id
        
    def get_all_responsibles(self):
        return self.course_group_ids.source_course_group_responsible_id

    ##############################################################################
    #
    # Constraints
    #
    
    @api.constrains('course_group_ids')
    def _check_individual_block(self):
        for rec in self:
            scg_ids = list(map(lambda cg : cg.source_course_group_id.uid,rec.program_id.all_ind_course_group_ids.filtered(lambda ic: ic.state != '7_failed')))
            duplicates = [item for item, count in collections.Counter(scg_ids).items() if count > 1]
            if len(duplicates) > 0 :
                all_cgs = rec.program_id.all_ind_course_group_ids.filtered(lambda ic: ic.state != '7_failed')
                duplicate_cgs = all_cgs.filtered(lambda ic: ic.source_course_group_id.uid in duplicates)    
                raise ValidationError("Cannot have duplicated UE in a program : %s.\n\n Please check following UEI : %s" % (duplicates,duplicate_cgs.mapped('uid')))

    ##############################################################################
    #
    # UX/UI Helpers
    #

    def _domain_source_course_group_id(self):
        return []
    
    new_source_course_group_id = fields.Many2one('school.course_group', string="New Source Course Group", domain=lambda self: self._domain_source_course_group_id())
    
    @api.onchange('new_source_course_group_id')
    def _on_change_new_source_course_group_id(self):
        for rec in self:
            _logger.info('Assign course group : ' + rec.new_source_course_group_id.uid + ' - ' +rec.new_source_course_group_id.name)
            courses = []
            for course in rec.new_source_course_group_id.course_ids:
                _logger.info('Assign course : ' + course.name)
                courses.append((0,0,{'source_course_id': course.id}))
            cg = self.env['school.individual_course_group'].create({'bloc_id': self.id,'source_course_group_id': rec.new_source_course_group_id.id, 'acquiered' : 'NA', 'course_ids' : courses})
            rec.course_group_ids |= cg
            rec.new_source_course_group_id = False


class IndividualBlocTag(models.Model):
    _name = 'school.individual_bloc.tag'
    _description = 'Individual Bloc Tags'
    name = fields.Char(string='Asset Tag', index=True, required=True)
    color = fields.Integer('Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]

class IndividualCourseGroup(models.Model):
    '''Individual Course Group'''
    _name='school.individual_course_group'
    _description='Individual Course Group'
    _inherit = ['mail.thread','school.year_sequence.mixin','school.uid.mixin','school.open.form.mixin']
    
    _order = 'year_id, sequence'
    
    name = fields.Char(related="source_course_group_id.name", readonly=True) #, store=True)
    title = fields.Char(related="source_course_group_id.title", readonly=True, store=True)
    
    sequence = fields.Integer(related="source_course_group_id.sequence", readonly=True, store=True)
    
    state = fields.Selection([
            ('10_irregular','Irregular'),
            ('9_draft','Draft'),
            ('7_failed', 'Failed'),
            ('6_success', 'Success'),
            ('5_progress','In Progress'),
            ('3_rejected','Rejected'),
            ('2_candidate','Candidate'),
            ('1_confirmed','Confirmed'),
            ('1_1_checked','Checked'),
            ('0_valuated', 'Valuated'),
        ], string='Status', index=True, default='9_draft',
        tracking=True,
        copy=False,
        help=" * The 'Draft' status is used when course group is only plan.\n"
             " * The 'Irregular' status is used when course group is in an irregular program.\n"
             " * The 'In Progress' status is used when results are not confirmed yet.\n"
             " * The 'Confirmed' status is when restults are confirmed.\n"
             " * The 'Success' status is when delibration has confirmed success.\n"
             " * The 'Failed' status is when delibration has confirmed failure.\n"
             " * The 'Rejected' status is used when the course group is rejected for valuation.\n"
             " * The 'Candidate' status is used when the course group is candidate for valuation.\n"
             " * The 'Confirmed' status is used when the course group is confirmed for valuation.\n"
             " * The 'Valuated' status is used when the course group is confirmed for valuation.")
    
    year_id = fields.Many2one(related="bloc_id.year_id", string='Year', store=True)
    student_id = fields.Many2one('res.partner', string='Student', store=True, compute='_compute_student_id')
    
    @api.depends('bloc_id.student_id')
    def _compute_student_id(self):
        for rec in self:
            rec.student_id = rec.bloc_id.student_id
    
    responsible_id = fields.Many2one('res.partner', related="source_course_group_id.responsible_id")
    
    image_1920 = fields.Binary('Image', attachment=True, related='student_id.image_1920')
    image_512 = fields.Binary('Image', attachment=True, related='student_id.image_512')
    image_128 = fields.Binary('Image', attachment=True, related='student_id.image_128')
    
    def _domain_source_course_group_id(self):
        return []
    
    source_course_group_id = fields.Many2one('school.course_group', string="Source Course Group", ondelete="restrict", domain=lambda self: self._domain_source_course_group_id())
    source_course_group_uid = fields.Char(related='source_course_group_id.uid', string="Source Course Group UID", store=True)
    source_course_group_responsible_id = fields.Many2one('res.partner', related='source_course_group_id.responsible_id', string="Source Course Group Responsible")
    
    bloc_id = fields.Many2one('school.individual_bloc', string="Bloc", ondelete='cascade', readonly=True)
    program_id = fields.Many2one(string="Program", related='bloc_id.program_id', readonly=True, store=True)

    source_bloc_id = fields.Many2one('school.bloc', string="Source Bloc", related='bloc_id.source_bloc_id', readonly=True, store=True)
    source_bloc_name = fields.Char(related='bloc_id.source_bloc_name', string="Source Course Bloc Name", readonly=True, store=True)
    source_bloc_level = fields.Selection([('0','Free'),('1','Bac 1'),('2','Bac 2'),('3','Bac 3'),('4','Master 1'),('5','Master 2'),],related='bloc_id.source_bloc_level', string="Source Course Bloc Level", readonly=True, store=True)
    
    source_bloc_domain_id = fields.Many2one(related='bloc_id.source_bloc_domain_id', string='Domain', readonly=True, store=True)
    source_bloc_speciality_id = fields.Many2one(related='bloc_id.source_bloc_speciality_id', string='Speciality', readonly=True, store=True)
    source_bloc_section_id = fields.Many2one(related='bloc_id.source_bloc_section_id', string='Section', readonly=True, store=True)
    source_bloc_track_id = fields.Many2one(related='bloc_id.source_bloc_track_id', string='Track', readonly=True, store=True)
    source_bloc_cycle_id = fields.Many2one(related='bloc_id.source_bloc_cycle_id', string='Cycle', readonly=True, store=True)

    course_ids = fields.One2many('school.individual_course', 'course_group_id', string='Courses',tracking=True)
    
    is_ghost_cg = fields.Boolean(string='Is Ghost Course Group', default=False)
    
    total_credits = fields.Integer(compute='_get_courses_total', string='Total Credits', store=True)
    total_hours = fields.Integer(compute='_get_courses_total', string='Total Hours', store=True)
    total_weight = fields.Float(compute='_get_courses_total', string='Total Weight', store=True)
    
    @api.onchange('source_course_group_id')
    def onchange_source_cg(self):
        courses = []
        for course in self.source_course_group_id.course_ids:
            courses.append((0,0,{'source_course_id':course.id}))
        self.update({'course_ids': courses})

    @api.depends('course_ids.hours','course_ids.credits','course_ids.weight')
    def _get_courses_total(self):
        for rec in self:
            _logger.debug('Trigger "_get_courses_total" on Course Group %s' % rec.name)
            rec.total_hours = sum(course.hours for course in rec.course_ids)
            rec.total_credits = sum(course.credits for course in rec.course_ids)
            rec.total_weight = sum(course.weight for course in rec.course_ids)
            
    def get_all_tearchers(self):
        return self.course_ids.teacher_id
            
    def action_open_source_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Course Group',
            'res_model': 'school.course_group',
            'res_id': self.source_course_group_id.id,
            'view_mode': 'form',
        }

class IndividualCourse(models.Model):
    '''Individual Course'''
    _name = 'school.individual_course'
    _description = 'Individual Course'
    _inherit = ['mail.thread','school.year_sequence.mixin','school.uid.mixin','mail.activity.mixin','school.open.form.mixin']
    
    _order = 'sequence'
    
    name = fields.Char(related="source_course_id.name", readonly=True, store=True)
    title = fields.Char(related="source_course_id.title", readonly=True, store=True)
    level = fields.Integer(related="source_course_id.level", readonly=True)
    
    sequence = fields.Integer(related="source_course_id.sequence", readonly=True, store=True)
    
    year_id = fields.Many2one('school.year', related="course_group_id.bloc_id.year_id",store=True)
    student_id = fields.Many2one('res.partner', related="course_group_id.bloc_id.student_id",store=True)
    
    teacher_id = fields.Many2one('res.partner', string='Teacher', compute='compute_teacher_id', store=True)
    teacher_choice_id = fields.Many2one('res.partner', string='Teacher Choice', domain=[('teacher', '=',1)])
    
    @api.depends('teacher_choice_id','source_course_id.teacher_ids')
    def compute_teacher_id(self):
        for rec in self:
            if rec.teacher_choice_id:
                rec.teacher_id = rec.teacher_choice_id
            elif len(rec.source_course_id.teacher_ids) == 1:
                rec.teacher_id = rec.source_course_id.teacher_ids[0]
            else:
                rec.teacher_id = None

    def guess_teacher_id(self):
        for rec in self:
            old_course = self.env['school.individual_course'].search([('student_id','=',rec.student_id.id),('year_id','=',rec.year_id.previous.id),('title', '=', rec.source_course_id.title)])
            if len(old_course) == 1 and old_course.teacher_id:
                rec.teacher_id = old_course.teacher_id

    image_1920 = fields.Binary('Image', attachment=True, related='student_id.image_1920')
    image_512 = fields.Binary('Image', attachment=True, related='student_id.image_512')
    image_128 = fields.Binary('Image', attachment=True, related='student_id.image_128')

    url_ref = fields.Char(related="source_course_id.url_ref", readonly=True)

    credits = fields.Integer(related="source_course_id.credits", readonly=True)
    hours = fields.Integer(related="source_course_id.hours", readonly=True)
    weight =  fields.Float(related="source_course_id.weight", readonly=True, default=1.00)
    
    source_course_id = fields.Many2one('school.course', string="Source Course", auto_join=True, ondelete="restrict")
    
    source_bloc_id = fields.Many2one('school.bloc', string="Source Bloc", related='course_group_id.bloc_id.source_bloc_id', readonly=True, store=True)
    source_bloc_name = fields.Char(related='course_group_id.bloc_id.source_bloc_name', string="Source Course Bloc Name", readonly=True, store=True)
    source_bloc_level = fields.Selection([('0','Free'),('1','Bac 1'),('2','Bac 2'),('3','Bac 3'),('4','Master 1'),('5','Master 2'),],related='course_group_id.bloc_id.source_bloc_level', string="Source Course Bloc Level", readonly=True, store=True)
    
    source_bloc_domain_id = fields.Many2one(related='course_group_id.bloc_id.source_bloc_domain_id', string='Domain', readonly=True, store=True)
    source_bloc_speciality_id = fields.Many2one(related='course_group_id.bloc_id.source_bloc_speciality_id', string='Speciality', readonly=True, store=True)
    source_bloc_section_id = fields.Many2one(related='course_group_id.bloc_id.source_bloc_section_id', string='Section', readonly=True, store=True)
    source_bloc_track_id = fields.Many2one(related='course_group_id.bloc_id.source_bloc_track_id', string='Track', readonly=True, store=True)
    source_bloc_cycle_id = fields.Many2one(related='course_group_id.bloc_id.source_bloc_cycle_id', string='Cycle', readonly=True, store=True)
    
    course_group_id = fields.Many2one('school.individual_course_group', string='Course Groups', ondelete='cascade', readonly=True)
    bloc_id = fields.Many2one('school.individual_bloc', string='Bloc', related='course_group_id.bloc_id', readonly=True, store=True)
    
    
    def open_program(self):
        """ Utility method used to add an "Open Bloc" button in course views """
        self.ensure_one()
        return {'type': 'ir.actions.act_window',
                'res_model': 'school.individual_bloc',
                'view_mode': 'form',
                'res_id': self.bloc_id.id,
                'target': 'current',
                'flags': {'form': {'action_buttons': True}}}
    
class IndividualCourseProxy(models.Model):
    _name = 'school.individual_course_proxy'
    _auto = False
    _inherit = ['school.year_sequence.mixin']

    name = fields.Char(string="Name", readonly=True)
    title = fields.Char(string="Title", readonly=True)
    
    year_id = fields.Many2one('school.year', string='Year', readonly=True)
    teacher_id = fields.Many2one('res.partner', string='Teacher', readonly=True)
    source_course_id = fields.Many2one('school.course', string="Source Course", readonly=True)
    
    student_count = fields.Integer(string="Student Count", readonly=True)

    def init(self):
        """ School Individual Course Proxy """
        cr = self._cr
        tools.drop_view_if_exists(cr, 'school_individual_course_proxy')
        cr.execute(""" CREATE VIEW school_individual_course_proxy AS (
            SELECT
                CAST(CAST(school_individual_course.year_id AS text)||
                CAST(school_individual_course.teacher_id AS text)||
                CAST(school_individual_course.source_course_id AS text) AS BIGINT) as id,
                school_individual_course.name,
                school_individual_course.title,
                school_individual_course.year_id,
                school_individual_course.teacher_id,
                school_individual_course.source_course_id,
                COUNT(CAST(CAST(school_individual_course.year_id AS text)||
                CAST(school_individual_course.teacher_id AS text)||
                CAST(school_individual_course.source_course_id AS text) AS BIGINT)) as student_count
            FROM
                school_individual_course
            WHERE
                school_individual_course.teacher_id IS NOT NULL
            GROUP BY CAST(CAST(school_individual_course.year_id AS text)||
                CAST(school_individual_course.teacher_id AS text)||
                CAST(school_individual_course.source_course_id AS text) AS BIGINT),
                school_individual_course.name,
                school_individual_course.title,
                school_individual_course.year_id,
                school_individual_course.teacher_id,
                school_individual_course.source_course_id
        )""")
        
        
    
    def edit_course(self):
        self.ensure_one()
        value = {
            'domain': "[]",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'school.individual_course',
            'view_id': False,
            'context': dict(self._context or {}),
            'type': 'ir.actions.act_window',
            'search_view_id': False
        }
        return value