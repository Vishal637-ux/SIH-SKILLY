# SKILLY Module 04 — Design Clarification & Architectural Alignment

## 1. RBAC Clarification: Canonical Roles vs Staff Sub-Roles

### **Question / Ambiguity**:
Are `TPO_ADMIN`, `TPO_COORDINATOR`, and `DEPT_HEAD` new canonical system roles or permission/sub-role concepts under existing canonical roles?

### **Architectural Decision (Option A)**:
They are **permission / sub-role designation concepts** stored in the existing `institution_staff.staff_role` column, strictly operating under the canonical `users.role = "COLLEGE_ADMIN"`.

- **No New Canonical System Roles**: The primary `users.role` enum values remain strictly `['STUDENT', 'COLLEGE_ADMIN', 'TEACHER', 'INDUSTRY', 'ALUMNI']`.
- **Database-Authoritative RBAC Mapping**:
  1. Primary auth dependency `require_role("COLLEGE_ADMIN")` validates `users.role == "COLLEGE_ADMIN"`.
  2. Secondary permission check queries `institution_staff` using `current_user.id` to resolve:
     - `staff_role`: `"TPO_ADMIN"`, `"TPO_COORDINATOR"`, or `"DEPT_HEAD"`.
     - `institution_id`: Mandatory multi-tenant institutional isolation boundary.
  3. Canonical `users.role == "TEACHER"` users resolve their `institution_id` and `department_id` via the existing `teachers` table, granting read-only access to their department's roster and skill gap analytics.

### **Exact Mapping & Implementation Impact**:

| User Type | Canonical `users.role` | Database Identity Table | Sub-Role (`staff_role`) | Module 04 Permissions |
| :--- | :--- | :--- | :--- | :--- |
| **Institutional TPO Admin** | `COLLEGE_ADMIN` | `institution_staff` | `"TPO_ADMIN"` | Full TPO Portal Access (Dashboard, Roster, Drives, Shortlisting, Staff Management) |
| **TPO Coordinator** | `COLLEGE_ADMIN` | `institution_staff` | `"TPO_COORDINATOR"` | Drive Management, Shortlisting, Candidate Tracking, Student Roster |
| **Department Head (Staff)** | `COLLEGE_ADMIN` | `institution_staff` | `"DEPT_HEAD"` | Department-scoped Student Roster & Skill Gap Analytics |
| **Faculty / Teacher** | `TEACHER` | `teachers` | N/A | Read-Only Department Roster & Skill Gap Analytics |

---

## 2. Placement Drive Ownership & Opportunity Reuse

### **Question / Ambiguity**:
Who owns opportunity creation, who publishes opportunities, what does College/TPO configure for a campus drive, and how is the existing `opportunities` table reused?

### **Architectural Ownership Matrix**:

| Ownership Concern | Responsible Persona | Domain / Module | Entity & Mechanism |
| :--- | :--- | :--- | :--- |
| **Opportunity Creation** | Industry / Company | Module 06 (Industry) | Inserts record into `opportunities` table (`company_id`, `title`, `role_type`, `description`, `stipend_salary`, `application_deadline`, `status='OPEN'`). |
| **Opportunity Publishing** | Industry / Company | Module 06 (Industry) | Sets `opportunities.status = 'OPEN'` making it visible for campus recruitment. |
| **Campus Drive Consumption** | College Admin / TPO | Module 04 (College) | Reads open opportunities from `opportunities` table. Zero duplicate drive creation tables are added. |
| **Drive Criteria & Shortlisting** | College Admin / TPO | Module 04 (College) | Configures institution-specific eligibility filters (min CGPA, batch year, department, required skill proficiency) against `opportunities.id`. |
| **Student Application & Status** | College Admin / TPO & Student | Module 03 / Module 04 | Creates/updates `applications` (`opportunity_id`, `student_id`, `status`: `APPLIED` ➔ `SHORTLISTED` ➔ `INTERVIEW_SCHEDULED`). |
| **Placement Outcome Logging** | College Admin / TPO | Module 04 (College) | Logs final accepted offers into `placement_records` table (`student_id`, `company_name`, `job_title`, `package_amount`, `status='ACCEPTED'`). |

