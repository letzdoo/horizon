# -*- coding: utf-8 -*-
import base64
from odoo import http
from odoo.http import request, Response
from odoo.exceptions import AccessError, MissingError


class ExportReportController(http.Controller):

    @http.route('/web/content/export.report/<int:report_id>/excel_file/<filename>',
                type='http', auth='user', methods=['GET'])
    def download_excel_report(self, report_id, filename, **kwargs):
        """Download Excel report file."""
        try:
            # Check if user has access to the report
            report = request.env['export.report'].browse(report_id)
            if not report.exists():
                return request.not_found()

            # Check access rights
            report.check_access_rights('read')
            report.check_access_rule('read')

            if not report.excel_file:
                return request.not_found("No Excel file available")

            # Decode the binary content
            file_content = base64.b64decode(report.excel_file)

            # Create response with proper headers
            response = Response(
                file_content,
                headers={
                    'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'Content-Disposition': f'attachment; filename="{report.excel_filename or filename}"',
                    'Content-Length': len(file_content),
                }
            )

            return response

        except (AccessError, MissingError):
            return request.not_found()
        except Exception:
            return request.not_found()