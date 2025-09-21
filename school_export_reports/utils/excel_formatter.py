# -*- coding: utf-8 -*-
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ExcelFormatter:
    """Utility class for Excel formatting and styling with French character support."""

    def __init__(self, workbook):
        """Initialize formatter with xlsxwriter workbook."""
        self.workbook = workbook
        self.formats = {}
        self._create_standard_formats()

    def _create_standard_formats(self):
        """Create standard formatting styles."""
        self.formats.update({
            'header': self.workbook.add_format({
                'bold': True,
                'font_size': 12,
                'bg_color': '#D3D3D3',
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'text_wrap': True,
                'font_name': 'Arial Unicode MS'  # Better Unicode support
            }),

            'data': self.workbook.add_format({
                'font_size': 10,
                'border': 1,
                'text_wrap': True,
                'valign': 'top',
                'font_name': 'Arial Unicode MS'
            }),

            'french_text': self.workbook.add_format({
                'font_size': 10,
                'border': 1,
                'text_wrap': True,
                'valign': 'top',
                'font_name': 'Arial Unicode MS',
                'font_color': '#000080'  # Subtle color for French text
            }),

            'numeric': self.workbook.add_format({
                'font_size': 10,
                'border': 1,
                'align': 'right',
                'num_format': '#,##0',
                'font_name': 'Arial Unicode MS'
            }),

            'date': self.workbook.add_format({
                'font_size': 10,
                'border': 1,
                'align': 'center',
                'num_format': 'dd/mm/yyyy',
                'font_name': 'Arial Unicode MS'
            }),

            'error': self.workbook.add_format({
                'font_size': 10,
                'border': 1,
                'bg_color': '#FFE6E6',
                'font_color': '#CC0000',
                'font_name': 'Arial Unicode MS'
            })
        })

    def get_format(self, format_name):
        """Get a predefined format by name."""
        return self.formats.get(format_name, self.formats['data'])

    def create_custom_format(self, properties):
        """Create a custom format with given properties."""
        try:
            # Ensure Unicode font support
            if 'font_name' not in properties:
                properties['font_name'] = 'Arial Unicode MS'

            return self.workbook.add_format(properties)
        except Exception as e:
            _logger.error(f"Error creating custom format: {e}")
            return self.formats['data']

    def format_worksheet_headers(self, worksheet, headers):
        """Format and write headers to worksheet."""
        try:
            header_format = self.get_format('header')

            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_format)

            # Freeze header row
            worksheet.freeze_panes(1, 0)

            return True

        except Exception as e:
            _logger.error(f"Error formatting headers: {e}")
            raise UserError(f"Excel header formatting failed: {str(e)}")

    def auto_adjust_columns(self, worksheet, headers, max_width=50):
        """Auto-adjust column widths based on content."""
        try:
            for col_idx, header in enumerate(headers):
                # Calculate width based on header length, with reasonable limits
                width = min(max(len(str(header)) + 3, 10), max_width)
                worksheet.set_column(col_idx, col_idx, width)

            return True

        except Exception as e:
            _logger.error(f"Error adjusting columns: {e}")
            return False

    def detect_french_content(self, text):
        """Detect if text contains French characters."""
        if not isinstance(text, str):
            return False

        french_chars = ['é', 'è', 'à', 'ç', 'ô', 'û', 'ê', 'â', 'î', 'ï', 'ü', 'ÿ', 'À', 'É', 'È', 'Ç']
        french_words = ['École', 'Français', 'Mathématiques', 'Périodes', 'Crédit']

        return any(char in text for char in french_chars) or \
               any(word.lower() in text.lower() for word in french_words)

    def format_cell_by_content(self, worksheet, row, col, value):
        """Format cell based on content type and French character detection."""
        try:
            if value is None or value == '':
                format_to_use = self.get_format('data')
            elif isinstance(value, (int, float)):
                format_to_use = self.get_format('numeric')
            elif self.detect_french_content(str(value)):
                format_to_use = self.get_format('french_text')
            else:
                format_to_use = self.get_format('data')

            worksheet.write(row, col, value, format_to_use)
            return True

        except Exception as e:
            _logger.error(f"Error formatting cell at {row},{col}: {e}")
            # Fallback to plain write
            worksheet.write(row, col, value)
            return False

    def add_report_title(self, worksheet, title, report_date=None):
        """Add formatted title to the worksheet."""
        try:
            # Insert row at top for title
            worksheet.insert_row(0)

            title_format = self.create_custom_format({
                'bold': True,
                'font_size': 16,
                'font_color': '#000080',
                'align': 'center',
                'font_name': 'Arial Unicode MS'
            })

            # Write title
            if report_date:
                full_title = f"{title} - {report_date}"
            else:
                full_title = title

            worksheet.write(0, 0, full_title, title_format)

            # Adjust header row position
            worksheet.freeze_panes(2, 0)

            return True

        except Exception as e:
            _logger.error(f"Error adding report title: {e}")
            return False

    def apply_data_validation(self, worksheet, col_idx, validation_type, criteria):
        """Apply data validation to a column."""
        try:
            if validation_type == 'list':
                worksheet.data_validation(1, col_idx, 1000, col_idx, {
                    'validate': 'list',
                    'source': criteria
                })
            elif validation_type == 'length':
                worksheet.data_validation(1, col_idx, 1000, col_idx, {
                    'validate': 'length',
                    'criteria': 'between',
                    'minimum': criteria.get('min', 1),
                    'maximum': criteria.get('max', 255)
                })

            return True

        except Exception as e:
            _logger.error(f"Error applying data validation: {e}")
            return False

    def finalize_worksheet(self, worksheet, headers):
        """Apply final formatting and optimizations to worksheet."""
        try:
            # Auto-adjust columns
            self.auto_adjust_columns(worksheet, headers)

            # Set print options
            worksheet.set_landscape()
            worksheet.fit_to_pages(1, 0)  # Fit to one page wide

            # Set margins for better printing
            worksheet.set_margins(0.7, 0.7, 0.75, 0.75)

            return True

        except Exception as e:
            _logger.error(f"Error finalizing worksheet: {e}")
            return False