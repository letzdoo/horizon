# -*- coding: utf-8 -*-
import unittest
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestContractPrograms(TransactionCase):
    """Contract test for generate_programs_report method.

    This test validates the API contract defined in contracts/report_generation.yaml
    for the generate_programs_report endpoint. Tests MUST fail before implementation.
    """

    def setUp(self):
        super().setUp()
        self.ExportReport = self.env['export.report']

    def test_generate_programs_report_success(self):
        """Test successful generation of programs report from CSV."""
        # This test MUST fail before implementation exists
        result = self.ExportReport.generate_programs_report()

        # Contract expectations from OpenAPI spec
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        self.assertIn('report_id', result)
        self.assertIn('download_url', result)
        self.assertIn('record_count', result)
        self.assertTrue(result['success'])
        self.assertIsInstance(result['report_id'], int)
        self.assertIsInstance(result['download_url'], str)
        self.assertIsInstance(result['record_count'], int)
        self.assertGreater(result['record_count'], 0)

    def test_generate_programs_report_missing_csv(self):
        """Test error handling when school_programs.csv is missing."""
        # Mock missing file scenario - test MUST fail before implementation
        with self.assertRaisesRegex(UserError, "CSV file not found.*school_programs.csv"):
            self.ExportReport.generate_programs_report()

    def test_generate_programs_report_invalid_csv(self):
        """Test validation failure for corrupted CSV file."""
        # Mock invalid CSV scenario - test MUST fail before implementation
        with self.assertRaisesRegex(UserError, "CSV file validation failed"):
            # This should trigger validation error with detailed messages
            self.ExportReport.generate_programs_report()

    def test_generate_programs_report_creates_record(self):
        """Test that successful generation creates an export report record."""
        # Test MUST fail before implementation exists
        initial_count = self.ExportReport.search_count([])
        result = self.ExportReport.generate_programs_report()

        # Should create one new export report record
        final_count = self.ExportReport.search_count([])
        self.assertEqual(final_count, initial_count + 1)

        # Verify the created record has correct attributes
        report = self.ExportReport.browse(result['report_id'])
        self.assertEqual(report.report_type, 'programs')
        self.assertEqual(report.status, 'success')
        self.assertGreater(report.record_count, 0)
        self.assertGreater(report.file_size_bytes, 0)