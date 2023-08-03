import logging
import time
import werkzeug.utils
import json

from datetime import datetime, timedelta
import dateutil
import dateutil.parser
import dateutil.relativedelta

from odoo import api, fields
from odoo import http
from odoo.http import request
from odoo.addons.auth_oauth.controllers.main import OAuthLogin as Home

_logger = logging.getLogger(__name__)

# Gestion des différentes routes pour les programmes de cours
class reservations(http.Controller):
    @http.route('/responsive/booking_new', type='http', auth='user', website=True)
    def responsive_booking_new(self, debug=False, **k):
        values = {
            'user': request.env.user,
            'today' : datetime.today(),
            'tomorrow' : datetime.today() + timedelta(days=1)
        }
        return request.render('website_school_management.hz_booking_new', values)
    
    @http.route('/responsive/booking_search', type='http', auth='user', website=True)
    def responsive_booking_search(self, debug=False, **k):
        values = {
            'user': request.env.user,
            'today' : fields.Datetime.to_string(datetime.today()),
            'tomorrow' : fields.Datetime.to_string(datetime.today() + timedelta(days=1))
        }
        return request.render('website_school_management.hz_booking_search', values)
    
    @http.route('/responsive/bookings', type='http', auth='user', website=True)
    def responsive_bookings(self, debug=False, **k):
        start = fields.Datetime.to_string(datetime.today().replace(hour=0, minute=0, second=0))
        end = fields.Datetime.to_string(datetime.today().replace(hour=23, minute=59, second=59))
        event_fields = ['name','start','stop','allday','room_id','user_id','final_date','recurrency','categ_ids']
        domain = [
            ('start', '<=', end),    
            ('stop', '>=', start),
            ('user_id','=',request.uid),
        ]
        domain_next = [
            ('start', '<=', fields.Datetime.to_string(datetime.today().replace(hour=23, minute=59, second=59) + timedelta(days=1))),
            ('stop', '>=', fields.Datetime.to_string(datetime.today().replace(hour=0, minute=0, second=0) + timedelta(days=1))),
            ('user_id','=',request.uid),
        ]
        values = {
            'user': request.env.user,
            'bookings': request.env['calendar.event'].sudo().with_context({'virtual_id': True, 'tz':request.env.user.tz}).search(domain,order='start asc'),
            'bookings_next': request.env['calendar.event'].sudo().with_context({'virtual_id': True,'tz':request.env.user.tz}).search(domain_next,order='start asc'),
        }
        return request.render('website_school_management.hz_bookings', values)
    
    @http.route('/responsive/delete/<int:booking_id>', type='http', auth='user', website=True)
    def responsive_delete_booking(self, booking_id, debug=False, **k):
        booking = request.env['calendar.event'].browse(booking_id)
        booking.unlink()
        return werkzeug.utils.redirect('/responsive/bookings')