# Horizon CRLG to WBE - Business Migration Guide

**Document Version:** 1.0
**Date:** November 4, 2025
**Purpose:** Data owner review and validation of migration mappings

---

## Executive Summary

This document describes the data migration from **Horizon CRLG (source)** to **Horizon WBE (target)**. It details:
- What data will be migrated
- How data models correspond between systems
- Which fields match automatically
- Which fields need transformation
- What requires your review and approval

**Total Data Volume:** 112,263 records across 11 entity types

---

## 1. CONTACTS & PEOPLE (res.partner → res.partner)

### Overview
All contacts (students, teachers, staff, partners) will be migrated.

**Volume:** 2,115 contacts

### Automatic Field Mappings (No Changes)

These fields have the same name in both systems and will transfer directly:

| Field Purpose | Field Name |
|--------------|------------|
| Name | name |
| First name | firstname |
| Last name | lastname |
| Email | email |
| Phone | phone |
| Mobile | mobile |
| Street | street |
| Street 2 | street2 |
| City | city |
| ZIP code | zip |
| Country | country_id |
| State/Province | state_id |
| National registry number | national_register_number |
| Birth date | birthdate |
| Function/Title | function |
| Language | lang |
| Active status | active |
| Company | company_id |
| Parent contact | parent_id |
| VAT number | vat |
| Website | website |

**Plus 88 more technical and system fields**

### Field Name Changes (Automatic Mapping)

These fields exist in both systems but have different names. The migration will automatically map them:

| CRLG Field | WBE Field | Description | Example |
|------------|-----------|-------------|---------|
| `birthdate_date` | `birthdate` | Birth date | 1990-05-15 |
| `gender` | `genre` | Gender | Male/Female |
| `second_first_name` | `second_firstname` | Additional first name(s) | Marie |
| `secondary_city` | `sec_city` | Secondary address - city | Brussels |
| `secondary_country_id` | `sec_country_id` | Secondary address - country | Belgium |
| `secondary_state_id` | `sec_state_id` | Secondary address - state | Walloon Brabant |
| `secondary_street` | `sec_street` | Secondary address - street | Rue de la Paix |
| `secondary_street2` | `sec_street2` | Secondary address - street 2 | Apt 5 |
| `secondary_zip` | `sec_zip` | Secondary address - ZIP | 1348 |
| `student` | `is_student` | Is this person a student? | Yes/No |
| `teacher` | `is_teacher` | Is this person a teacher? | Yes/No |

### Fields Requiring Review

These fields exist in CRLG but **may not transfer exactly**. Please review:

**Medium Confidence Mappings (need validation):**

| CRLG Field | Suggested WBE Field | Question for Review |
|------------|---------------------|---------------------|
| `birth_state_id` | `state_id` | Should birth state map to general state field? |
| `birthcountry` | `country_id` or `birth_country_id` | Which field for birth country in WBE? |
| `email_personnel` | `email` | Should personal email go to main email field? |
| `lastname2` | `lastname` or `name` | How to handle second last name? |
| `official_document_ids` | `student_document_ids` | Are these the same type of documents? |
| `phone2` | `phone` | Should secondary phone map to main phone? |
| `registration_date` | `date` | Which date field in WBE? |

**Fields Not Yet Mapped (27 fields):**

The following CRLG fields don't have an obvious match in WBE:

- `access_titles_ids` - Access titles
- `admission_exam_date` - Admission exam date
- `age` - Age (may be computed in WBE)
- `birthplace` - Place of birth
- `erasmus_ids` - Erasmus programs
- `google_drive_*` - Google Drive integration fields
- `initials` - Person initials
- `internships_ids` - Internship information
- `memo` - Internal notes
- `teacher_current_course_ids` - Current courses taught
- `student_current_course_ids` - Current courses taken
- And 16 more technical fields

**❓ REVIEW NEEDED:** Should these fields be migrated? Are they still relevant in WBE?

---

## 2. ACADEMIC YEARS (school.year → gwr.academic.year)

### Overview
All academic year definitions will be migrated.

**Volume:** 39 academic years

### Automatic Field Mappings

| CRLG Field | WBE Field | Description |
|------------|-----------|-------------|
| `name` | `name` | Year name (e.g., "2023-2024") |

### Field Name Changes

