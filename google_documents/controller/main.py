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
import time
import werkzeug.utils
import json

from datetime import datetime, timedelta
import dateutil
import dateutil.parser
import dateutil.relativedelta

from odoo import api, fields, models
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class GoogleServiceController(http.Controller):
    @http.route('/google_documents/authorize', type='http', auth='user')
    def google_drive_service_authorize(self, state, code, scope, redirect=None, *args, **kw):
        _logger.info('Authorize response : %s %s %s' % (state, code, scope))
        drive_service = request.env['google.drive.service'].browse(state)
        drive_service.drive_auth_code = code
        return werkzeug.utils.redirect('/web#view_type=form&model=google.drive.service&id=%s' % state)
        
    @http.route('/google_documents/refresh_token', type='http', auth='user')
    def google_drive_service_refresh_token(self, redirect=None, *args, **kw):
        _logger.info('Refresh Token response : %s' % (request))
        return 'done'
