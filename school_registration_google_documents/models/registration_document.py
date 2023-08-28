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

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class OfficialDocument(models.Model):
    """Official Document"""

    _inherit = "school.official_document"

    google_drive_files = fields.One2many(
        "google_drive_file", "official_document_id", string="Official Document"
    )

    def _compute_attachment_count(self):
        for doc in self:
            doc.attachment_count = len(doc.attachment_ids) + len(doc.google_drive_files)


class GoogleDriveFile(models.Model):
    _inherit = "google_drive_file"

    official_document_id = fields.Many2one(
        "school.official_document", "Related Official Document"
    )
    is_available = fields.Boolean(related="official_document_id.is_available")

    @api.onchange("official_document_id")
    def onchange_official_document_id(self):
        if self.official_document_id:
            google_service = self.env.company.google_drive_id
            if len(self.official_document_id.google_drive_files) == 1:
                doc_name = f"CRLG - {self.env.user.current_year_id.name} - {self.official_document_id.name}"
                google_service.rename_file(self, doc_name)
            else:
                total = len(self.official_document_id.google_drive_files)
                for index, file in enumerate(
                    self.official_document_id.google_drive_files
                ):
                    doc_name = f"CRLG - {self.env.user.current_year_id.name} - {self.official_document_id.name} ({index}/{total})"
                    google_service.rename_file(file, doc_name)
