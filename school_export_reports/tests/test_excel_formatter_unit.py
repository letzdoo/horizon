# -*- coding: utf-8 -*-
import unittest
from unittest.mock import Mock, patch
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from odoo.addons.school_export_reports.utils.excel_formatter import ExcelFormatter


class TestExcelFormatterUnit(TransactionCase):
    """Unit tests for Excel formatter utility class."""

    def setUp(self):
        """Set up test fixtures with mock workbook."""
        super().setUp()
        self.mock_workbook = Mock()
        self.mock_format = Mock()
        self.mock_workbook.add_format.return_value = self.mock_format
        self.formatter = ExcelFormatter(self.mock_workbook)

    def test_excel_formatter_initialization(self):
        """Test Excel formatter initialization."""
        self.assertEqual(self.formatter.workbook, self.mock_workbook)
        self.assertIn('header', self.formatter.formats)
        self.assertIn('data', self.formatter.formats)
        self.assertIn('french_text', self.formatter.formats)

    def test_create_standard_formats(self):
        """Test creation of standard formatting styles."""
        expected_formats = ['header', 'data', 'french_text', 'numeric', 'date', 'error']

        for format_name in expected_formats:
            self.assertIn(format_name, self.formatter.formats)

    def test_get_format_existing(self):
        """Test getting an existing format."""
        header_format = self.formatter.get_format('header')
        self.assertEqual(header_format, self.formatter.formats['header'])

    def test_get_format_nonexistent(self):
        """Test getting a non-existent format returns default."""
        unknown_format = self.formatter.get_format('unknown_format')
        self.assertEqual(unknown_format, self.formatter.formats['data'])

    def test_create_custom_format(self):
        """Test creating a custom format."""
        properties = {'bold': True, 'font_size': 14}

        custom_format = self.formatter.create_custom_format(properties)

        # Should add Unicode font support automatically
        expected_properties = properties.copy()
        expected_properties['font_name'] = 'Arial Unicode MS'
        self.mock_workbook.add_format.assert_called_with(expected_properties)

    def test_create_custom_format_with_font_name(self):
        """Test creating custom format with existing font name."""
        properties = {'bold': True, 'font_name': 'Times New Roman'}

        self.formatter.create_custom_format(properties)

        self.mock_workbook.add_format.assert_called_with(properties)

    def test_format_worksheet_headers(self):
        """Test formatting and writing headers to worksheet."""
        mock_worksheet = Mock()
        headers = ['Header 1', 'Header 2', 'Header 3']

        result = self.formatter.format_worksheet_headers(mock_worksheet, headers)

        self.assertTrue(result)
        # Should write each header
        self.assertEqual(mock_worksheet.write.call_count, 3)
        # Should freeze panes
        mock_worksheet.freeze_panes.assert_called_once_with(1, 0)

    def test_format_worksheet_headers_error(self):
        """Test header formatting with error."""
        mock_worksheet = Mock()
        mock_worksheet.write.side_effect = Exception("Write error")
        headers = ['Header 1']

        with self.assertRaisesRegex(UserError, "Excel header formatting failed"):
            self.formatter.format_worksheet_headers(mock_worksheet, headers)

    def test_auto_adjust_columns(self):
        """Test automatic column width adjustment."""
        mock_worksheet = Mock()
        headers = ['Short', 'A Very Long Header Name', 'Med']

        result = self.formatter.auto_adjust_columns(mock_worksheet, headers)

        self.assertTrue(result)
        # Should set column width for each header
        self.assertEqual(mock_worksheet.set_column.call_count, 3)

    def test_auto_adjust_columns_with_max_width(self):
        """Test column adjustment with maximum width limit."""
        mock_worksheet = Mock()
        headers = ['A' * 100]  # Very long header

        result = self.formatter.auto_adjust_columns(mock_worksheet, headers, max_width=30)

        self.assertTrue(result)
        # Should limit width to max_width
        mock_worksheet.set_column.assert_called_with(0, 0, 30)

    def test_detect_french_content_with_accents(self):
        """Test detection of French accented characters."""
        french_texts = [
            'École Primaire',
            'Mathématiques',
            'Français',
            'élève',
            'crédit'
        ]

        for text in french_texts:
            result = self.formatter.detect_french_content(text)
            self.assertTrue(result, f"Should detect French content in: {text}")

    def test_detect_french_content_with_words(self):
        """Test detection of French words."""
        french_texts = [
            'École de musique',
            'Cours de Français',
            'Mathématiques avancées'
        ]

        for text in french_texts:
            result = self.formatter.detect_french_content(text)
            self.assertTrue(result, f"Should detect French content in: {text}")

    def test_detect_french_content_english_only(self):
        """Test no detection for English-only content."""
        english_texts = [
            'School Report',
            'Mathematics',
            'English Class',
            'Student Name'
        ]

        for text in english_texts:
            result = self.formatter.detect_french_content(text)
            self.assertFalse(result, f"Should not detect French content in: {text}")

    def test_detect_french_content_non_string(self):
        """Test French content detection with non-string input."""
        non_strings = [123, None, [], {}]

        for value in non_strings:
            result = self.formatter.detect_french_content(value)
            self.assertFalse(result)

    def test_format_cell_by_content_numeric(self):
        """Test cell formatting for numeric content."""
        mock_worksheet = Mock()

        result = self.formatter.format_cell_by_content(mock_worksheet, 1, 2, 123)

        self.assertTrue(result)
        mock_worksheet.write.assert_called_once_with(1, 2, 123, self.formatter.get_format('numeric'))

    def test_format_cell_by_content_french_text(self):
        """Test cell formatting for French text content."""
        mock_worksheet = Mock()

        result = self.formatter.format_cell_by_content(mock_worksheet, 1, 2, 'École Primaire')

        self.assertTrue(result)
        mock_worksheet.write.assert_called_once_with(1, 2, 'École Primaire', self.formatter.get_format('french_text'))

    def test_format_cell_by_content_regular_text(self):
        """Test cell formatting for regular text content."""
        mock_worksheet = Mock()

        result = self.formatter.format_cell_by_content(mock_worksheet, 1, 2, 'Regular Text')

        self.assertTrue(result)
        mock_worksheet.write.assert_called_once_with(1, 2, 'Regular Text', self.formatter.get_format('data'))

    def test_format_cell_by_content_empty_value(self):
        """Test cell formatting for empty/None values."""
        mock_worksheet = Mock()

        result = self.formatter.format_cell_by_content(mock_worksheet, 1, 2, None)

        self.assertTrue(result)
        mock_worksheet.write.assert_called_once_with(1, 2, None, self.formatter.get_format('data'))

    def test_format_cell_by_content_error(self):
        """Test cell formatting with write error."""
        mock_worksheet = Mock()
        mock_worksheet.write.side_effect = Exception("Write error")

        result = self.formatter.format_cell_by_content(mock_worksheet, 1, 2, 'Test')

        # Should still return True as it falls back to plain write
        self.assertTrue(result)

    def test_add_report_title(self):
        """Test adding formatted title to worksheet."""
        mock_worksheet = Mock()

        result = self.formatter.add_report_title(mock_worksheet, 'Test Report', '2023-01-01')

        self.assertTrue(result)
        mock_worksheet.insert_row.assert_called_once_with(0)
        mock_worksheet.write.assert_called_once()
        mock_worksheet.freeze_panes.assert_called_once_with(2, 0)

    def test_add_report_title_no_date(self):
        """Test adding title without date."""
        mock_worksheet = Mock()

        result = self.formatter.add_report_title(mock_worksheet, 'Test Report')

        self.assertTrue(result)
        mock_worksheet.write.assert_called_once()

    def test_apply_data_validation_list(self):
        """Test applying list data validation."""
        mock_worksheet = Mock()

        result = self.formatter.apply_data_validation(mock_worksheet, 0, 'list', ['A', 'B', 'C'])

        self.assertTrue(result)
        mock_worksheet.data_validation.assert_called_once()

    def test_apply_data_validation_length(self):
        """Test applying length data validation."""
        mock_worksheet = Mock()

        result = self.formatter.apply_data_validation(mock_worksheet, 0, 'length', {'min': 1, 'max': 50})

        self.assertTrue(result)
        mock_worksheet.data_validation.assert_called_once()

    def test_finalize_worksheet(self):
        """Test worksheet finalization."""
        mock_worksheet = Mock()
        headers = ['Header 1', 'Header 2']

        result = self.formatter.finalize_worksheet(mock_worksheet, headers)

        self.assertTrue(result)
        mock_worksheet.set_landscape.assert_called_once()
        mock_worksheet.fit_to_pages.assert_called_once_with(1, 0)
        mock_worksheet.set_margins.assert_called_once()

    def test_finalize_worksheet_error(self):
        """Test worksheet finalization with error."""
        mock_worksheet = Mock()
        mock_worksheet.set_landscape.side_effect = Exception("Format error")

        result = self.formatter.finalize_worksheet(mock_worksheet, ['Header'])

        self.assertFalse(result)