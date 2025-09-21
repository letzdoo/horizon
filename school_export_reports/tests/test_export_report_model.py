# -*- coding: utf-8 -*-
import unittest
import os
from unittest.mock import patch, mock_open
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestExportReportModel(TransactionCase):
    """Unit tests for ExportReport model functionality."""

    def setUp(self):
        super().setUp()
        self.ExportReport = self.env['export.report']

    def test_export_report_creation(self):
        """Test creating an export report record."""
        report = self.ExportReport.create({
            'name': 'Test Programs Report',
            'report_type': 'programs',
            'csv_source_path': '/export/school_programs.csv',
            'status': 'pending'
        })

        self.assertEqual(report.name, 'Test Programs Report')
        self.assertEqual(report.report_type, 'programs')
        self.assertEqual(report.status, 'pending')
        self.assertTrue(report.generation_timestamp)

    def test_export_report_status_transitions(self):
        """Test status transitions from pending to success/error."""
        report = self.ExportReport.create({
            'name': 'Test Report',
            'report_type': 'students',
            'csv_source_path': '/export/school_students.csv',
            'status': 'pending'
        })

        # Test successful status transition
        report.write({'status': 'success'})
        self.assertEqual(report.status, 'success')

        # Test error status transition
        error_report = self.ExportReport.create({
            'name': 'Error Report',
            'report_type': 'teachers',
            'csv_source_path': '/export/school_teachers.csv',
            'status': 'error',
            'error_message': 'Test error'
        })
        self.assertEqual(error_report.status, 'error')

    def test_error_report_immutable(self):
        """Test that error reports cannot be modified."""
        error_report = self.ExportReport.create({
            'name': 'Error Report',
            'report_type': 'teachers',
            'csv_source_path': '/export/school_teachers.csv',
            'status': 'error',
            'error_message': 'Test error'
        })

        with self.assertRaisesRegex(UserError, "Cannot modify error report"):
            error_report.write({'status': 'success'})

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='header1,header2\ndata1,data2\n')
    def test_compute_file_stats_success(self, mock_file, mock_exists):
        """Test file statistics computation for successful reports."""
        mock_exists.return_value = True

        report = self.ExportReport.create({
            'name': 'Test Report',
            'report_type': 'programs',
            'csv_source_path': '/export/school_programs.csv',
            'status': 'success'
        })

        # Force computation
        report._compute_file_stats()

        self.assertEqual(report.record_count, 1)  # One data row
        self.assertGreater(report.file_size_bytes, 0)

    def test_compute_file_stats_missing_file(self):
        """Test file statistics when CSV file is missing."""
        report = self.ExportReport.create({
            'name': 'Test Report',
            'report_type': 'programs',
            'csv_source_path': '/export/nonexistent.csv',
            'status': 'success'
        })

        report._compute_file_stats()

        self.assertEqual(report.record_count, 0)
        self.assertEqual(report.file_size_bytes, 0)

    @patch('os.path.exists')
    def test_create_error_record(self, mock_exists):
        """Test creation of error report records."""
        mock_exists.return_value = False

        initial_count = self.ExportReport.search_count([])

        # This should create an error record
        self.ExportReport._create_error_record(
            'programs',
            '/export/missing.csv',
            'File not found'
        )

        final_count = self.ExportReport.search_count([])
        self.assertEqual(final_count, initial_count + 1)

        error_report = self.ExportReport.search([('status', '=', 'error')], limit=1, order='id desc')
        self.assertTrue(error_report)
        self.assertEqual(error_report.report_type, 'programs')
        self.assertIn('File not found', error_report.error_message)

    def test_report_type_selection_values(self):
        """Test that all expected report types are supported."""
        expected_types = ['programs', 'students', 'teachers', 'blocs']

        for report_type in expected_types:
            report = self.ExportReport.create({
                'name': f'Test {report_type.title()} Report',
                'report_type': report_type,
                'csv_source_path': f'/export/school_{report_type}.csv',
                'status': 'pending'
            })
            self.assertEqual(report.report_type, report_type)

    def test_report_ordering(self):
        """Test that reports are ordered by generation timestamp (newest first)."""
        # Create reports with different timestamps
        old_report = self.ExportReport.create({
            'name': 'Old Report',
            'report_type': 'programs',
            'csv_source_path': '/export/school_programs.csv',
            'status': 'success'
        })

        new_report = self.ExportReport.create({
            'name': 'New Report',
            'report_type': 'students',
            'csv_source_path': '/export/school_students.csv',
            'status': 'success'
        })

        reports = self.ExportReport.search([])
        # First report should be the newest one
        self.assertEqual(reports[0].id, new_report.id)

    def test_required_fields_validation(self):
        """Test that required fields are validated."""
        with self.assertRaises(Exception):  # Should raise validation error
            self.ExportReport.create({
                'report_type': 'programs',
                'csv_source_path': '/export/school_programs.csv',
                # Missing required 'name' field
            })

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='id,name,subject\n1,Jean,Français\n2,Marie,Mathématiques\n')
    def test_french_character_handling(self, mock_file, mock_exists):
        """Test that French characters are handled properly in file stats."""
        mock_exists.return_value = True

        report = self.ExportReport.create({
            'name': 'French Test Report',
            'report_type': 'students',
            'csv_source_path': '/export/school_students.csv',
            'status': 'success'
        })

        # Force computation - should not raise encoding errors
        report._compute_file_stats()

        self.assertEqual(report.record_count, 2)  # Two data rows with French chars
        self.assertGreater(report.file_size_bytes, 0)