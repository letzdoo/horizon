========================
School Export Reports
========================

.. |badge1| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

|badge1|

This module generates Excel reports from existing CSV export files in educational management systems.

**Table of contents**

.. contents::
   :local:

Features
========

* Generate Excel reports from 4 CSV export types:

  * school_programs.csv → Educational Programs Report
  * school_students.csv → Students Report
  * school_teachers.csv → Teachers Report
  * school_blocs.csv → Academic Blocs Report

* CSV file validation with detailed error reporting
* French character support (UTF-8 encoding)
* Report generation history and audit trail
* Integrated menu actions for each report type
* Fail-fast error handling for missing or invalid files

Installation
============

Prerequisites
-------------

1. Odoo 16 instance running
2. school_management module installed
3. report_xlsx module installed
4. Python xlsxwriter library::

    pip install xlsxwriter

Module Installation
-------------------

1. Copy this module to your Odoo addons directory
2. Update the module list: Apps → Update Apps List
3. Search for "School Export Reports" and install

Configuration
=============

CSV File Setup
---------------

Ensure the following CSV files exist in your export directory:

* school_programs.csv
* school_students.csv
* school_teachers.csv
* school_blocs.csv

All CSV files must be UTF-8 encoded to support French characters.

Usage
=====

Generating Reports
------------------

1. Navigate to School → Reports → Export Reports
2. Select the desired report type:

   * Generate Programs Report
   * Generate Students Report
   * Generate Teachers Report
   * Generate Blocs Report

3. Click "Generate Report" button
4. The system will validate the CSV file and generate an Excel report
5. Download the generated Excel file

Viewing Report History
----------------------

1. Go to School → Reports → Export Reports → Export Reports
2. View list of all generated reports with:

   * Generation timestamps
   * Record counts processed
   * Success/error status
   * File sizes

Error Handling
--------------

The module implements fail-fast error handling:

* **Missing CSV File**: Clear error message with filename
* **Invalid CSV Structure**: Detailed validation errors
* **Encoding Issues**: UTF-8 validation and error reporting
* **Generation Failures**: Technical error details preserved

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/education/issues>`_.

Credits
=======

Authors
~~~~~~~

* School Management Team

Contributors
~~~~~~~~~~~~

* Development Team

Maintainers
~~~~~~~~~~~

This module is maintained by the School Management Team.

Performance Specifications
===========================

The module is designed to handle school-scale data efficiently:

* **Processing Speed**: <2 seconds for Excel generation with 1000+ records
* **Memory Usage**: <10MB memory consumption during report generation
* **File Size Support**: Handles CSV files up to 10MB efficiently
* **Concurrent Operations**: Supports multiple report generations simultaneously

Technical Implementation
========================

Architecture
~~~~~~~~~~~~

The module follows OCA conventions with a clean separation of concerns:

* **Models**: Core data models for report tracking and CSV management
* **Reports**: Excel generation classes with French character support
* **Utils**: Reusable validation and formatting utilities
* **Views**: Complete UI integration with Odoo interface
* **Tests**: Comprehensive test coverage (contract, integration, unit, performance)

French Language Support
~~~~~~~~~~~~~~~~~~~~~~~

Special attention to French educational terminology:

* UTF-8 encoding throughout the system
* Automatic detection and handling of accented characters (é, è, à, ç, etc.)
* Specialized Excel formatting for French text content
* French-specific validation patterns

Error Handling Strategy
~~~~~~~~~~~~~~~~~~~~~~~

Implements fail-fast approach as per constitutional requirements:

* **Missing Files**: Immediate error with clear filename identification
* **Invalid Structure**: Detailed validation error messages
* **Encoding Issues**: Automatic detection with fallback strategies
* **Generation Failures**: Complete error context preservation
* **Immutable Records**: Error reports cannot be modified once created

Test Coverage
~~~~~~~~~~~~~

Comprehensive test suite ensuring reliability:

* **Contract Tests**: Validate API endpoints match OpenAPI specifications
* **Integration Tests**: End-to-end CSV processing and error handling
* **Unit Tests**: Individual component testing with mocking
* **Performance Tests**: Validate speed and memory requirements
* **French Character Tests**: Specific encoding and display validation

Development Standards
~~~~~~~~~~~~~~~~~~~~

Code follows strict quality standards:

* **PEP8 Compliance**: All Python code formatted to standard
* **Type Hinting**: Where applicable for better code documentation
* **Logging Integration**: Comprehensive audit trail for operations
* **Security Practices**: No secrets or credentials in codebase
* **Documentation**: Complete inline documentation and README

Migration Path
==============

From school_reporting_xlsx
~~~~~~~~~~~~~~~~~~~~~~~~~~~

If migrating from the existing school_reporting_xlsx module:

1. **Backup Data**: Export existing report configurations
2. **Install Dependencies**: Ensure report_xlsx module is available
3. **CSV Files**: Prepare CSV export files in /export directory
4. **Install Module**: Follow standard installation procedure
5. **Test Generation**: Verify all report types work correctly
6. **User Training**: Brief users on new menu structure

Future Enhancements
==================

Planned improvements (not included in current scope):

* **Scheduled Reports**: Automatic generation at specified intervals
* **Email Distribution**: Send generated reports via email
* **Template Customization**: User-defined Excel formatting options
* **Advanced Filtering**: Date ranges and data subset selection
* **Dashboard Integration**: Report statistics in main dashboard

For feature requests, please use the GitHub Issues tracker.