# -*- coding: utf-8 -*-
import csv
import logging
from odoo import models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class BlocsReport(models.AbstractModel):
    """Excel report generator for Academic Blocs from CSV."""
    _name = 'report.school_export_reports.blocs_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Academic Blocs Excel Report from CSV'

    def generate_xlsx_report(self, workbook, data, blocs):
        """Generate Excel report from school_blocs.csv."""
        csv_path = '/export/school_blocs.csv'

        # Create worksheet
        worksheet = workbook.add_worksheet('Academic Blocs')

        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#FFF2E6',
            'border': 1
        })

        data_format = workbook.add_format({
            'font_size': 10,
            'border': 1,
            'text_wrap': True
        })

        # Special format for French academic terminology
        french_format = workbook.add_format({
            'font_size': 10,
            'border': 1,
            'text_wrap': True,
            'font_name': 'Arial Unicode MS'  # Better French character support
        })

        try:
            # Read CSV data with UTF-8 encoding for French characters
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader)

                # Write headers
                for col, header in enumerate(headers):
                    worksheet.write(0, col, header, header_format)

                # Write data rows with French character support
                for row_idx, row in enumerate(reader, start=1):
                    for col_idx, cell_value in enumerate(row):
                        # Use French format for academic terminology columns
                        format_to_use = french_format if any(
                            keyword in headers[col_idx].lower()
                            for keyword in ['bloc', 'matière', 'périodes', 'crédits']
                        ) else data_format

                        worksheet.write(row_idx, col_idx, cell_value, format_to_use)

                # Auto-adjust column widths
                for col_idx, header in enumerate(headers):
                    worksheet.set_column(col_idx, col_idx, min(len(header) + 5, 50))

                # Freeze header row
                worksheet.freeze_panes(1, 0)

                _logger.info(f"Blocs report generated successfully from {csv_path}")

        except FileNotFoundError:
            raise UserError(f"CSV file not found: school_blocs.csv")
        except UnicodeDecodeError as e:
            raise UserError(f"Encoding error reading CSV file: {str(e)}")
        except Exception as e:
            _logger.error(f"Error generating blocs report: {e}")
            raise UserError(f"Excel generation failed: {str(e)}")


class BlocsReportWizard(models.TransientModel):
    """Wizard for generating Academic Blocs report."""
    _name = 'blocs.report.wizard'
    _description = 'Academic Blocs Report Generation Wizard'

    def generate_report(self):
        """Generate and download the Academic Blocs Excel report."""
        return {
            'type': 'ir.actions.report',
            'report_name': 'school_export_reports.blocs_xlsx',
            'report_type': 'xlsx',
            'name': f'Academic Blocs Report - {self.env.user.name}',
        }