# SKILLY Module 04 — College / TPO Design Specification

## 1. Scope

Module 04 establishes the **College & Placement Training Office (TPO) Operations Platform**, providing institutional administrators, TPO coordinators, department heads, and faculty members with operational visibility, student progress tracking, placement drive coordination, and data-driven shortlisting.

### Core Included Workflows:
1. **College/TPO Dashboard & Institutional Analytics**:
   - Institutional overview metrics (Total Students, Department Count, Active Campus Drives, Placement Rate, Average Package, Top Skill Gaps).
   - Real-time aggregations from PostgreSQL (zero hardcoded/mock metrics).
2. **Institutional Department & Faculty Management**:
   - Department directory inspection and faculty list (`teachers`, `institution_staff`).
   - Staff role delegation (`TPO_ADMIN`, `TPO_COORDINATOR`, `DEPT_HEAD`).
3. **Batch Academic Performance & Skill-Gap Aggregations**:
   - Filter students by Batch (`enrollment_year`, `graduation_year`), Department (`department_id`), Semester (`current_semester`), and CGPA threshold.
   - Aggregate batch skill proficiencies and critical skill gaps from `student_skills` and `skill_gaps`.
4. **Campus Placement Drive Operations**:
   - View, create, and manage campus drives tied to company opportunities (`opportunities`, `placement_records`).
   - Track application stages (`APPLIED`, `SHORTLISTED`, `INTERVIEW_SCHEDULED`, `OFFERED`, `REJECTED`, `ACCEPTED`).
5. **Deterministic Student Eligibility Filtering & Shortlisting**:
   - Filter students deterministically based on minimum CGPA, specific department, zero active backlogs, target role alignment, and required skill proficiency.
   - Export / generate shortlisted candidate lists for campus drives.

---

## 2. Out of Scope

To prevent scope creep and maintain architectural boundaries, the following are explicitly **Out of Scope** for Module 04:
- Direct Company/Industry job posting creation (belongs to Module 06 — Industry/Company).
- Direct student assessment creation or grading (belongs to Module 03.5 / Module 05 — Teacher/Assessment).
- Modify student skill scores or student profile details directly from TPO portal (students own their profile updates).
- AI/LLM placement probability predictions (deterministic filtering rules are strictly used; AI recommendation services remain decoupled).
- Payment gateways, sponsorship management, or commercial billing for campus drives.

---

## 3. Existing Entity Reuse Matrix (47-Table DB Compliance)

Module 04 requires **ZERO Schema Changes**, **ZERO New Tables**, and **ZERO Migrations**. The entire design operates on the verified 47-table database architecture.

| Core Workflow | Primary Tables Used | Secondary / Relationship Tables | Entity Ownership |
| :--- | :--- | :--- | :--- |
| **Institutional Identity** | `institutions` | `user_profiles`, `users` | Institution Domain |
| **Department & Staff** | `departments`, `institution_staff`, `teachers` | `users` | Institution Domain |
| **Student Roster & Batch** | `students` | `user_profiles`, `users`, `departments` | Student Domain |
| **Skill & Gap Analytics** | `student_skills`, `skill_gaps` | `skills`, `career_roles` | Skill Domain |
| **Campus Drive & Opportunities** | `opportunities`, `opportunity_skills` | `companies` | Opportunity Domain |
| **Applications & Shortlists** | `applications`, `application_status_history` | `students`, `opportunities` | Application Domain |
| **Placement Records & Package**| `placement_records`, `placement_interactions` | `students`, `institutions` | Placement Domain |
| **Training Programs** | `training_programs`, `training_enrollments` | `institutions`, `students` | Training Domain |

---

## 4. Domain Ownership

Each domain retains a single canonical service layer to enforce single responsibility:

