# Data Model: School Export Reports Addon

## Core Entities

### ExportReport
**Purpose**: Represents a generated Excel report based on CSV export data
**Fields**:
- name: Report display name (string, required)
- report_type: Type of report (selection: programs/students/teachers/blocs, required)
- csv_source_path: Path to source CSV file (string, required)
- generation_timestamp: When report was generated (datetime, auto)
- file_size_bytes: Size of generated Excel file (integer, computed)
- record_count: Number of records processed (integer, computed)
- status: Report generation status (selection: pending/success/error, default=pending)
- error_message: Error details if generation failed (text, optional)

**Validation Rules**:
- csv_source_path must exist and be readable
- report_type must match available CSV files
- file_size_bytes must be > 0 for successful reports
- error_message required when status = 'error'

**State Transitions**:
- pending → success (when Excel generated successfully)
- pending → error (when validation or generation fails)
- No transitions from success/error states (immutable records)

### ReportType
**Purpose**: Defines configuration for each report category
**Fields**:
- code: Technical identifier (string, required, unique)
- name: Display name for users (string, required)
- csv_filename: Expected CSV filename (string, required)
- excel_template: Excel formatting configuration (text, JSON format)
- column_mappings: CSV to Excel column mappings (text, JSON format)
- validation_rules: Data validation requirements (text, JSON format)
- menu_sequence: Order in menu display (integer, default=10)

**Predefined Records**:
- programs: school_programs.csv → "Educational Programs Report"
- students: school_students.csv → "Students Report"
- teachers: school_teachers.csv → "Teachers Report"
- blocs: school_blocs.csv → "Academic Blocs Report"

### CSVDataSource
**Purpose**: Handles CSV file access and validation
**Fields**:
- file_path: Full path to CSV file (string, required)
- last_modified: File modification timestamp (datetime, computed)
- header_row: CSV column headers (text, computed)
- record_count: Number of data rows (integer, computed)
- encoding: File character encoding (string, default='utf-8')
- validation_status: File integrity status (selection: valid/invalid/missing)
- validation_errors: List of validation issues (text, optional)

**Computed Methods**:
- _compute_file_stats(): Updates file metadata and record count
- _validate_csv_structure(): Checks headers and data integrity
- _detect_encoding(): Determines file character encoding

## Entity Relationships

```
ReportType (1) ----→ (N) ExportReport
    ↓
CSVDataSource (1) ----→ (N) ExportReport
```

**Relationship Rules**:
- Each ExportReport references exactly one ReportType
- Each ExportReport references exactly one CSVDataSource
- ReportType defines configuration for CSV processing
- CSVDataSource provides actual data file access

## Data Flow

1. **Report Request**: User selects report type from menu
2. **Validation**: System validates corresponding CSV file exists and is readable
3. **Data Loading**: CSVDataSource reads and validates file structure
4. **Report Generation**: ExportReport created with processing status
5. **Excel Creation**: Report processor generates Excel using ReportType configuration
6. **Status Update**: ExportReport status updated (success/error)
7. **File Download**: Generated Excel file provided to user

## Error Handling

**Missing CSV File**:
- CSVDataSource.validation_status = 'missing'
- ExportReport.status = 'error'
- ExportReport.error_message = "CSV file not found: {filename}"

**Invalid CSV Structure**:
- CSVDataSource.validation_status = 'invalid'
- Detailed validation_errors captured
- Report generation blocked with specific error message

**Excel Generation Failure**:
- ExportReport.status = 'error'
- Technical error details in error_message
- Original CSV file remains untouched

## Performance Considerations

**File Access**: CSV files read once per report generation, cached in memory
**Record Limits**: Support up to 10,000 records per CSV file (school-scale)
**Memory Usage**: Process CSV in chunks for large files (>1MB)
**Concurrent Access**: File locks prevent concurrent access to same CSV file