### **Key Rules**:
1. **Module 04 ONLY Consumes Opportunities**: College TPOs do NOT create arbitrary company job postings. TPOs view open opportunities posted by companies (`opportunities` table) and initiate campus drive workflows.
2. **Opportunity Table Reuse**: Campus placement drives in Module 04 represent **institution-scoped views, shortlist queries, and application tracking pipelines** built directly on existing `opportunities`, `applications`, and `placement_records` tables.

---

## 3. Updated Endpoint Authorization Matrix

| Method | Path | Canonical Auth Guard | Sub-Role / Scope Rule | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/college/dashboard` | `require_role(["COLLEGE_ADMIN"])` | `institution_staff.institution_id` | Fetch institutional metrics & top skill gaps |
| `GET` | `/api/v1/college/departments` | `require_role(["COLLEGE_ADMIN", "TEACHER"])` | Own `institution_id` | List departments with student/faculty counts |
| `GET` | `/api/v1/college/faculty` | `require_role(["COLLEGE_ADMIN", "TEACHER"])` | Own `institution_id` | Read faculty & staff directory |
| `GET` | `/api/v1/college/students` | `require_role(["COLLEGE_ADMIN", "TEACHER"])` | Own `institution_id` (+ dept for `TEACHER`) | Filter student roster (CGPA, Batch, Dept, Role) |
| `GET` | `/api/v1/college/analytics/skills`| `require_role(["COLLEGE_ADMIN", "TEACHER"])` | Own `institution_id` | Aggregate batch skill proficiencies & gaps |
| `GET` | `/api/v1/college/drives` | `require_role(["COLLEGE_ADMIN"])` | Own `institution_id` | Fetch open campus placement drives (`opportunities`) |
| `POST`| `/api/v1/college/shortlist` | `require_role(["COLLEGE_ADMIN"])` | Own `institution_id` | Run deterministic shortlisting on an opportunity |
| `POST`| `/api/v1/college/placements` | `require_role(["COLLEGE_ADMIN"])` | Own `institution_id` | Record confirmed student placement in `placement_records` |

---

## 4. Exact File-Change List for Implementation

When implementation begins after explicit user approval, only the following files will be created or updated:

### Backend Files:
- `[NEW] backend/app/schemas/college.py` (Pydantic v2 schemas for college metrics, roster query filters, shortlisting request/response)
- `[NEW] backend/app/services/college_service.py` (Service business logic for dashboard metrics, student roster filtering, shortlisting engine, placement logging)
- `[NEW] backend/app/api/v1/endpoints/college.py` (FastAPI router endpoints guarded by `require_role`)
- `[NEW] backend/test_college_module_phase4.py` (Automated integration & isolation test suite)
- `[MODIFY] backend/app/api/v1/router.py` (Includes `/college` router prefix)

### Frontend Files:
- `[NEW] src/modules/college/components/CollegeDashboardWorkspace.jsx`
- `[NEW] src/modules/college/components/CollegeDepartmentWorkspace.jsx`
- `[NEW] src/modules/college/components/CollegeStudentRosterWorkspace.jsx`
- `[NEW] src/modules/college/components/CollegePlacementDriveWorkspace.jsx`
- `[MODIFY] src/pages/College.jsx` (Mounts real module workspaces)

---

## 5. Final Implementation-Ready Decision

🟢 **DESIGN CLARIFICATION COMPLETE & IMPLEMENTATION READY**

- **RBAC**: Uses existing canonical `users.role = "COLLEGE_ADMIN"` with `institution_staff.staff_role` for sub-role permission granularity. Zero new canonical roles or database migration required.
- **Drive Ownership**: Industry creates & publishes `opportunities` (Module 06); College TPO consumes open opportunities and manages campus shortlisting & placement logging (Module 04).
- **Compliance**: Operates 100% within the verified 47-table PostgreSQL schema.

---
**STOP & WAIT FOR APPROVAL**:  
No source code, database tables, migrations, or frontend files have been modified. Implementation will begin only after explicit approval of this clarified design.
