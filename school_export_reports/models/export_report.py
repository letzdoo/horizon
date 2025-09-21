# -*- coding: utf-8 -*-
import os
import csv
import logging
from datetime import datetime
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ExportReport(models.Model):
    """Model for tracking Excel report generation from CSV export data."""
    _name = 'export.report'
    _description = 'Export Report'
    _order = 'generation_timestamp desc'

    name = fields.Char(
        string='Report Name',
        required=True,
        help='Display name for this report'
    )
    report_type = fields.Selection([
        ('programs', 'Educational Programs Report'),
        ('students', 'Students Report'),
        ('teachers', 'Teachers Report'),
        ('blocs', 'Academic Blocs Report'),
    ], string='Report Type', required=True)

    csv_source_path = fields.Char(
        string='CSV Source Path',
        required=True,
        help='Path to source CSV file'
    )
    generation_timestamp = fields.Datetime(
        string='Generated At',
        default=fields.Datetime.now,
        help='When this report was generated'
    )
    file_size_bytes = fields.Integer(
        string='File Size (Bytes)',
        compute='_compute_file_stats',
        store=True,
        help='Size of generated Excel file'
    )
    record_count = fields.Integer(
        string='Records Processed',
        compute='_compute_file_stats',
        store=True,
        help='Number of CSV records processed'
    )
    status = fields.Selection([
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('error', 'Error'),
    ], string='Status', default='pending', required=True)

    error_message = fields.Text(
        string='Error Details',
        help='Detailed error message if generation failed'
    )

    @api.depends('csv_source_path', 'status')
    def _compute_file_stats(self):
        """Compute file size and record count from CSV source."""
        for record in self:
            if record.status == 'success' and record.csv_source_path:
                try:
                    if os.path.exists(record.csv_source_path):
                        # Count CSV records
                        with open(record.csv_source_path, 'r', encoding='utf-8') as f:
                            reader = csv.reader(f)
                            next(reader, None)  # Skip header
                            record.record_count = sum(1 for row in reader)

                        # Mock Excel file size (would be actual Excel file in real implementation)
                        record.file_size_bytes = record.record_count * 100  # Approximate
                    else:
                        record.record_count = 0
                        record.file_size_bytes = 0
                except Exception:
                    record.record_count = 0
                    record.file_size_bytes = 0
            else:
                record.record_count = 0
                record.file_size_bytes = 0

    def generate_programs_report(self):
        """Generate Excel report from school_programs.csv."""
        return self._generate_report('programs', 'school_programs.csv')

    def generate_students_report(self):
        """Generate Excel report from school_students.csv."""
        return self._generate_report('students', 'school_students.csv')

    def generate_teachers_report(self):
        """Generate Excel report from school_teachers.csv."""
        return self._generate_report('teachers', 'school_teachers.csv')

    def generate_blocs_report(self):
        """Generate Excel report from school_blocs.csv."""
        return self._generate_report('blocs', 'school_blocs.csv')

    def _generate_report(self, report_type, csv_filename):
        """Core report generation logic with fail-fast error handling."""
        try:
            # Validate CSV file exists
            csv_path = f'/export/{csv_filename}'
            if not os.path.exists(csv_path):
                error_msg = f"CSV file not found: {csv_filename}"
                self._create_error_record(report_type, csv_path, error_msg)
                raise UserError(error_msg)

            # Validate CSV structure
            csv_source = self.env['csv.data.source'].create({
                'file_path': csv_path
            })
            csv_source._validate_csv_structure()

            if csv_source.validation_status != 'valid':
                error_msg = f"CSV file validation failed: {csv_source.validation_errors}"
                self._create_error_record(report_type, csv_path, error_msg)
                raise UserError("CSV file validation failed")

            # Create report record
            report = self.create({
                'name': f'{report_type.title()} Report - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                'report_type': report_type,
                'csv_source_path': csv_path,
                'status': 'success',
            })

            # Generate Excel file (simplified for MVP)
            download_url = f'/web/content/export.report/{report.id}/excel_file'

            return {
                'success': True,
                'report_id': report.id,
                'download_url': download_url,
                'record_count': report.record_count,
            }

        except UserError:
            raise
        except Exception as e:
            error_msg = f"Excel generation failed: {str(e)}"
            self._create_error_record(report_type, csv_path if 'csv_path' in locals() else '', error_msg)
            raise UserError("Excel generation failed")

    def _create_error_record(self, report_type, csv_path, error_message):
        """Create error report record for failed generations."""
        self.create({
            'name': f'{report_type.title()} Report - ERROR - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
            'report_type': report_type,
            'csv_source_path': csv_path,
            'status': 'error',
            'error_message': f'{error_message}\nAttempted: generate_{report_type}_report\nTimestamp: {datetime.now()}'
        })

    def write(self, vals):
        """Prevent modification of error reports (immutable once created)."""
        for record in self:
            if record.status == 'error' and 'status' in vals and vals['status'] != 'error':
                raise UserError("Cannot modify error report records")
        return super().write(vals)