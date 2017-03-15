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
from datetime import timedelta
from datetime import datetime
from datetime import time

from openerp import api, fields, models, _
from openerp.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class WeeklyBooking(models.Model):
    _name = "school.weekly_booking"
    _description = "Weekly Booking"
    _order = 'dayofweek, hour_from'

    type = fields.Selection([
        ('ind' , 'Individual'),
        ('col' , 'Collective'),
    ], 'Type of booking', default='col')

    state = fields.Selection([
            ('draft','Draft'),
            ('confirmed', 'Confirmed'),
            ('refused', 'Refused'),
            ('stopped', 'Stopped'),
        ], string='Status', index=True, readonly=True, default='draft',
        copy=False,
        help=" * The 'Draft' status is used when a new request is made.\n"
             " * The 'Confirmed' status is when a booking is confirmed.\n"
             " * The 'Refused' status is when a booking has been refused.\n"
             " * The 'Stopped' status is when a booking is stopped.")

    @api.multi
    def set_to_draft(self):
        for wb in self:
            if wb.event_id:
                wb.event_id.unlink()
        return self.write({'state': 'draft','event_id': False})
        
    @api.multi
    def set_to_confirmed(self):
        for wb in self:
            start_date = max(fields.Date.from_string( wb.calendar_id.from_date), datetime.now().date())
            next_event_date = start_date + timedelta( (int( wb.dayofweek)-start_date.weekday()) % 7 )
        
            if wb.group_id :
                partner_ids = [ (4,  wb.group_id.responsible_id.id) ]
                partner_ids += [ (4, record.id) for record in  wb.group_id.staff_ids ]
                partner_ids += [ (4, record.id) for record in  wb.group_id.participant_ids ]
            else :
                partner_ids = [ (4, wb.responsible_id.id) ] if wb.responsible_id else []
            
            event = self.env['calendar.event'].with_context(no_email=True).create({
                'name':  wb.name,
                'categ_ids' : [ (4, self.env.ref('school_student_group_booking.school_group_booking_event_type').id) ],
                'partner_ids' : partner_ids,
                'start': fields.Datetime.to_string(datetime.combine(next_event_date, time.min) + timedelta(hours= wb.hour_from)),
                'stop': fields.Datetime.to_string(datetime.combine(next_event_date, time.min) + timedelta(hours= wb.hour_to)),
                'end_type': 'end_date',
                'final_date':  wb.calendar_id.to_date,
                'day': 0.0,
                'mo':  wb.dayofweek == '0',
                'tu':  wb.dayofweek == '1',
                'we':  wb.dayofweek == '2',
                'th':  wb.dayofweek == '3',
                'fr':  wb.dayofweek == '4',
                'sa':  wb.dayofweek == '5',
                'su':  wb.dayofweek == '6',
                'duration': 1.0,
                'recurrency': True,
                'rrule_type': 'weekly',
                'room_id':  wb.room_id.id,
                'asset_ids': [ (4, record.id) for record in  wb.asset_ids ],
                'show_as': 'busy' if (wb.type == 'col') else 'free',
            })
            wb['state'] = 'confirmed'
            wb['event_id'] = event.id
        return self
        
    @api.multi
    def set_to_refused(self):
        # TODO use a workflow to make sure only valid changes are used.
        return self.write({'state': 'refused'})
        
    @api.multi
    def set_to_stop(self):
        for wb in self:
            if wb.event_id:
                wb.event_id.final_date = fields.Datetime.to_string(datetime.now())
        return self.write({'state': 'stopped'})

    name = fields.Char(required=True, readonly=True, states={'draft': [('readonly', False)]})
    year_id = fields.Many2one('school.year', string='Year', default=lambda self: self.env.user.current_year_id, readonly=True, states={'draft': [('readonly', False)]})
    group_id = fields.Many2one('school.student_group', string='Group', readonly=True, states={'draft': [('readonly', False)]})
    responsible_id = fields.Many2one('res.partner', string='Responsible', readonly=True, states={'draft': [('readonly', False)]})
    
    dayofweek = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
        ], 'Day of Week', required=True, index=True, default='0', readonly=True, states={'draft': [('readonly', False)]})
    hour_from = fields.Float(string='Start', required=True, index=True, help="Start and End time of the activity.", readonly=True, states={'draft': [('readonly', False)]})
    hour_to = fields.Float(string='End', required=True, readonly=True, states={'draft': [('readonly', False)]})
    room_id = fields.Many2one('school.asset', string='Room', domain=[('is_room','=',True)], readonly=True, states={'draft': [('readonly', False)]})
    asset_ids = fields.Many2many('school.asset', 'weekly_booking_assets_ref','weekly_booking_id','asset_id', string='Assets', domain=[('is_room','=',False)], readonly=True, states={'draft': [('readonly', False)]})
    
    calendar_id = fields.Many2one("school.calendar", string="School Calendar", required=True, ondelete='restrict', default=lambda self: self.env.user.current_year_id.calendar_id, readonly=True, states={'draft': [('readonly', False)]})
    event_id = fields.Many2one('calendar.event', string="Event", readonly=True)
    
    @api.multi
    def unlink(self):
        for wb in self:
            if wb.event_id:
                wb.event_id.unlink()
        return super(WeeklyBooking,self).unlink()
        
class StudentGroup(models.Model):
    '''Student Group'''
    _inherit = ['school.student_group']
    
    booking_ids = fields.One2many('school.weekly_booking', 'group_id')