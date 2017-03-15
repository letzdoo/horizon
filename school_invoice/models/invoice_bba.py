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
import re, time, random
from openerp import api
from openerp.osv import fields, osv
from openerp.tools.translate import _
import logging
from openerp.exceptions import UserError
_logger = logging.getLogger(__name__)

class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    def generate_bbacomm(self, cr, uid, ids, type, reference_type, partner_id, reference, context=None):
        try:
            return super(account_invoice, self).generate_bbacomm(cr, uid, ids, type, reference_type, partner_id, reference, context)
        except UserError:
            partner_obj =  self.pool.get('res.partner')
            reference = reference or ''
            algorithm = False
            if partner_id:
                algorithm = partner_obj.browse(cr, uid, partner_id, context=context).out_inv_comm_algorithm
            if (type == 'out_invoice'):
                if reference_type == 'bba':
                    if algorithm == 'student_id':
                        if not self.check_bbacomm(reference):
                            year = time.strftime('%Y')
                            year = year[:1] + year[2:]
                            student_id = format(partner_id,'04d')
                            seq = '001'
                            seq_ids = self.search(cr, uid,
                                [('type', '=', 'out_invoice'), ('reference_type', '=', 'bba'),
                                 ('reference', 'like', '+++%s/%s/%%' % (year,student_id))], order='reference')
                            if seq_ids:
                                prev_seq = int(self.browse(cr, uid, seq_ids[-1]).reference[12:15])
                                if prev_seq < 999:
                                    seq = '%03d' % (prev_seq + 1)
                                else:
                                    raise UserError(_('The daily maximum of outgoing invoices with an automatically generated BBA Structured Communications has been exceeded!' \
                                                        '\nPlease create manually a unique BBA Structured Communication.'))
                            bbacomm = student_id + year + seq
                            base = int(bbacomm)
                            mod = base % 97 or 97
                            reference = '+++%s/%s/%s%02d+++' % (year, student_id, seq, mod)
                    else:
                        raise UserError(_("Unsupported Structured Communication Type Algorithm '%s' !" \
                                            "\nPlease contact your Odoo support channel.") % algorithm)
            return {'value': {'reference': reference}}