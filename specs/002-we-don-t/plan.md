# Implementation Plan: CSV Binary Storage Enhancement

**Branch**: `002-we-don-t` | **Date**: 2025-09-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/home/js/horizon/specs/002-we-don-t/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 8. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Enhance the existing school_export_reports Odoo addon to store CSV export data as binary fields within database records instead of file system files. Users will download CSV files through Odoo's standard web interface, improving data security, backup integration, and user experience consistency.

## Technical Context
**Language/Version**: Python 3.11 (Odoo 16 requirement)
**Primary Dependencies**: Odoo 16, school_export_reports (existing), xlsxwriter
**Storage**: PostgreSQL (Odoo database) with binary fields for CSV data
**Testing**: Odoo test framework, unittest
**Target Platform**: Linux server (Odoo deployment)
**Project Type**: single (Odoo addon enhancement)
**Performance Goals**: <2s CSV generation and storage, <10MB memory usage per operation
**Constraints**: OCA addon standards, existing functionality preservation, fail-fast error handling
**Scale/Scope**: School-scale data (1000+ students, 4 CSV export types), binary field storage optimization

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**OCA Standards Compliance**: ✅ PASS - Enhancement to existing OCA-compliant module, maintains standards
**Module Architecture**: ✅ PASS - Modifies existing school_export_reports module, clear dependencies
**Semantic Versioning**: ✅ PASS - Minor version bump (adds binary storage without breaking changes)
**Code Quality Gates**: ✅ PASS - Will include unit tests, maintain existing test coverage
**Fail-Fast Development**: ✅ PASS - Enhanced error handling for binary field operations

## Project Structure

### Documentation (this feature)
```
specs/002-we-don-t/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Existing Odoo addon structure (enhanced)
school_export_reports/
├── models/
│   ├── export_report.py      # Enhanced with binary fields
│   ├── csv_data_source.py    # Modified for binary storage
│   └── report_type.py        # Configuration updates
├── views/
│   ├── export_report_views.xml  # Enhanced with download links
│   └── school_export_reports_menu.xml
├── controllers/              # NEW - Binary file downloads
│   └── download_controller.py
├── tests/
│   ├── test_binary_storage.py   # NEW - Binary field tests
│   └── [existing test files]    # Enhanced
└── __manifest__.py           # Version bump, dependencies
```

**Structure Decision**: Single project (Odoo addon enhancement)

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - Binary field implementation patterns in Odoo
   - Download controller best practices
   - Memory optimization for large CSV files
   - Migration strategy from file to binary storage

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research Odoo binary field storage patterns for CSV data"
     Task: "Find best practices for file download controllers in Odoo"
     Task: "Research memory optimization for large binary fields"
     Task: "Find migration patterns from file storage to binary fields"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Enhanced ExportReport with binary CSV field and filename
   - Download access control mechanisms
   - Migration data structures

2. **Generate API contracts** from functional requirements:
   - Binary field storage API patterns
   - Download endpoint contracts
   - Error handling for binary operations
   - Output OpenAPI schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - Binary storage operation tests
   - Download functionality tests
   - File size and memory constraint tests
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - CSV binary storage scenarios
   - Download interface scenarios
   - Migration from file system scenarios
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh claude`
   - Add binary field storage patterns
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load existing school_export_reports structure
- Generate enhancement tasks from Phase 1 design docs
- Binary field model modifications → model update tasks [P]
- Download controller → new controller tasks
- View enhancements → UI update tasks [P]
- Migration logic → data migration tasks
- Test updates → test enhancement tasks [P]

**Ordering Strategy**:
- TDD order: Enhanced tests before implementation
- Dependency order: Models before controllers before views
- Migration tasks after core implementation
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 15-20 numbered, ordered enhancement tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

**Specific Task Planning for CSV Binary Enhancement**:
- Load existing models → Enhance with binary fields and download methods
- Load existing views → Add download links and binary field displays
- Create new controller → Binary file download handling
- Create migration → File system to binary field data transfer
- Enhance tests → Binary storage and download functionality validation

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [ ] Phase 0: Research complete (/plan command)
- [ ] Phase 1: Design complete (/plan command)
- [ ] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [ ] Post-Design Constitution Check: PASS
- [ ] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*