| CRLG Field | WBE Field | Description | Example |
|------------|-----------|-------------|---------|
| `startdate` | `start_date` | Academic year start date | 2023-09-01 |
| `enddate` | `end_date` | Academic year end date | 2024-06-30 |

### Fields Not Mapped

**Requiring Review:**

| CRLG Field | Description | Question |
|------------|-------------|----------|
| `calendar_id` | Default calendar | Does WBE use calendars differently? |
| `next` | Link to next year | Does WBE auto-calculate this? |
| `previous` | Link to previous year | Does WBE auto-calculate this? |
| `short_name` | Abbreviated name | Not in WBE, is it needed? |

**❓ REVIEW NEEDED:** Are calendar and year linkages handled differently in WBE?

---

## 3. PAE CYCLES (school.cycle → gwr.pae.cycle)

### Overview
Educational cycle definitions (Bachelor 1, Bachelor 2, Bachelor 3, Master, etc.)

**Volume:** 35 cycles

### Automatic Field Mappings

| CRLG Field | WBE Field | Description |
|------------|-----------|-------------|
| `name` | `name` | Cycle name |

### Fields Requiring Significant Review

**⚠️ WARNING:** This model has significant structural differences between CRLG and WBE.

**CRLG has these fields (not yet mapped):**
- `code` - Cycle code
- `type` - Cycle type
- `certification_profile` - Certification profile
- `grade` - Grade level
- `grade_code` - Grade code
- `required_credits` - Required ECTS credits
- `description` - Description
- `sequence` - Display order
- And 5 more fields

**❓ CRITICAL REVIEW NEEDED:**
- How do cycles work in WBE vs CRLG?
- Are the concepts equivalent?
- Which CRLG fields map to WBE fields?

---

## 4. COURSES / LEARNING ACTIVITIES (school.course → gwr.learning.activity)

### Overview
Individual course/learning activity definitions.

**Volume:** 4,424 courses

### Automatic Field Mappings (14 exact matches)

| Field Purpose |
|--------------|
| Name |
| Active status |
| Description |
| Hours |
| Credits |
| Objectives |
| All messaging/mail tracking fields |

### Field Name Changes

| CRLG Field | WBE Field | Description |
|------------|-----------|-------------|
| `responsible_id` | `responsible_teacher_id` | Main responsible teacher |
| `teacher_ids` | `teachers_ids` | List of teachers |

### Fields Possibly Requiring Mapping (Review Recommended)

| CRLG Field | Suggested WBE Field | Question |
|------------|---------------------|----------|
| `course_type` | `weighting_type` | Are these the same concept? |
| `sequence` | `sequence_order` | Display order |
| `weight` | `weighting` | Course weight/importance |

### Fields Not Yet Mapped (20 fields)

Including:
- `bloc_ids` - Associated blocks
- `course_group_id` - Parent course group
- `cycle_id` - Associated cycle
- `course_organization` - Organization type
- `documentation_id` - Course documentation
- `exam_form` - Exam format
- `language` - Teaching language
- And 13 more fields

**❓ REVIEW NEEDED:** Which of these fields are still relevant in WBE?

---

## 5. COURSE GROUPS / TEACHING UNITS (school.course_group → gwr.teaching.unit)