- **Auth & User Domain** (`app/services/auth_service.py`): User lookup, token verification, password security.
- **College/Institution Domain** (`app/services/college_service.py`): Institutional metrics, department lists, faculty roster, TPO staff access.
- **Student Analytics Domain** (`app/services/student_service.py`): Student profile queries, batch statistics, skill/gap aggregations.
- **Placement & Drive Domain** (`app/services/placement_service.py`): Opportunity shortlisting, campus drive management, application status transitions, placement statistics.

---

## 5. RBAC Matrix

| Endpoint Category | `STUDENT` | `COLLEGE_ADMIN` | `TEACHER` | `INDUSTRY` | `ALUMNI` |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `GET /api/v1/college/dashboard` | ❌ 403 | ✅ 200 (Own Institution) | ❌ 403 | ❌ 403 | ❌ 403 |
| `GET /api/v1/college/departments` | ❌ 403 | ✅ 200 (Own Institution) | ✅ 200 (Read Only) | ❌ 403 | ❌ 403 |
| `GET /api/v1/college/faculty` | ❌ 403 | ✅ 200 (Own Institution) | ✅ 200 (Read Only) | ❌ 403 | ❌ 403 |
| `GET /api/v1/college/students` | ❌ 403 | ✅ 200 (Own Institution) | ✅ 200 (Dept Scoped) | ❌ 403 | ❌ 403 |
| `GET /api/v1/college/analytics/skills` | ❌ 403 | ✅ 200 (Own Institution) | ✅ 200 (Dept Scoped) | ❌ 403 | ❌ 403 |
| `POST /api/v1/college/drives` | ❌ 403 | ✅ 200 (Own Institution) | ❌ 403 | ❌ 403 | ❌ 403 |
| `POST /api/v1/college/shortlist` | ❌ 403 | ✅ 200 (Own Institution) | ❌ 403 | ❌ 403 | ❌ 403 |

---

## 6. Institution Isolation Rules

1. **Database-Authoritative Access**:
   The user's `institution_id` is resolved by querying `institution_staff` or `teachers` table using `current_user.id`. Client-supplied `institution_id` parameters in query strings or request bodies are strictly rejected or ignored.
2. **Multi-Tenant Data Boundaries**:
   - `College Admin / TPO` can ONLY view or interact with students where `students.institution_id == staff.institution_id`.
   - `Teacher / Faculty` can ONLY view students where `students.institution_id == teacher.institution_id` and (if configured) `students.department_id == teacher.department_id`.
   - Placement drives and candidate shortlists are strictly scoped to the TPO's registered `institution_id`.

---

## 7. IDOR Threat Model

| Potential Attack Vector | Attack Description | Mitigation Mechanism |
| :--- | :--- | :--- |
| **Foreign Student Inspection** | TPO A attempts to query student details belonging to College B via `GET /api/v1/college/students/{student_id}` | Backend joins `students.institution_id == current_user_institution_id`. Returns `404 Not Found` if mismatch. |
| **Foreign Drive Shortlisting** | TPO A attempts to shortlist candidates for College B's drive via `POST /api/v1/college/drives/{drive_id}/shortlist` | Verifies `opportunity.institution_id == current_user_institution_id`. Rejects with `403 Forbidden` if unauthorized. |
| **Department Tampering** | TPO Admin attempts to assign staff to another college's department | Enforces `department.institution_id == current_user_institution_id` during all relational operations. |

---

## 8. Database Impact Analysis

- **Schema Alterations**: `NONE` (0 tables added, 0 columns modified, 0 migrations required).
- **Index Utilization**:
  - `idx_students_institution` on `students(institution_id)`
  - `idx_students_dept` on `students(institution_id, department_id)`
  - `fk_student_institution_dept` composite FK constraint
  - `idx_applications_opportunity` on `applications(opportunity_id)`
  - `idx_placement_records_student` on `placement_records(student_id)`
- **Query Efficiency**: Aggregations (`COUNT`, `AVG`, `GROUP BY`) leverage existing foreign key indexes for performant real-time analytics.

---

## 9. API Specification

