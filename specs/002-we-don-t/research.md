# Research: CSV Binary Storage Enhancement

## Binary Field Implementation in Odoo Models

**Decision**: Use Odoo's `fields.Binary` with `attachment=True` parameter for CSV storage
**Rationale**:
- `attachment=True` stores binary data in `ir_attachment` table, optimizing PostgreSQL performance
- Provides automatic MIME type handling and metadata storage
- Integrates with Odoo's existing download mechanisms
- Supports large file handling without memory issues
**Alternatives considered**:
- Direct `fields.Binary` without attachment: Rejected due to PostgreSQL bytea limitations for large files
- Custom file storage: Rejected as it contradicts the requirement to move away from file system

## Download Controller Best Practices

**Decision**: Extend Odoo's existing `ir.http` download functionality with custom controller
**Rationale**:
- Leverages Odoo's built-in security and access control mechanisms
- Provides proper HTTP headers for CSV file downloads (Content-Type, Content-Disposition)
- Handles streaming for large files to prevent memory overload
- Maintains consistency with other Odoo file downloads
**Alternatives considered**:
- Direct binary field access in views: Rejected due to lack of proper HTTP headers and security
- Custom HTTP endpoint: Rejected as it bypasses Odoo's security framework

## Memory Optimization for Large CSV Files

**Decision**: Implement streaming downloads using `werkzeug.wsgi.FileWrapper` for large binary fields
**Rationale**:
- Prevents loading entire CSV file into memory during download
- Compatible with Odoo's WSGI architecture
- Provides better user experience for large datasets (1000+ records)
- Maintains server stability under concurrent download requests
**Alternatives considered**:
- Direct binary field serving: Rejected due to memory constraints with large files
- Chunked custom streaming: Rejected as Odoo already provides optimized mechanisms

## CSV Binary Field Storage Strategy

**Decision**: Store CSV content as UTF-8 encoded bytes in binary field with separate filename field
**Rationale**:
- UTF-8 encoding ensures French character compatibility
- Separate filename field allows proper Content-Disposition headers
- Binary storage includes automatic compression in PostgreSQL
- Maintains data integrity better than file system storage
**Alternatives considered**:
- Base64 encoding: Rejected due to 33% storage overhead
- Compressed binary storage: Rejected as PostgreSQL provides transparent compression

## Migration from File System to Binary Storage

**Decision**: Implement post-install hook with batch migration processing
**Rationale**:
- Ensures existing CSV data is not lost during addon upgrade
- Batch processing prevents memory issues with large datasets
- Post-install hook runs automatically during module upgrade
- Provides rollback capability if migration fails
**Alternatives considered**:
- Manual migration script: Rejected due to user complexity
- On-demand migration: Rejected as it would create inconsistent data states
- Background job migration: Rejected due to Odoo 16 job queue complexity

## Integration with Existing Export Report Model

**Decision**: Add binary fields to existing `export.report` model while maintaining backward compatibility
**Rationale**:
- Preserves existing report history and metadata
- Allows gradual migration from file-based to binary storage
- Maintains existing UI and user workflows
- Enables A/B testing of storage methods
**Alternatives considered**:
- New separate model: Rejected as it would fragment report history
- Complete model replacement: Rejected due to breaking change impact

## Access Control and Security

**Decision**: Leverage Odoo's existing `ir.model.access` and record rules for binary field access
**Rationale**:
- Maintains consistent security model with rest of application
- Provides granular permission control (read/write/create/delete)
- Integrates with existing user groups and roles
- Ensures CSV downloads respect organizational access policies
**Alternatives considered**:
- Custom permission system: Rejected as it would bypass Odoo security
- Public download links: Rejected due to security requirements