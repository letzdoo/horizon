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

import pytz
from datetime import datetime, date, time, timedelta

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

def to_tz(datetime, tz):
    return pytz.UTC.localize(datetime.replace(tzinfo=None), is_dst=False).astimezone(tz).replace(tzinfo=None)

class Event(models.Model):
    """ Model for School Event """
    _inherit = 'calendar.event'
    
    def confirm(self):
        self.write({'state': 'open'})
        
    def to_draft(self):
        self.write({'state': 'draft'})

    @api.constrains('room_id')
    def _check_room_quota(self):
        for rec in self :
            _logger.info('Check constraints _check_room_quota on record %s using COVID rules' % self.id)
           
            if self.recurrency :
                return
            
            # Get user timezone
            
            utc_tz = pytz.UTC
            #user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'Europe/Brussels')
            user_tz = pytz.timezone('Europe/Brussels')
    
            # Prevent concurrent bookings

            domain = [('room_id','=',self.room_id.id), ('start', '<', self.stop_datetime), ('stop', '>', self.start_datetime)]
            conflicts_count = self.env['calendar.event'].sudo().with_context({'virtual_id': True}).search_count(domain)
            if conflicts_count > 1:
                raise ValidationError(_("Concurrent event detected - %s in %s") % (self.start_datetime, self.room_id.name))
    
            # Constraint not for employees and teatchers
    
            if self.env.user.has_group('school_management.group_employee'):
                return
    
            if self.env.user.has_group('school_management.group_teacher'):
                return
    
            # Constraint on student events
            
            student_event = self.env.ref('school_booking.school_student_event_type')
            
            if student_event in self.categ_ids:
                
                dt = to_tz(fields.Datetime.from_string(self.start_datetime),utc_tz)
                
                if dt.minute != 0 and dt.minute != 30 :
                    raise ValidationError(_("Invalid booking, please use standard booking."))
                    
                now = to_tz(datetime.now(),user_tz)
                
                start_time = fields.Datetime.from_string(self.start_datetime)
               
                next_day = now + timedelta(days= 7-now.weekday() if now.weekday()>3 else 1)
                
                #last_booking_day = now - timedelta(days=now.weekday()) + timedelta(days=6) # end of week
                # change suivant email Marie-Catherine Bach Mon, 1 Mar, 13:14
                
                # change suivant call du 05/05/21
                last_booking_day = next_day + timedelta(days=2) # 2 following days

                # removed suivant call du 05/05/21
                #if now.weekday > 3 :
                #    last_booking_day = last_booking_day + timedelta(days=7) # end of next week

                if start_time > last_booking_day :
                    raise ValidationError(_("Bookings are not yet open for this date."))
                
                if dt < (datetime.now() + timedelta(minutes=-30)):
                    raise ValidationError(_("You cannot book in the past."))
                
                event_day = fields.Datetime.from_string(self.start_datetime).date()
                
                duration_list = self.env['calendar.event'].read_group([
                        ('user_id', '=', self.user_id.id), ('room_id','!=',False), ('categ_ids','in',student_event.id), ('start', '>=', fields.Datetime.to_string(event_day)), ('start', '<=', fields.Datetime.to_string(event_day + timedelta(days=1)))
                    ],['room_id','duration'],['room_id'])
                for duration in duration_list:
                    if duration['duration'] and duration['duration'] > 4:
                        raise ValidationError(_("You cannot book the room %s more than three hours") % (duration.get('room_id','')[1]))

                utc_tz = pytz.UTC
                #user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'Europe/Brussels')
                user_tz = pytz.timezone('Europe/Brussels')
        
                # Prevent concurrent bookings
    
                domain = [('room_id','=',rec.room_id.id), ('start', '<', rec.stop), ('stop', '>', rec.start)]
                conflicts_count = self.env['calendar.event'].sudo().with_context({'virtual_id': True}).search_count(domain)
                if conflicts_count > 1:
                    raise ValidationError(_("Concurrent event detected - %s in %s") % (rec.start, rec.room_id.name))
        
                # Constraint not for employees and teatchers
        
                if self.env.user.has_group('school_management.group_employee'):
                    return
        
                if self.env.user.has_group('school_management.group_teacher'):
                    return
        
                _logger.info('Check done')
                