### 1. `GET /api/v1/college/dashboard`
- **Purpose**: Fetch top-level institutional metrics & overview.
- **Authorization**: `COLLEGE_ADMIN`
- **Institution Rule**: Resolves `institution_id` via `institution_staff`.
- **Response Schema**:
  ```json
  {
    "institution_id": "uuid",
    "institution_name": "string",
    "total_students": 1250,
    "total_departments": 8,
    "active_drives": 12,
    "total_placements": 320,
    "placement_rate_percentage": 78.5,
    "average_package_lpa": 6.8,
    "highest_package_lpa": 24.0,
    "top_skill_gaps": [
      {"skill_name": "Docker", "student_count": 142},
      {"skill_name": "System Design", "student_count": 98}
    ]
  }
  ```

### 2. `GET /api/v1/college/departments`
- **Purpose**: List all academic departments under the institution.
- **Authorization**: `COLLEGE_ADMIN`, `TEACHER`
- **Response Schema**: List of departments with student count & faculty count.

### 3. `GET /api/v1/college/faculty`
- **Purpose**: Retrieve directory of teachers & staff members.
- **Authorization**: `COLLEGE_ADMIN`, `TEACHER`
- **Response Schema**: Faculty details, designations, and department affiliations.

### 4. `GET /api/v1/college/students`
- **Purpose**: Query institutional student roster with batch, semester, CGPA, and career role filters.
- **Authorization**: `COLLEGE_ADMIN`, `TEACHER`
- **Query Parameters**: `department_id`, `graduation_year`, `min_cgpa`, `current_semester`, `page`, `limit`
- **Response Schema**: Paginated list of student profiles, CGPA, and target career role.

### 5. `GET /api/v1/college/analytics/skills`
- **Purpose**: Aggregate batch skill proficiencies and identify critical department-wide skill gaps.
- **Authorization**: `COLLEGE_ADMIN`, `TEACHER`
- **Response Schema**: Skill frequency, proficiency distribution, and top gap severities.

### 6. `GET /api/v1/college/drives`
- **Purpose**: Fetch active and upcoming placement drives for the institution.
- **Authorization**: `COLLEGE_ADMIN`
- **Response Schema**: Drive details, posting company, stipend/salary, application counts.

### 7. `POST /api/v1/college/shortlist`
- **Purpose**: Deterministically filter and shortlist eligible students for a campus placement drive.
- **Authorization**: `COLLEGE_ADMIN`
- **Request Body**:
  ```json
  {
    "opportunity_id": "uuid",
    "min_cgpa": 7.5,
    "graduation_year": 2026,
    "department_ids": ["uuid-dept-1", "uuid-dept-2"],
    "required_skill_ids": ["uuid-skill-1"]
  }
  ```
- **Response Schema**:
  ```json
  {
    "opportunity_id": "uuid",
    "eligible_student_count": 45,
    "shortlisted_students": [
      {
        "student_id": "uuid",
        "name": "John Doe",
        "roll_number": "CS202601",
        "department": "Computer Science",
        "cgpa": 8.4,
        "matching_skills_count": 4
      }
    ]
  }
  ```

---

## 10. Backend Service Design

- **`CollegeService`** (`backend/app/services/college_service.py`):
  - `get_dashboard_metrics(db: AsyncSession, user_id: UUID) -> CollegeDashboardSchema`
  - `get_departments(db: AsyncSession, institution_id: UUID) -> List[DepartmentSchema]`
  - `get_faculty_directory(db: AsyncSession, institution_id: UUID) -> List[FacultySchema]`
- **`CollegeAnalyticsService`** (`backend/app/services/college_analytics_service.py`):
  - `get_batch_student_roster(db: AsyncSession, institution_id: UUID, filters: FilterParams)`
  - `get_skill_gap_aggregations(db: AsyncSession, institution_id: UUID, department_id: Optional[UUID])`
