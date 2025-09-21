# -*- coding: utf-8 -*-
import os
import csv
import chardet
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CSVValidator:
    """Utility class for validating CSV files with fail-fast error handling."""

    def __init__(self, file_path):
        """Initialize validator with CSV file path."""
        self.file_path = file_path
        self.encoding = 'utf-8'
        self.validation_errors = []

    def validate_file_exists(self):
        """Validate that CSV file exists and is accessible."""
        if not self.file_path:
            raise UserError("No CSV file path provided")

        if not os.path.exists(self.file_path):
            raise UserError(f"CSV file not found: {os.path.basename(self.file_path)}")

        if not os.path.isfile(self.file_path):
            raise UserError(f"Path is not a file: {self.file_path}")

        try:
            with open(self.file_path, 'r'):
                pass  # Just test if file can be opened
        except PermissionError:
            raise UserError(f"Permission denied accessing CSV file: {os.path.basename(self.file_path)}")

        return True

    def detect_encoding(self):
        """Detect and validate character encoding, prefer UTF-8 for French support."""
        try:
            with open(self.file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB
                result = chardet.detect(raw_data)
                detected_encoding = result.get('encoding', 'utf-8')

                # Test if file can be read with detected encoding
                with open(self.file_path, 'r', encoding=detected_encoding) as test_file:
                    test_file.read(1000)  # Try to read some content

                # Prefer UTF-8 for French character support
                if detected_encoding.lower() in ['ascii', 'windows-1252']:
                    # Try UTF-8 first for French characters
                    try:
                        with open(self.file_path, 'r', encoding='utf-8') as test_file:
                            test_file.read(1000)
                        self.encoding = 'utf-8'
                    except UnicodeDecodeError:
                        self.encoding = detected_encoding
                else:
                    self.encoding = detected_encoding

                return self.encoding

        except Exception as e:
            error_msg = f"Encoding detection failed: {str(e)}"
            _logger.error(error_msg)
            raise UserError(f"Encoding error: {error_msg}")

    def validate_csv_structure(self):
        """Validate CSV file structure and content."""
        self.validation_errors = []

        try:
            # Ensure encoding is detected
            if not self.encoding:
                self.detect_encoding()

            with open(self.file_path, 'r', encoding=self.encoding) as f:
                reader = csv.reader(f)

                # Validate headers exist
                try:
                    headers = next(reader)
                    if not headers or all(not h.strip() for h in headers):
                        self.validation_errors.append("CSV file has no valid headers")
                        return False
                except StopIteration:
                    self.validation_errors.append("CSV file is empty")
                    return False

                # Validate minimum structure
                if len(headers) < 1:
                    self.validation_errors.append("CSV file must have at least one column")

                # Check for duplicate headers
                header_lower = [h.strip().lower() for h in headers]
                if len(header_lower) != len(set(header_lower)):
                    self.validation_errors.append("CSV file contains duplicate column headers")

                # Validate data rows (sample first 100 for performance)
                row_count = 0
                for i, row in enumerate(reader):
                    if i >= 100:  # Limit validation to first 100 rows
                        break
                    row_count += 1

                    # Check row length consistency
                    if len(row) != len(headers):
                        self.validation_errors.append(f"Row {i+2} has {len(row)} columns, expected {len(headers)}")
                        if len(self.validation_errors) > 10:  # Limit error count
                            break

                if row_count == 0:
                    self.validation_errors.append("CSV file contains no data rows")

        except UnicodeDecodeError as e:
            self.validation_errors.append(f"Invalid character encoding: {str(e)}")
            return False
        except Exception as e:
            self.validation_errors.append(f"CSV validation error: {str(e)}")
            return False

        if self.validation_errors:
            error_details = '\n'.join(self.validation_errors)
            raise UserError(f"CSV file validation failed:\n{error_details}")

        return True

    def validate_required_columns(self, required_columns):
        """Validate that CSV contains all required columns."""
        if not required_columns:
            return True

        try:
            with open(self.file_path, 'r', encoding=self.encoding or 'utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader, [])

                headers_lower = [h.strip().lower() for h in headers]
                required_lower = [c.strip().lower() for c in required_columns]

                missing_columns = [col for col in required_lower if col not in headers_lower]
                if missing_columns:
                    missing_list = "', '".join(missing_columns)
                    raise UserError(f"Missing required columns: '{missing_list}'")

                return True

        except StopIteration:
            raise UserError("Cannot validate columns: CSV file is empty")
        except Exception as e:
            raise UserError(f"Column validation error: {str(e)}")

    def validate_french_characters(self):
        """Validate that CSV properly handles French characters."""
        french_test_chars = ['é', 'è', 'à', 'ç', 'ô', 'û', 'ê', 'â', 'î', 'ï', 'ü']

        try:
            with open(self.file_path, 'r', encoding=self.encoding or 'utf-8') as f:
                content = f.read(10000)  # Read first 10KB

                # Check if any French characters are present
                has_french_chars = any(char in content for char in french_test_chars)

                if has_french_chars and self.encoding.lower() not in ['utf-8', 'utf-16', 'latin-1']:
                    _logger.warning(f"CSV contains French characters but encoding is {self.encoding}")
                    # This is a warning, not an error - file may still be valid

                return True

        except UnicodeDecodeError:
            raise UserError("French character validation failed: encoding issue detected")
        except Exception as e:
            _logger.warning(f"French character validation warning: {str(e)}")
            return True  # Don't fail validation for this

    def get_file_stats(self):
        """Get basic statistics about the CSV file."""
        try:
            with open(self.file_path, 'r', encoding=self.encoding or 'utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader, [])
                row_count = sum(1 for row in reader)

                file_size = os.path.getsize(self.file_path)

                return {
                    'headers': headers,
                    'row_count': row_count,
                    'column_count': len(headers),
                    'file_size_bytes': file_size,
                    'encoding': self.encoding
                }

        except Exception as e:
            _logger.error(f"Error getting file stats: {e}")
            return None