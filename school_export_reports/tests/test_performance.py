# -*- coding: utf-8 -*-
import unittest
import time
import tempfile
import csv
import os
import psutil
from odoo.tests.common import TransactionCase


class TestPerformance(TransactionCase):
    """Performance tests for large CSV file processing (1000+ records)."""

    def setUp(self):
        super().setUp()
        self.ExportReport = self.env['export.report']
        self.CSVDataSource = self.env['csv.data.source']
        self.temp_files = []

    def tearDown(self):
        """Clean up temporary files."""
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        super().tearDown()

    def _create_large_csv_file(self, num_records=1000, include_french=True):
        """Create a temporary CSV file with specified number of records."""
        temp_fd, temp_path = tempfile.mkstemp(suffix='.csv', prefix='test_large_')
        os.close(temp_fd)
        self.temp_files.append(temp_path)

        # Sample data with French characters
        french_names = ['Jean-Pierre', 'Marie-Claire', 'François', 'Élise', 'André', 'Céline']
        french_subjects = ['Mathématiques', 'Français', 'Sciences', 'Histoire-Géographie', 'Éducation']
        french_schools = ['École Primaire Saint-Jean', 'Collège République', 'Lycée Napoléon']

        with open(temp_path, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Write headers
            writer.writerow(['id', 'nom', 'prénom', 'matière', 'école', 'note', 'date'])

            # Write data records
            for i in range(num_records):
                name = french_names[i % len(french_names)] if include_french else f'Student{i}'
                subject = french_subjects[i % len(french_subjects)] if include_french else f'Subject{i}'
                school = french_schools[i % len(french_schools)] if include_french else f'School{i}'

                writer.writerow([
                    i + 1,
                    name,
                    f'Prénom{i}' if include_french else f'FirstName{i}',
                    subject,
                    school,
                    (i % 20) + 1,  # Grade 1-20
                    f'2023-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}'  # Random dates
                ])

        return temp_path

    def test_csv_validation_performance_1000_records(self):
        """Test CSV validation performance with 1000 records."""
        csv_path = self._create_large_csv_file(1000)

        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

        csv_source = self.CSVDataSource.create({
            'file_path': csv_path
        })
        csv_source._validate_csv_structure()

        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

        elapsed_time = end_time - start_time
        memory_used = end_memory - start_memory

        # Performance requirements: <2s processing, <10MB memory
        self.assertLess(elapsed_time, 2.0, f"CSV validation took {elapsed_time:.2f}s, should be <2s")
        self.assertLess(memory_used, 10.0, f"Memory usage {memory_used:.2f}MB, should be <10MB")

        # Verify validation succeeded
        self.assertEqual(csv_source.validation_status, 'valid')
        self.assertEqual(csv_source.record_count, 1000)

    def test_csv_validation_performance_5000_records(self):
        """Test CSV validation performance with 5000 records (stress test)."""
        csv_path = self._create_large_csv_file(5000)

        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

        csv_source = self.CSVDataSource.create({
            'file_path': csv_path
        })
        csv_source._validate_csv_structure()

        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

        elapsed_time = end_time - start_time
        memory_used = end_memory - start_memory

        # Relaxed requirements for larger dataset: <5s, <50MB
        self.assertLess(elapsed_time, 5.0, f"CSV validation took {elapsed_time:.2f}s, should be <5s")
        self.assertLess(memory_used, 50.0, f"Memory usage {memory_used:.2f}MB, should be <50MB")

        # Verify validation succeeded
        self.assertEqual(csv_source.validation_status, 'valid')
        self.assertEqual(csv_source.record_count, 5000)

    def test_french_character_encoding_performance(self):
        """Test performance with heavy French character usage."""
        csv_path = self._create_large_csv_file(1000, include_french=True)

        start_time = time.time()

        csv_source = self.CSVDataSource.create({
            'file_path': csv_path
        })

        # Test encoding detection performance
        encoding = csv_source._detect_encoding()
        self.assertEqual(encoding, 'utf-8')

        # Test validation with French characters
        csv_source._validate_csv_structure()
        csv_source.validate_french_characters()

        end_time = time.time()
        elapsed_time = end_time - start_time

        # Should handle French characters efficiently
        self.assertLess(elapsed_time, 3.0, f"French character processing took {elapsed_time:.2f}s")
        self.assertEqual(csv_source.validation_status, 'valid')

    def test_file_stats_computation_performance(self):
        """Test performance of file statistics computation."""
        csv_path = self._create_large_csv_file(2000)

        start_time = time.time()

        csv_source = self.CSVDataSource.create({
            'file_path': csv_path
        })
        csv_source._compute_file_stats()

        end_time = time.time()
        elapsed_time = end_time - start_time

        # File stats should be computed quickly
        self.assertLess(elapsed_time, 1.0, f"File stats computation took {elapsed_time:.2f}s")

        # Verify computed stats
        self.assertEqual(csv_source.record_count, 2000)
        self.assertTrue(csv_source.header_row)
        self.assertTrue(csv_source.last_modified)

    def test_concurrent_csv_validation(self):
        """Test performance with multiple CSV validations."""
        # Create multiple CSV files
        csv_paths = [
            self._create_large_csv_file(500),
            self._create_large_csv_file(750),
            self._create_large_csv_file(1000)
        ]

        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

        csv_sources = []
        for csv_path in csv_paths:
            csv_source = self.CSVDataSource.create({
                'file_path': csv_path
            })
            csv_source._validate_csv_structure()
            csv_sources.append(csv_source)

        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

        elapsed_time = end_time - start_time
        memory_used = end_memory - start_memory

        # Should handle multiple files efficiently
        self.assertLess(elapsed_time, 5.0, f"Concurrent validation took {elapsed_time:.2f}s")
        self.assertLess(memory_used, 25.0, f"Memory usage {memory_used:.2f}MB for concurrent processing")

        # Verify all validations succeeded
        for csv_source in csv_sources:
            self.assertEqual(csv_source.validation_status, 'valid')

    def test_large_file_size_handling(self):
        """Test handling of large file sizes (file system limits)."""
        # Create a very large CSV file (10MB+)
        csv_path = self._create_large_csv_file(50000)  # ~10MB file

        start_time = time.time()

        csv_source = self.CSVDataSource.create({
            'file_path': csv_path
        })

        # Should handle large files without memory issues
        csv_source._compute_file_stats()
        file_size = os.path.getsize(csv_path)

        end_time = time.time()
        elapsed_time = end_time - start_time

        # Should process large files in reasonable time
        self.assertLess(elapsed_time, 10.0, f"Large file processing took {elapsed_time:.2f}s")
        self.assertGreater(file_size, 5 * 1024 * 1024, "File should be at least 5MB")

        # Verify stats computation worked
        self.assertEqual(csv_source.record_count, 50000)

    def test_memory_usage_stability(self):
        """Test that memory usage remains stable across multiple operations."""
        csv_path = self._create_large_csv_file(1000)

        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_readings = []

        # Perform multiple validation cycles
        for i in range(10):
            csv_source = self.CSVDataSource.create({
                'file_path': csv_path
            })
            csv_source._validate_csv_structure()
            csv_source._compute_file_stats()

            current_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            memory_readings.append(current_memory - initial_memory)

        # Memory usage should remain stable (not continuously growing)
        max_memory = max(memory_readings)
        min_memory = min(memory_readings)
        memory_variance = max_memory - min_memory

        self.assertLess(memory_variance, 5.0, f"Memory variance {memory_variance:.2f}MB too high")
        self.assertLess(max_memory, 15.0, f"Peak memory usage {max_memory:.2f}MB too high")