### Overview
Groupings of courses into teaching units (UE - Unités d'Enseignement).

**Volume:** 3,441 course groups

### Automatic Field Mappings (14 exact matches)

Including name, code, active status, ECTS credits, description, etc.

### Fields Possibly Requiring Mapping (Review Recommended)

| CRLG Field | Suggested WBE Field | Question |
|------------|---------------------|----------|
| `sequence` | `sequence_order` | Display order |
| `total_hours_to_select` | `total_hours` | Total hours |
| `type` | `weighting_type` | Grouping type |

### Fields Not Mapped (28 fields)

**❓ REVIEW NEEDED:** Many fields related to course relationships, prerequisites, and groupings need review.

---

## 6. PROGRAMS / PEDAGOGICAL OFFERS (school.program → gwr.pedagogical.offer)

### Overview
Academic programs and pedagogical offerings.

**Volume:** 1,659 programs

### Automatic Field Mappings (12 exact matches)

Including name, code, active status, description, domain, section, speciality, cycle, etc.

### Field Name Changes

| CRLG Field | WBE Field | Description |
|------------|-----------|-------------|
| `is_second_cycle` | `second_cycle` | Is this a second cycle program? |

### Fields Not Yet Mapped (30 fields)

**❓ REVIEW NEEDED:** Many program-specific fields need validation.

---

## 7. STUDENT REGISTRATIONS (school.registration → gwr.registration)

### Overview
Student registration records.

**Volume:** 845 registrations

### Automatic Field Mappings (13 exact matches)

Including partner (student), state, registration number, etc.

### Field Name Changes

| CRLG Field | WBE Field | Description |
|------------|-----------|-------------|
| `year_id` | `academic_year_id` | Academic year |

### Fields Not Yet Mapped (19 fields)

**❓ REVIEW NEEDED:** Registration workflow and status fields need review.

---

## 8. ANNUAL BLOCKS (school.bloc → gwr.annual.block)

### Overview
Annual block definitions (year programs).

**Volume:** 5,210 blocks

### Automatic Field Mappings

| CRLG Field | WBE Field | Description |
|------------|-----------|-------------|
| `name` | `name` | Block name |
| `total_hours` | `total_hours` | Total hours |

### Field Possibly Requiring Mapping

| CRLG Field | Suggested WBE Field | Question |
|------------|---------------------|----------|
| `year_id` | `academic_year_id` | Academic year |

### Fields Not Yet Mapped (28 fields)

**⚠️ WARNING:** This model has significant differences. Most fields don't have obvious matches.

**❓ CRITICAL REVIEW NEEDED:** How do annual blocks work in WBE vs CRLG?

---

## 9. INDIVIDUAL PAE (school.individual_bloc → gwr.pae)

### Overview
Individual student annual programs (PAE - Programme Annuel d'Etudes).

**Volume:** 4,381 individual PAEs

### Automatic Field Mappings (20 exact matches)

Including student, state, year, total credits, various activity tracking fields.

### Field Name Changes

| CRLG Field | WBE Field | Description |
|------------|-----------|-------------|
| `year_id` | `academic_year_id` | Academic year |

### Fields Not Yet Mapped (35 fields)

**❓ REVIEW NEEDED:** Many PAE-specific workflow and approval fields need review.

---

## 10. INDIVIDUAL COURSES / PAE LEARNING ACTIVITIES (school.individual_course → gwr.pae.learning.activity)

### Overview
Individual course enrollments within student PAEs.

**Volume:** 48,006 individual course records (LARGEST TABLE)

### Automatic Field Mappings (26 exact matches)

Including basic enrollment information, results, credits, etc.

### Fields Possibly Requiring Mapping (8 fields need review)

Session and result fields may need special attention:
- `first_session_result` - First session result
- `first_session_result_bool` - First session pass/fail
- `second_session_result` - Second session result
- `second_session_result_bool` - Second session pass/fail
- `teacher_choice_id` - Teacher assignment
- `type` - Course type
- `weight` - Course weight
- `year_id` - Academic year

**❓ REVIEW NEEDED:** How do session results map between systems?

### Fields Not Yet Mapped (42 fields)

**⚠️ WARNING:** Many fields related to:
- Exam sessions and results
- Course approval workflow
- Dispensations and exemptions
- Prerequisites and corequisites

**❓ CRITICAL REVIEW NEEDED:** This is the largest table. Ensure result and session logic is correctly mapped.

---

## 11. INDIVIDUAL COURSE GROUPS / PAE TEACHING UNITS (school.individual_course_group → gwr.pae.teaching.unit)

### Overview
Individual enrollments in teaching unit groups within PAEs.

**Volume:** 42,108 records (SECOND LARGEST TABLE)

### Automatic Field Mappings (14 exact matches)

### Field Name Changes

| CRLG Field | WBE Field | Description |
|------------|-----------|-------------|
| `year_id` | `academic_year_id` | Academic year |

### Fields Not Yet Mapped (42 fields)

Similar issues as individual courses - session results, workflows, etc.

**❓ CRITICAL REVIEW NEEDED:** Same concerns as individual courses.

---

## 12. STUDENT DOCUMENTS (school.official_document → gwr.res.partner.student.document)

### Overview
Official documents associated with students.

**Volume:** 74 documents

### Automatic Field Mappings

Only 1 exact match: `name`

### Fields Not Yet Mapped (20 fields)

**⚠️ WARNING:** This model has very different structure between systems.

**CRLG fields not mapped:**
- `partner_id` - Associated student
- `type_id` - Document type
- `date` - Document date
- `file` - Document file
- `state` - Document state
- And 15 more fields

**❓ CRITICAL REVIEW NEEDED:**
- How do documents work in WBE?
- Are the concepts equivalent?
- This may need custom migration logic.

---

## SUMMARY TABLE: Migration Readiness

| Entity | Volume | Exact Matches | Renamed Fields | Unmapped Fields | Status |
|--------|--------|---------------|----------------|-----------------|--------|
| Contacts (res.partner) | 2,115 | 107 | 11 | 27 | 🟢 Ready (review medium confidence) |
| Academic Years | 39 | 1 | 2 | 3 | 🟢 Ready (minor review) |
| Courses | 4,424 | 14 | 2 | 20 | 🟡 Review recommended |
| Course Groups | 3,441 | 14 | 0 | 28 | 🟡 Review recommended |
| Individual Courses | 48,006 | 26 | 0 | 42 | 🔴 Critical review needed |
| Individual Course Groups | 42,108 | 14 | 1 | 42 | 🔴 Critical review needed |
| Programs | 1,659 | 12 | 1 | 30 | 🟡 Review recommended |
| Registrations | 845 | 13 | 1 | 19 | 🟡 Review recommended |
| Individual PAE | 4,381 | 20 | 1 | 35 | 🟡 Review recommended |
| PAE Cycles | 35 | 1 | 0 | 12 | 🔴 Critical review needed |
| Annual Blocks | 5,210 | 2 | 0 | 28 | 🔴 Critical review needed |
| Student Documents | 74 | 1 | 0 | 20 | 🔴 Critical review needed |

---

## REVIEW CHECKLIST FOR DATA OWNERS

### High Priority Review Items

1. **Individual Courses (48,006 records)**
   - ❏ Verify session result fields mapping
   - ❏ Confirm exam session logic
   - ❏ Review dispensation/exemption handling

2. **Individual Course Groups (42,108 records)**
   - ❏ Same as individual courses

3. **Contacts Secondary Address**
   - ✅ Confirmed: `secondary_*` → `sec_*` mapping is correct

4. **Academic Year Dates**
   - ✅ Confirmed: `startdate` → `start_date`, `enddate` → `end_date`

### Medium Priority Review Items

5. **PAE Cycles**
   - ❏ Confirm cycle structure equivalence
   - ❏ Map remaining fields

6. **Annual Blocks**
   - ❏ Confirm block concept equivalence
   - ❏ Identify field mappings

7. **Student Documents**
   - ❏ Confirm document model equivalence
   - ❏ May need custom migration

8. **Contacts - Birth Information**
   - ❏ Decide: `birthcountry` → `country_id` or `birth_country_id`?
   - ❏ Decide: `birth_state_id` → `state_id`?

9. **Contacts - Email**
   - ❏ Decide: `email_personnel` → `email`?

10. **Contacts - Unmapped Fields**
    - ❏ Review 27 unmapped fields
    - ❏ Determine which are still needed

---

## NEXT STEPS

### For Data Owners:

1. **Review this document** section by section
2. **Answer the "REVIEW NEEDED" questions** for each entity
3. **Prioritize** the high-priority review items
4. **Validate** the suggested field mappings
5. **Identify** any missing mappings that are critical
6. **Approve** or request changes to the migration plan

### For Technical Team:

1. Wait for data owner feedback
2. Update field mappings based on feedback
3. Create custom transformation logic where needed
4. Run test migrations on small datasets
5. Validate results with data owners
6. Proceed with full migration

---

## CONTACT FOR QUESTIONS

For questions about this migration plan:
- Technical questions: Development team
- Business questions: Data owners
- Field mapping validation: Subject matter experts

---

## APPENDIX: Detailed Field Lists

Complete field lists are available in:
- `field_analysis/SOURCE_*_fields.json` - All CRLG fields with descriptions
- `field_analysis/TARGET_*_fields.json` - All WBE fields with descriptions
- `field_analysis/FIELD_MAPPINGS_CODE.py` - Complete mapping analysis

---

**Document End** - Ready for data owner review and approval
