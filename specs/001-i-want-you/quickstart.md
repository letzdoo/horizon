# Quickstart: School Export Reports Addon

## Prerequisites
1. Odoo 16 instance running
2. school_management module installed
3. report_xlsx module installed
4. CSV export files present in export directory:
   - school_programs.csv
   - school_students.csv
   - school_teachers.csv
   - school_blocs.csv

## Installation Steps
1. **Clone addon to addons directory**:
   ```bash
   cd /path/to/odoo/addons
   git clone school_export_reports
   ```

2. **Install dependencies**:
   ```bash
   pip install xlsxwriter
   ```

3. **Update module list in Odoo**:
   - Go to Apps → Update Apps List
   - Search for "School Export Reports"
   - Click Install

## Basic Usage Test

### Test 1: Generate Programs Report
1. **Navigate to Reports menu**:
   - Go to School → Reports → Export Reports
   - Click "Generate Programs Report"

2. **Expected behavior**:
   - Form opens for report generation
   - Click "Generate Report" button
   - System validates school_programs.csv exists
   - Excel file generated and downloaded

3. **Verify results**:
   - Excel file contains all program data from CSV
   - French characters display correctly
   - Column headers match CSV structure
   - File size > 0 bytes

### Test 2: Handle Missing CSV File
1. **Temporarily rename CSV file**:
   ```bash
   mv export/school_students.csv export/school_students.csv.bak
   ```

2. **Attempt report generation**:
   - Go to School → Reports → Export Reports
   - Click "Generate Students Report"
   - Click "Generate Report" button

3. **Expected behavior**:
   - Error message displayed: "CSV file not found: school_students.csv"
   - No Excel file generated
   - Report status = 'error' in database

4. **Restore file**:
   ```bash
   mv export/school_students.csv.bak export/school_students.csv
   ```

### Test 3: Validate All Report Types
1. **Generate each report type**:
   - Programs Report (school_programs.csv)
   - Students Report (school_students.csv)
   - Teachers Report (school_teachers.csv)
   - Blocs Report (school_blocs.csv)

2. **Verify each generates successfully**:
   - All CSV files processed
   - Excel files downloaded
   - No error messages
   - French characters preserved

### Test 4: Check Report History
1. **View generated reports**:
   - Go to School → Reports → Export Reports → Export Reports
   - List view shows all generated reports

2. **Verify report metadata**:
   - Generation timestamps accurate
   - Record counts match CSV row counts
   - Status shows 'success' for valid reports
   - File sizes > 0 for successful reports

## Validation Checklist

### Functional Requirements Validation
- [ ] **FR-001**: Excel reports generated from all 4 CSV files
- [ ] **FR-002**: All CSV data fields preserved in Excel output
- [ ] **FR-003**: Separate menu actions for each report type visible
- [ ] **FR-004**: French educational terminology displayed correctly
- [ ] **FR-005**: CSV validation prevents processing invalid files
- [ ] **FR-006**: Report generation logged in database
- [ ] **FR-007**: Download functionality works for Excel files
- [ ] **FR-008**: OCA addon structure followed
- [ ] **FR-009**: Dependencies on school_management and report_xlsx working
- [ ] **FR-010**: Missing CSV files handled with clear error messages

### User Story Validation
- [ ] **Story 1**: Administrator can see export-based report options in menu
- [ ] **Story 2**: Programs report generates Excel with proper formatting
- [ ] **Story 3**: Multiple report types can be generated independently
- [ ] **Story 4**: Missing/corrupted CSV files display clear error messages

### Performance Validation
- [ ] Excel generation completes in <2 seconds for 1000 records
- [ ] Memory usage remains <10MB during report generation
- [ ] French characters handled correctly in all outputs
- [ ] File sizes appropriate for data volume

## Troubleshooting

### Common Issues

**Issue**: "Module not found" error during installation
**Solution**: Ensure addon is in correct addons directory and restart Odoo

**Issue**: "CSV file not found" error with existing files
**Solution**: Check file permissions and absolute path configuration

**Issue**: French characters display as "?" in Excel
**Solution**: Verify UTF-8 encoding in CSV files and Excel generation

**Issue**: Excel file size 0 bytes
**Solution**: Check CSV file content and validation error messages

### Log Locations
- Odoo server logs: `/var/log/odoo/odoo.log`
- Report generation errors: Database table `export_report.error_message`
- CSV validation issues: Database table `csv_data_source.validation_errors`

## Next Steps
After successful quickstart validation:
1. Run full test suite: `python -m pytest tests/`
2. Review generated Excel files for data accuracy
3. Test with production-scale CSV files
4. Configure automated report scheduling (optional)
5. Set up user permissions for report access