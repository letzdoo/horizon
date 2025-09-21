# -*- coding: utf-8 -*-
import csv
import logging
from odoo import models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ProgramsReport(models.AbstractModel):
    """Excel report generator for Educational Programs from CSV."""
    _name = 'report.school_export_reports.programs_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Programs Excel Report from CSV'

    def generate_xlsx_report(self, workbook, data, programs):
        """Generate Excel report from school_programs.csv."""
        csv_path = '/export/school_programs.csv'

        # Create worksheet
        worksheet = workbook.add_worksheet('Educational Programs')

        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#D3D3D3',
            'border': 1
        })

        data_format = workbook.add_format({
            'font_size': 10,
            'border': 1,
            'text_wrap': True
        })

        try:
            # Read CSV data with UTF-8 encoding for French characters
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader)

                # Write headers
                for col, header in enumerate(headers):
                    worksheet.write(0, col, header, header_format)

                # Write data rows
                for row_idx, row in enumerate(reader, start=1):
                    for col_idx, cell_value in enumerate(row):
                        worksheet.write(row_idx, col_idx, cell_value, data_format)

                # Auto-adjust column widths
                for col_idx, header in enumerate(headers):
                    worksheet.set_column(col_idx, col_idx, min(len(header) + 5, 50))

                # Freeze header row
                worksheet.freeze_panes(1, 0)

                _logger.info(f"Programs report generated successfully from {csv_path}")

        except FileNotFoundError:
            raise UserError(f"CSV file not found: school_programs.csv")
        except UnicodeDecodeError as e:
            raise UserError(f"Encoding error reading CSV file: {str(e)}")
        except Exception as e:
            _logger.error(f"Error generating programs report: {e}")
            raise UserError(f"Excel generation failed: {str(e)}")


class ProgramsReportWizard(models.TransientModel):
    """Wizard for generating Programs report."""
    _name = 'programs.report.wizard'
    _description = 'Programs Report Generation Wizard'

    def generate_report(self):
        """Generate and download the Programs Excel report."""
        return {
            'type': 'ir.actions.report',
            'report_name': 'school_export_reports.programs_xlsx',
            'report_type': 'xlsx',
            'name': f'Programs Report - {self.env.user.name}',
        }