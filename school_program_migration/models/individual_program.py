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

from odoo import models

_logger = logging.getLogger(__name__)


class IndividualProgram(models.Model):
    """Individual Program"""

    _inherit = ["school.individual_program"]

    def action_clean_summaries(self):
        self.ensure_one()
        summaries = self.env["school.individual_course_summary"].search(
            [("program_id", "=", self.id)]
        )
        for summary in summaries:
            if len(summary.ind_course_group_ids) == 0:
                _logger.info("PROGRM MIGRATION - Unlink UE %s" % summary.uid)
                summary.unlink()
