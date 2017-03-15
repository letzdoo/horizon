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
from datetime import date
from dateutil.relativedelta import relativedelta

from openerp import api, fields, models, _
from openerp.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = 'res.partner'
    out_inv_comm_algorithm = fields.Selection(selection_add=[('student_id', 'Student Id')])

class Invoice(models.Model):
    _inherit = 'account.invoice'
    
    final_payment_date = fields.Date(compute='_compute_final_payment_date')
    
    @api.depends('residual')
    def _compute_final_payment_date(self):
        if self.residual == 0 :
            for payment in self.payment_move_line_ids:
                date = self.final_payment_date
                if date:
                    date = date if date > payment.date else payment.date
                else :
                    date = payment.date
                self.final_payment_date = date
        else:
            self.final_payment_date = False

class IndividualBloc(models.Model):
    '''Individual Bloc'''
    _inherit = 'school.individual_bloc'

    invoice_id = fields.Many2one(
        'account.invoice', 'Invoice',
        copy=False, readonly=True, track_visibility="onchange")
        
    invoice_count = fields.Integer(compute='_compute_invoice_count',store=True)
     
    @api.depends('invoice_id')  
    @api.one
    def _compute_invoice_count(self):
        self.invoice_count = 1 if self.invoice_id else 0
        
    @api.multi
    def action_invoice_create(self):
        """ Creates invoice(s) for individual bloc.
        @return: Invoice Ids.
        """
        self.ensure_one()
        invoice_ids = []
        InvoiceLine = self.env['account.invoice.line']
        Invoice = self.env['account.invoice']
        invoice = None
        for bloc in self:
            if bloc.invoice_id :
                invoice_ids.append(self.invoice_id.id)
            else :
                invoice = Invoice.create({
                    'name': bloc.name,
                    'origin': bloc.name,
                    'type': 'out_invoice',
                    'partner_id': bloc.student_id.id,
                    'date_invoice': "2016-09-15",
                    
                })
                bloc.write({'invoice_id': invoice.id})
                invoice_ids.append(invoice.id)
        invoice_ids = tuple(invoice_ids)
        return {
            'domain': [('id', 'in', invoice_ids)],
            'name': 'Invoices',
            'res_id': invoice_ids[0],
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'account.invoice',
            'view_id': False,
            'views': [(self.env.ref('account.invoice_form').id, 'form'),(self.env.ref('account.invoice_tree').id, 'tree')],
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window'
        }
        
class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"
    
    # TODO : too bad but no extention possible, so we duplicate
    @api.one
    def compute(self, value, date_ref=False):
        date_ref = date_ref or fields.Date.today()
        amount = value
        result = []
        if self.env.context.get('currency_id'):
            currency = self.env['res.currency'].browse(self.env.context['currency_id'])
        else:
            currency = self.env.user.company_id.currency_id
        prec = currency.decimal_places
        
        for line in self.line_ids:
            if line.value == 'fixed':
                amt = round(line.value_amount, prec)
            elif line.value == 'percent':
                amt = round(value * (line.value_amount / 100.0), prec)
            elif line.value == 'balance':
                amt = round(amount, prec)
            if amt:
                next_date = fields.Date.from_string(date_ref)
                if line.option == 'day_after_invoice_date':
                    next_date += relativedelta(days=line.days)
                elif line.option == 'fix_day_following_month':
                    next_first_date = next_date + relativedelta(day=1, months=1)  # Getting 1st of next month
                    next_date = next_first_date + relativedelta(days=line.days - 1)
                elif line.option == 'last_day_following_month':
                    next_date += relativedelta(day=31, months=1)  # Getting last day of next month
                elif line.option == 'last_day_current_month':
                    next_date += relativedelta(day=31, months=0)  # Getting last day of next month
                elif line.option == 'next_day_in_year':
                    the_date = date(next_date.year, line.month, line.day)
                    if the_date < next_date:
                        the_date = date(next_date.year + 1, line.month, line.day)
                    next_date = the_date
                result.append((fields.Date.to_string(next_date), amt))
                amount -= amt
        amount = reduce(lambda x, y: x + y[1], result, 0.0)
        dist = round(value - amount, prec)
        if dist:
            last_date = result and result[-1][0] or fields.Date.today()
            result.append((last_date, dist))
        return result
        
class AccountPaymentTermLine(models.Model):
    _inherit = "account.payment.term.line"
    
    option = fields.Selection(selection_add=[('next_day_in_year', 'Next Fixed Day/Month')])

    day = fields.Integer(string="Day in month")
    month = fields.Integer(string="Day in month")