# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ReportGenerationWizard(models.TransientModel):
    """Wizard for report generation with parameter selection."""
    _name = 'report.generation.wizard'
    _description = 'Report Generation Wizard'

    report_type = fields.Selection([
        ('programs', 'Educational Programs Report'),
        ('students', 'Students Report'),
        ('teachers', 'Teachers Report'),
        ('blocs', 'Academic Blocs Report'),
    ], string='Report Type', required=True)

    csv_file_status = fields.Char(
        string='CSV File Status',
        compute='_compute_csv_file_status',
        help='Status of the CSV file for selected report type'
    )

    @api.depends('report_type')
    def _compute_csv_file_status(self):
        """Check CSV file availability for selected report type."""
        csv_filenames = {
            'programs': 'school_programs.csv',
            'students': 'school_students.csv',
            'teachers': 'school_teachers.csv',
            'blocs': 'school_blocs.csv',
        }

        for wizard in self:
            if wizard.report_type:
                filename = csv_filenames.get(wizard.report_type)
                csv_path = f'/export/{filename}'

                try:
                    csv_source = self.env['csv.data.source'].create({
                        'file_path': csv_path
                    })
                    csv_source._validate_csv_structure()

                    if csv_source.validation_status == 'valid':
                        wizard.csv_file_status = f"✓ Ready - {csv_source.record_count} records"
                    elif csv_source.validation_status == 'missing':
                        wizard.csv_file_status = f"✗ File not found: {filename}"
                    else:
                        wizard.csv_file_status = f"⚠ Validation errors detected"
                except Exception:
                    wizard.csv_file_status = f"✗ Cannot access: {filename}"
            else:
                wizard.csv_file_status = "Select a report type"

    def generate_report(self):
        """Generate the selected report type."""
        if not self.report_type:
            raise UserError("Please select a report type")

        try:
            # Call appropriate generation method
            export_report = self.env['export.report']

            if self.report_type == 'programs':
                result = export_report.generate_programs_report()
            elif self.report_type == 'students':
                result = export_report.generate_students_report()
            elif self.report_type == 'teachers':
                result = export_report.generate_teachers_report()
            elif self.report_type == 'blocs':
                result = export_report.generate_blocs_report()
            else:
                raise UserError(f"Unknown report type: {self.report_type}")

            if result.get('success'):
                # Show success notification
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'success',
                        'title': 'Report Generated Successfully',
                        'message': f'{self.report_type.title()} report generated with {result.get("record_count", 0)} records.',
                        'sticky': False,
                    }
                }
            else:
                raise UserError("Report generation failed")

        except UserError:
            raise
        except Exception as e:
            _logger.error(f"Report generation error: {e}")
            raise UserError(f"Report generation failed: {str(e)}")

    def validate_csv_file(self):
        """Validate the CSV file for selected report type."""
        if not self.report_type:
            raise UserError("Please select a report type first")

        csv_filenames = {
            'programs': 'school_programs.csv',
            'students': 'school_students.csv',
            'teachers': 'school_teachers.csv',
            'blocs': 'school_blocs.csv',
        }

        filename = csv_filenames.get(self.report_type)
        csv_path = f'/export/{filename}'

        try:
            csv_source = self.env['csv.data.source'].create({
                'file_path': csv_path
            })
            csv_source._validate_csv_structure()

            if csv_source.validation_status == 'valid':
                message = f"File validation successful!\n"
                message += f"Records: {csv_source.record_count}\n"
                message += f"Encoding: {csv_source.encoding}\n"
                message += f"Headers: {csv_source.header_row}"

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'success',
                        'title': 'CSV File Valid',
                        'message': message,
                        'sticky': True,
                    }
                }
            else:
                error_message = f"Validation failed for {filename}:\n"
                error_message += csv_source.validation_errors or "Unknown validation error"

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'danger',
                        'title': 'CSV File Invalid',
                        'message': error_message,
                        'sticky': True,
                    }
                }

        except Exception as e:
            _logger.error(f"CSV validation error: {e}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'danger',
                    'title': 'Validation Error',
                    'message': f"Cannot validate {filename}: {str(e)}",
                    'sticky': True,
                }
            }


class QuickReportWizard(models.TransientModel):
    """Quick wizard for immediate report generation."""
    _name = 'quick.report.wizard'
    _description = 'Quick Report Generation'

    def generate_programs_report(self):
        """Quick generation of programs report."""
        return self.env['export.report'].generate_programs_report()

    def generate_students_report(self):
        """Quick generation of students report."""
        return self.env['export.report'].generate_students_report()

    def generate_teachers_report(self):
        """Quick generation of teachers report."""
        return self.env['export.report'].generate_teachers_report()

    def generate_blocs_report(self):
        """Quick generation of blocs report."""
        return self.env['export.report'].generate_blocs_report()