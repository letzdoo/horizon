# -*- coding: utf-8 -*-
import os
import csv
import chardet
import logging
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CSVDataSource(models.Model):
    """Model for handling CSV file access and validation."""
    _name = 'csv.data.source'
    _description = 'CSV Data Source'

    file_path = fields.Char(
        string='File Path',
        required=True,
        help='Full path to CSV file'
    )
    last_modified = fields.Datetime(
        string='Last Modified',
        compute='_compute_file_stats',
        help='File modification timestamp'
    )
    header_row = fields.Text(
        string='CSV Headers',
        compute='_compute_file_stats',
        help='CSV column headers'
    )
    record_count = fields.Integer(
        string='Record Count',
        compute='_compute_file_stats',
        help='Number of data rows in CSV'
    )
    encoding = fields.Char(
        string='File Encoding',
        default='utf-8',
        help='Character encoding of CSV file'
    )
    validation_status = fields.Selection([
        ('valid', 'Valid'),
        ('invalid', 'Invalid'),
        ('missing', 'Missing'),
    ], string='Validation Status', default='valid')

    validation_errors = fields.Text(
        string='Validation Errors',
        help='Detailed validation error messages'
    )

    @api.depends('file_path')
    def _compute_file_stats(self):
        """Compute file statistics and metadata."""
        for record in self:
            if not record.file_path or not os.path.exists(record.file_path):
                record.last_modified = False
                record.header_row = False
                record.record_count = 0
                continue

            try:
                # Get file modification time
                stat = os.stat(record.file_path)
                record.last_modified = fields.Datetime.from_timestamp(stat.st_mtime)

                # Read CSV headers and count records
                encoding = record._detect_encoding()
                with open(record.file_path, 'r', encoding=encoding) as f:
                    reader = csv.reader(f)
                    headers = next(reader, [])
                    record.header_row = ','.join(headers)
                    record.record_count = sum(1 for row in reader)

            except Exception as e:
                _logger.error(f"Error computing file stats for {record.file_path}: {e}")
                record.last_modified = False
                record.header_row = False
                record.record_count = 0

    def _detect_encoding(self):
        """Detect character encoding of CSV file."""
        if not self.file_path or not os.path.exists(self.file_path):
            raise UserError(f"File not found: {self.file_path}")

        try:
            with open(self.file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB for detection
                result = chardet.detect(raw_data)
                encoding = result.get('encoding', 'utf-8')

                # Prefer UTF-8 for French character support
                if encoding.lower() in ['ascii', 'windows-1252']:
                    encoding = 'utf-8'

                self.encoding = encoding
                return encoding

        except Exception as e:
            error_msg = f"Encoding detection failed: {str(e)}"
            _logger.error(error_msg)
            raise UserError(f"Encoding error: {error_msg}")

    def _validate_csv_structure(self):
        """Validate CSV file structure and content."""
        if not self.file_path:
            self.validation_status = 'invalid'
            self.validation_errors = "No file path specified"
            return

        if not os.path.exists(self.file_path):
            self.validation_status = 'missing'
            self.validation_errors = f"File not found: {self.file_path}"
            return

        try:
            # Detect encoding first
            encoding = self._detect_encoding()

            # Validate CSV structure
            errors = []
            with open(self.file_path, 'r', encoding=encoding) as f:
                reader = csv.reader(f)

                # Check if file has content
                try:
                    headers = next(reader)
                    if not headers:
                        errors.append("CSV file has no headers")
                except StopIteration:
                    errors.append("CSV file is empty")

                # Check for minimum required structure
                if len(headers) < 1:
                    errors.append("CSV file must have at least one column")

                # Validate encoding by trying to read all content
                try:
                    for i, row in enumerate(reader):
                        if i > 1000:  # Only validate first 1000 rows for performance
                            break
                        # Just reading validates encoding
                        pass
                except UnicodeDecodeError as e:
                    errors.append(f"Invalid encoding detected: {str(e)}")

            if errors:
                self.validation_status = 'invalid'
                self.validation_errors = '\n'.join(errors)
            else:
                self.validation_status = 'valid'
                self.validation_errors = False

        except Exception as e:
            self.validation_status = 'invalid'
            self.validation_errors = f"Validation error: {str(e)}"
            _logger.error(f"CSV validation failed for {self.file_path}: {e}")

    def validate_required_columns(self, required_columns):
        """Validate that CSV contains all required columns."""
        if not self.header_row:
            self._compute_file_stats()

        if not self.header_row:
            return False, ["Cannot read CSV headers"]

        headers = [h.strip().lower() for h in self.header_row.split(',')]
        required = [c.strip().lower() for c in required_columns]

        missing = [col for col in required if col not in headers]
        if missing:
            return False, [f"Missing required column: '{col}'" for col in missing]

        return True, []