- **`PlacementDriveService`** (`backend/app/services/placement_drive_service.py`):
  - `get_institution_drives(db: AsyncSession, institution_id: UUID)`
  - `filter_eligible_students(db: AsyncSession, institution_id: UUID, criteria: ShortlistCriteria)`

---

## 11. Frontend Route & Page Design

### Routes ([`src/routes/AppRoutes.jsx`](file:///c:/Users/visha/OneDrive/Desktop/skilly/src/routes/AppRoutes.jsx))
- `/college`: Main College Portal Layout guarded by `RoleRoute` (`role="COLLEGE_ADMIN"`).
- `/college/dashboard`: Executive Dashboard & Overview analytics.
- `/college/departments`: Department & Faculty Management.
- `/college/students`: Batch Roster & Skill Gap Analytics.
- `/college/drives`: Campus Placement Drives & Shortlisting Tool.

### Components ([`src/modules/college/components/`](file:///c:/Users/visha/OneDrive/Desktop/skilly/src/modules/college/components/))
- `CollegeLayout.jsx`: Navigation sidebar, header, and institution context header.
- `CollegeDashboardWorkspace.jsx`: Metric cards, placement rate charts, top skill gaps table.
- `CollegeDepartmentWorkspace.jsx`: Department directory list and staff assignment.
- `CollegeStudentRosterWorkspace.jsx`: Filterable student grid, CGPA distribution, and skill badges.
- `CollegePlacementDriveWorkspace.jsx`: Active placement drive listing, candidate shortlisting modal, export tools.

---

## 12. Dashboard Metrics

All metrics are derived directly from live database tables:

1. **Total Enrolled Students**: `COUNT(students.id)` WHERE `institution_id = current_institution`.
2. **Total Academic Departments**: `COUNT(departments.id)` WHERE `institution_id = current_institution`.
3. **Active Placement Drives**: `COUNT(opportunities.id)` WHERE `is_active = true` AND company/drive is published for institution.
4. **Institutional Placement Rate (%)**: `(COUNT(DISTINCT placement_records.student_id) / Total Eligible Students) * 100`.
5. **Average Package (LPA)**: `AVG(placement_records.package_amount)`.
6. **Top Department Skill Gaps**: `COUNT(skill_gaps.id)` GROUP BY `skills.name` ORDER BY count DESC LIMIT 5.

---

## 13. Placement Drive Workflow

```
[Industry Opportunity Published]
                │
                ▼
[TPO Views Drive in /college/drives]
                │
                ▼
[Set Eligibility Criteria: Min CGPA, Batch, Dept, Skills]
                │
                ▼
[Run Deterministic Shortlisting Engine]
                │
                ▼
[View Eligible Candidate List & Match Score]
                │
                ▼
[Bulk Submit / Notify Candidates (Status -> APPLIED / SHORTLISTED)]
                │
                ▼
[Track Interview Rounds & Log Final Offers in placement_records]
```

---

## 14. Eligibility & Shortlisting Rules

The shortlisting engine evaluates candidate eligibility using deterministic SQL/ORM boolean logic:

1. **Institution Boundary**: `student.institution_id == current_institution_id` (Mandatory).
2. **Academic Threshold**: `student.cgpa >= criteria.min_cgpa`.
3. **Batch Alignment**: `student.graduation_year == criteria.graduation_year`.
4. **Department Filter**: `student.department_id IN (criteria.department_ids)`.
5. **Skill Match Threshold**: Student possesses `REQUIRED` skills with `proficiency_level >= min_proficiency`.

Zero arbitrary or unexplainable AI scores are used for shortlisting.

---

## 15. Security Design

- **Authentication**: JWT token in `Authorization: Bearer <token>` header.
- **RBAC**: FastAPI dependency `require_role("COLLEGE_ADMIN")` or `require_role(["COLLEGE_ADMIN", "TEACHER"])`.
- **Institution Scoping**: Backend extracts `institution_id` from database record of authenticated user (`institution_staff` or `teachers`).
- **Input Sanitization**: Pydantic v2 schemas validate all UUIDs, numeric bounds (CGPA 0.0–10.0), and string lengths.

