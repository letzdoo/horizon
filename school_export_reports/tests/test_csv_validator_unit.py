# -*- coding: utf-8 -*-
import unittest
import tempfile
import os
from unittest.mock import patch, mock_open
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from odoo.addons.school_export_reports.utils.csv_validator import CSVValidator


class TestCSVValidatorUnit(TransactionCase):
    """Unit tests for CSV validator utility class."""

    def test_csv_validator_initialization(self):
        """Test CSV validator initialization."""
        validator = CSVValidator('/test/path.csv')
        self.assertEqual(validator.file_path, '/test/path.csv')
        self.assertEqual(validator.encoding, 'utf-8')
        self.assertEqual(validator.validation_errors, [])

    def test_validate_file_exists_missing_file(self):
        """Test validation failure when file doesn't exist."""
        validator = CSVValidator('/nonexistent/file.csv')

        with self.assertRaisesRegex(UserError, "CSV file not found"):
            validator.validate_file_exists()

    def test_validate_file_exists_no_path(self):
        """Test validation failure when no path provided."""
        validator = CSVValidator('')

        with self.assertRaisesRegex(UserError, "No CSV file path provided"):
            validator.validate_file_exists()

    @patch('builtins.open')
    @patch('os.path.exists')
    @patch('os.path.isfile')
    def test_validate_file_exists_success(self, mock_isfile, mock_exists, mock_open):
        """Test successful file existence validation."""
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_open.return_value.__enter__.return_value = None

        validator = CSVValidator('/test/file.csv')
        result = validator.validate_file_exists()

        self.assertTrue(result)

    @patch('builtins.open')
    @patch('os.path.exists')
    @patch('os.path.isfile')
    def test_validate_file_exists_permission_denied(self, mock_isfile, mock_exists, mock_open):
        """Test validation failure due to permission issues."""
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_open.side_effect = PermissionError("Permission denied")

        validator = CSVValidator('/test/file.csv')

        with self.assertRaisesRegex(UserError, "Permission denied"):
            validator.validate_file_exists()

    @patch('chardet.detect')
    @patch('builtins.open', new_callable=mock_open, read_data=b'test data')
    def test_detect_encoding_utf8(self, mock_file, mock_chardet):
        """Test UTF-8 encoding detection."""
        mock_chardet.return_value = {'encoding': 'utf-8'}

        validator = CSVValidator('/test/file.csv')
        encoding = validator.detect_encoding()

        self.assertEqual(encoding, 'utf-8')
        self.assertEqual(validator.encoding, 'utf-8')

    @patch('chardet.detect')
    @patch('builtins.open', new_callable=mock_open, read_data=b'test data')
    def test_detect_encoding_ascii_to_utf8(self, mock_file, mock_chardet):
        """Test ASCII encoding converted to UTF-8."""
        mock_chardet.return_value = {'encoding': 'ascii'}

        validator = CSVValidator('/test/file.csv')
        encoding = validator.detect_encoding()

        self.assertEqual(encoding, 'utf-8')  # Should prefer UTF-8

    def test_detect_encoding_error(self):
        """Test encoding detection failure."""
        validator = CSVValidator('/nonexistent/file.csv')

        with self.assertRaisesRegex(UserError, "Encoding error"):
            validator.detect_encoding()

    @patch('builtins.open', new_callable=mock_open, read_data='header1,header2\ndata1,data2\ndata3,data4\n')
    def test_validate_csv_structure_valid(self, mock_file):
        """Test successful CSV structure validation."""
        validator = CSVValidator('/test/file.csv')
        validator.encoding = 'utf-8'

        result = validator.validate_csv_structure()

        self.assertTrue(result)
        self.assertEqual(len(validator.validation_errors), 0)

    @patch('builtins.open', new_callable=mock_open, read_data='')
    def test_validate_csv_structure_empty_file(self, mock_file):
        """Test validation failure for empty CSV file."""
        validator = CSVValidator('/test/file.csv')
        validator.encoding = 'utf-8'

        with self.assertRaisesRegex(UserError, "CSV file is empty"):
            validator.validate_csv_structure()

    @patch('builtins.open', new_callable=mock_open, read_data='header1,header2\ndata1\ndata2,data3,extra\n')
    def test_validate_csv_structure_inconsistent_columns(self, mock_file):
        """Test validation failure for inconsistent column counts."""
        validator = CSVValidator('/test/file.csv')
        validator.encoding = 'utf-8'

        with self.assertRaisesRegex(UserError, "CSV file validation failed"):
            validator.validate_csv_structure()

    @patch('builtins.open', new_callable=mock_open, read_data='header1,header1,header2\ndata1,data2,data3\n')
    def test_validate_csv_structure_duplicate_headers(self, mock_file):
        """Test validation failure for duplicate headers."""
        validator = CSVValidator('/test/file.csv')
        validator.encoding = 'utf-8'

        with self.assertRaisesRegex(UserError, "duplicate column headers"):
            validator.validate_csv_structure()

    @patch('builtins.open', new_callable=mock_open, read_data='header1,header2\n')
    def test_validate_csv_structure_no_data_rows(self, mock_file):
        """Test validation failure for CSV with headers but no data."""
        validator = CSVValidator('/test/file.csv')
        validator.encoding = 'utf-8'

        with self.assertRaisesRegex(UserError, "no data rows"):
            validator.validate_csv_structure()

    @patch('builtins.open', new_callable=mock_open, read_data='id,name,email\n1,John,john@example.com\n2,Jane,jane@example.com\n')
    def test_validate_required_columns_success(self, mock_file):
        """Test successful required columns validation."""
        validator = CSVValidator('/test/file.csv')
        validator.encoding = 'utf-8'

        result = validator.validate_required_columns(['id', 'name'])

        self.assertTrue(result)

    @patch('builtins.open', new_callable=mock_open, read_data='id,name,email\n1,John,john@example.com\n')
    def test_validate_required_columns_missing(self, mock_file):
        """Test validation failure for missing required columns."""
        validator = CSVValidator('/test/file.csv')
        validator.encoding = 'utf-8'

        with self.assertRaisesRegex(UserError, "Missing required columns"):
            validator.validate_required_columns(['id', 'name', 'phone'])

    def test_validate_required_columns_empty_list(self):
        """Test required columns validation with empty requirements."""
        validator = CSVValidator('/test/file.csv')

        result = validator.validate_required_columns([])

        self.assertTrue(result)

    @patch('builtins.open', new_callable=mock_open, read_data='nom,prénom,école\nJean,Dupont,École Primaire\n')
    def test_validate_french_characters(self, mock_file):
        """Test French character validation."""
        validator = CSVValidator('/test/file.csv')
        validator.encoding = 'utf-8'

        result = validator.validate_french_characters()

        self.assertTrue(result)

    @patch('builtins.open', new_callable=mock_open)
    def test_validate_french_characters_encoding_error(self, mock_file):
        """Test French character validation with encoding error."""
        mock_file.side_effect = UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid start byte')

        validator = CSVValidator('/test/file.csv')
        validator.encoding = 'utf-8'

        with self.assertRaisesRegex(UserError, "French character validation failed"):
            validator.validate_french_characters()

    @patch('os.path.getsize')
    @patch('builtins.open', new_callable=mock_open, read_data='header1,header2\ndata1,data2\ndata3,data4\n')
    def test_get_file_stats(self, mock_file, mock_getsize):
        """Test file statistics computation."""
        mock_getsize.return_value = 1024

        validator = CSVValidator('/test/file.csv')
        validator.encoding = 'utf-8'

        stats = validator.get_file_stats()

        self.assertIsNotNone(stats)
        self.assertEqual(stats['headers'], ['header1', 'header2'])
        self.assertEqual(stats['row_count'], 2)
        self.assertEqual(stats['column_count'], 2)
        self.assertEqual(stats['file_size_bytes'], 1024)
        self.assertEqual(stats['encoding'], 'utf-8')

    def test_get_file_stats_error(self):
        """Test file statistics with error."""
        validator = CSVValidator('/nonexistent/file.csv')

        stats = validator.get_file_stats()

        self.assertIsNone(stats)