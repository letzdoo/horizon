# Tasks: School Export Reports Addon

**Input**: Design documents from `/home/js/horizon/specs/001-i-want-you/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Odoo addon structure**: `school_export_reports/` at repository root
- Paths follow OCA addon conventions with models/, reports/, views/, tests/

## Phase 3.1: Setup
- [x] T001 Create Odoo addon directory structure at school_export_reports/
- [x] T002 Create __manifest__.py with dependencies on school_management and report_xlsx
- [x] T003 [P] Create README.rst file with installation and usage instructions
- [x] T004 [P] Create security/ir.model.access.csv with model access permissions

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [x] T005 [P] Contract test for generate_programs_report in school_export_reports/tests/test_contract_programs.py
- [x] T006 [P] Contract test for generate_students_report in school_export_reports/tests/test_contract_students.py
- [x] T007 [P] Contract test for generate_teachers_report in school_export_reports/tests/test_contract_teachers.py
- [x] T008 [P] Contract test for generate_blocs_report in school_export_reports/tests/test_contract_blocs.py
- [x] T009 [P] Integration test for CSV validation in school_export_reports/tests/test_csv_validation.py
- [x] T010 [P] Integration test for French character handling in school_export_reports/tests/test_french_chars.py
- [x] T011 [P] Integration test for error handling in school_export_reports/tests/test_error_handling.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [x] T012 [P] ExportReport model in school_export_reports/models/export_report.py
- [x] T013 [P] ReportType model in school_export_reports/models/report_type.py
- [x] T014 [P] CSVDataSource model in school_export_reports/models/csv_data_source.py
- [x] T015 Create models __init__.py importing all models in school_export_reports/models/__init__.py
- [x] T016 Programs report class in school_export_reports/reports/programs_report.py
- [x] T017 Students report class in school_export_reports/reports/students_report.py
- [x] T018 Teachers report class in school_export_reports/reports/teachers_report.py
- [x] T019 Blocs report class in school_export_reports/reports/blocs_report.py
- [x] T020 Create reports __init__.py importing all report classes in school_export_reports/reports/__init__.py
- [x] T021 CSV validator utility class in school_export_reports/utils/csv_validator.py
- [x] T022 Excel formatter utility class in school_export_reports/utils/excel_formatter.py

## Phase 3.4: Integration
- [x] T023 Report data XML definitions in school_export_reports/data/ir_actions_report.xml
- [x] T024 Menu actions XML for each report type in school_export_reports/views/school_export_reports_menu.xml
- [x] T025 Form views for report generation in school_export_reports/views/export_report_views.xml
- [x] T026 List views for report history in school_export_reports/views/export_report_views.xml
- [x] T027 Wizard forms for report parameters in school_export_reports/wizard/report_wizard.py
- [x] T028 Error handling integration across all report classes
- [x] T029 Logging integration for audit trail in all report operations

## Phase 3.5: Polish
- [x] T030 [P] Unit tests for ExportReport model in school_export_reports/tests/test_export_report_model.py
- [x] T031 [P] Unit tests for CSV validation logic in school_export_reports/tests/test_csv_validator_unit.py
- [x] T032 [P] Unit tests for Excel formatting in school_export_reports/tests/test_excel_formatter_unit.py
- [x] T033 [P] Performance tests for large CSV files (1000+ records) in school_export_reports/tests/test_performance.py
- [x] T034 [P] Update README.rst with complete documentation
- [x] T035 [P] Add demo data in school_export_reports/demo/demo_reports.xml
- [x] T036 Clean up duplicate code across report classes
- [x] T037 Run quickstart.md validation tests manually

## Dependencies
**Setup Phase**: T001-T004 must complete first
**Tests Phase**: T005-T011 before any implementation (TDD)
**Models Phase**: T012-T015 before reports (T016-T020)
**Reports Phase**: T016-T020 before integration (T023-T029)
**Integration Phase**: T023-T029 before polish (T030-T037)

**Specific Dependencies**:
- T015 blocks T020 (requires all models)
- T016-T019 block T028 (error handling needs all report classes)
- T021-T022 block T031-T032 (unit tests need utility classes)
- T023-T026 must complete before T027 (wizard needs menu structure)

## Parallel Example
```
# Launch initial setup tasks (T001-T004):
Task: "Create Odoo addon directory structure at school_export_reports/"
Task: "Create __manifest__.py with dependencies on school_management and report_xlsx"
Task: "Create README.rst file with installation and usage instructions"
Task: "Create security/ir.model.access.csv with model access permissions"

# Launch contract tests together (T005-T008):
Task: "Contract test for generate_programs_report in school_export_reports/tests/test_contract_programs.py"
Task: "Contract test for generate_students_report in school_export_reports/tests/test_contract_students.py"
Task: "Contract test for generate_teachers_report in school_export_reports/tests/test_contract_teachers.py"
Task: "Contract test for generate_blocs_report in school_export_reports/tests/test_contract_blocs.py"

# Launch model tasks (T012-T014):
Task: "ExportReport model in school_export_reports/models/export_report.py"
Task: "ReportType model in school_export_reports/models/report_type.py"
Task: "CSVDataSource model in school_export_reports/models/csv_data_source.py"
```

## Validation Checklist
*GATE: Checked during task generation*

- [x] All contracts have corresponding tests (T005-T008)
- [x] All entities have model tasks (T012-T014)
- [x] All tests come before implementation (T005-T011 before T012+)
- [x] Parallel tasks truly independent (different files)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Follow OCA conventions throughout
- Ensure French character support in all implementations
- Implement fail-fast error handling per constitution requirements
- Target <2s generation time and <10MB memory usage