---

## 16. Automated Test Plan

New test suite: `backend/test_college_module_phase4.py`

| Test Case | Description | Expected Outcome |
| :--- | :--- | :--- |
| `test_college_dashboard_metrics` | Fetch dashboard for verified College Admin | Status 200, valid JSON metrics matching DB state |
| `test_college_department_list` | Query departments under college | Status 200, returns list of departments |
| `test_college_student_roster_filter` | Filter students by CGPA >= 8.0 & Batch 2026 | Status 200, returns strictly matching students |
| `test_college_shortlist_engine` | Run shortlisting for campus drive criteria | Status 200, returns deterministic list of eligible students |
| `test_college_institution_isolation` | TPO A queries College B student data via student_id | Status 404 / 403 Forbidden (Zero Data Leak) |
| `test_college_rbac_denial` | Student or Alumni attempts to access `/api/v1/college/*` | Status 403 Forbidden |

---

## 17. Regression Test Plan

Before approving Module 04 completion, the following automated regression suites must execute and pass 100%:

1. **Auth & RBAC**: `python backend/audit_phase2_3.py`
2. **Phase 3.1 Student Dashboard**: `python backend/audit_phase3_1.py`
3. **Phase 3.2 Student Profile**: `python backend/test_student_profile_phase3_2.py`
4. **Phase 3.3 Student Career Role**: `python backend/test_student_career_phase3_3.py`
5. **Phase 3.4 Student Roadmap**: `python backend/test_student_roadmap_phase3_4.py`
6. **Phase 3.5 Student Assessment Engine**: `python backend/test_student_assessment_phase3_5.py`
7. **Database System Catalog Audit**: `python backend/database_final_verification_runner.py`
8. **Frontend Build**: `npm run build`

---

## 18. Risks & Open Questions

- **Risk**: Large institutions with 10,000+ students may experience slow unpaginated roster queries.
  - *Mitigation*: Mandatory pagination (`page`, `limit` default 20, max 100) enforced on `GET /api/v1/college/students`.
- **Open Question**: Should faculty members (`TEACHER` role) have write access to placement drives?
  - *Design Decision*: No. Placement drive creation and shortlisting are reserved for `COLLEGE_ADMIN` / TPO staff. Faculty members receive read-only roster & skill gap analytics for their assigned department.

---

## 19. Exact Files Expected To Change During Implementation

When implementation begins after explicit user approval, only the following files will be created or updated:

### Backend Files:
- `[NEW] backend/app/api/v1/endpoints/college.py`
- `[NEW] backend/app/services/college_service.py`
- `[NEW] backend/app/schemas/college.py`
- `[NEW] backend/test_college_module_phase4.py`
- `[MODIFY] backend/app/api/v1/router.py` (To register `/college` router)

### Frontend Files:
- `[NEW] src/modules/college/components/CollegeDashboardWorkspace.jsx`
- `[NEW] src/modules/college/components/CollegeDepartmentWorkspace.jsx`
- `[NEW] src/modules/college/components/CollegeStudentRosterWorkspace.jsx`
- `[NEW] src/modules/college/components/CollegePlacementDriveWorkspace.jsx`
- `[MODIFY] src/pages/College.jsx` (To mount real module components)

---

## 20. Final Design Decision

**DESIGN RECOMMENDATION**:  
🟢 **MODULE 04 DESIGN APPROVED FOR REVIEW**

The design leverages the verified 47-table database architecture without requiring any schema changes or migrations. All queries maintain strict institution-level multi-tenant isolation, IDOR protection, and deterministic eligibility filtering.

---
**STOP & WAIT FOR APPROVAL**:  
No source code, database tables, migrations, or frontend files have been modified. Implementation will commence only after explicit approval of this design specification.
