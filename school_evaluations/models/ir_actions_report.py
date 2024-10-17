##############################################################################
#
#    Copyright (c) 2024 ito-invest.lu
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

import io
import logging

from odoo import models
#from odoo.tools.safe_eval import safe_eval, time

_logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        # Variable report_ref can be a report object OR the report name, so we must get the object.  
        report = self._get_report(report_ref)
        self.sudo()
        # Is it "Deliberation Report Annexes" (ID report_deliberation_annexe) for ONE individual bloc(k) ?
        deliberation_report = self.env.ref('school_evaluations.report_deliberation_annexe')
        if(len(res_ids) == 1 and report == deliberation_report):
            # Generate "Evaluations for student" (ID report_evaluation_for_student).
            deliberation_report_for_student = self.env.ref('school_evaluations.report_evaluation_for_student')
            self._render_qweb_pdf(
                deliberation_report_for_student, res_ids, data
            )

        # Anyway, generate the main report the default way.
        return super(IrActionsReport, self)._render_qweb_pdf(
                report_ref=report_ref, res_ids=res_ids, data=data
        )        
