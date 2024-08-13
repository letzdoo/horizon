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

import io
import logging

from odoo import fields, models, api
from odoo.tools.safe_eval import safe_eval, time

_logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    google_drive_enabled = fields.Boolean(
        string="Save in Google Drive",
        help="If enabled, the report will be saved in Google Drive.",
    )

    google_drive_patner_field = fields.Char(
        string="Partner property to save into",
        help="This field name is the Partner to which the Google Drive Forlder to save to.",
    ) # WARNING TYPO "patner" !

    # Disclaimer: The mention of "pa(r)tner_field" or "partner_id" is not appropriate as long as 
    # the google_drive_folder_mixin can be added to any Model, not just to res_partner. This naming
    # is due to the fact that res_partner has been used to build the process and still implements 
    # this mixin by default in the present module. Thus "res_field" and "res_id" would be better terms:
    # you can use this report class overload for any Model that implements google_drive_folder_mixin.    
    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        google_service = self.env.company.google_drive_id
        # self doesn't have any attributes set and has no id, despite being a ir.actions.report object. We retreive the report based on report_ref.
        report = self._get_report(report_ref)
        self.sudo()
        # If the report is not saved within Google Drive, simply call the ancestor.
        if not (google_service and report.google_drive_enabled and len(res_ids) == 1 and report.google_drive_patner_field):
            return super(IrActionsReport, self)._render_qweb_pdf(
                report_ref=report_ref, res_ids=res_ids, data=data
            )

        # The report must be saved within Google Drive.
        record = self.env[report.model].browse(res_ids)
        partner = record.mapped(report.google_drive_patner_field)

        if report.attachment_use:
            # Checks if the report already exists, and stream it if possible.
            google_doc = google_service.get_report(partner.id,report.id,report.model,record.id)
            if google_doc:
                pdf_content = google_service.get_file(google_doc)
                if pdf_content:
                    content_type = google_doc.mimeType
                    content = io.BytesIO(pdf_content)
                    content.seek(0)
                    return content.read(), content_type

        # The report must be generated and stored in Google Drive.
        pdf_content, content_type = super(IrActionsReport, self)._render_qweb_pdf(
            report_ref=report_ref, res_ids=res_ids, data=data
        )
        content = io.BytesIO(pdf_content)
        
        if partner.google_drive_folder_id:
            report_name = safe_eval(
                report.print_report_name, {"object": record, "time": time}
            )

            file = google_service.create_file(
                content,
                report_name,
                "application/pdf",
                partner.google_drive_folder_id,
            )

            google_drive_file = self.env["google_drive_file"].create(
                {
                    "name": file["name"],
                    "googe_drive_id": file["id"],
                    "mimeType": file["mimeType"],
                    "url": file["webViewLink"],
                    "res_model": partner._name,
                    "res_model_report" : report.model,
                    "res_id_report" : record.id,
                    "report_id": report.id
                }
            )

            partner.google_drive_files += google_drive_file

        content.seek(0)
        return content.read(), content_type

    def write(self, vals):    
        if (vals['google_drive_enabled'] if 'google_drive_enabled' in vals else self.google_drive_enabled) : 
            vals['attachment'] = ''
        else:
            vals['google_drive_patner_field'] = ''     
        return super().write(vals)