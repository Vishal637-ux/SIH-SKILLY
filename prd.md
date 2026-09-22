SKILLY – Combined Product Requirements Document (PRD)
Academia–Industry Skill Intelligence Platform | MVP v1.0
1. Product Overview
SKILLY is a centralized skill-to-career platform connecting students, academia, colleges/TPOs and industry across Skill Development → Internship → Placement.
2. Product Vision
Industry Demand → Required Skills → Student Capability → Skill Gap → Personalized Development → Internship / Project → Industry Evaluation → Verified Skill → Placement → Academia Insight → Updated Skill Intelligence
3. Product Objectives
•	Provide a public-facing website and secure authentication.
•	Build structured student skill profiles and career journeys.
•	Assess skills, identify gaps and recommend development paths.
•	Connect students with internships, projects, jobs and application tracking.
•	Centralize college/TPO student, company, scheduling and placement operations.
•	Connect students with teachers, trainers, alumni and mentors.
•	Enable companies to post opportunities, assess candidates, manage ATS and onboarding.
•	Support industry training, workshops, certifications, competitions and campus drives.
•	Provide meaningful recognition, peer skill exchange and operational visibility.
4. User Roles & Modules
•	Visitor/Public User – Public Website
•	Student – Student Module
•	College Admin/TPO – College Portal
•	Teacher/Faculty – College Portal
•	Trainer – College Portal
•	Company/Industry – Industry Module
•	Alumni/Mentor – College Portal
5. Public Website, Login & Registration
5.1 Public Website
•	Home: logo/name, navigation, hero/introduction, system description, features/services, CTA, Login/Register and footer.
•	About: purpose, problem, benefits and project information.
•	Features/Services: feature name, short description and relevant visual.
•	Contact: email, phone, address and contact form where implemented.
•	Navigation: Home, About, Features/Services, Contact, Login, Register.
5.2 Registration & Login
•	Registration fields: Full Name, Email, Username, Password, Confirm Password, Mobile Number.
•	Validate required fields, email, mobile and password requirements.
•	Prevent duplicate email/username.
•	Login using Email/Username and Password.
•	Validate credentials on the server and redirect authenticated users to the appropriate module.
•	Display clear validation and authentication errors.
5.3 Shared Authentication & Security
•	JWT-based authentication.
•	Role-based authorization (RBAC).
•	Secure password hashing; never store plain-text passwords.
•	Protected APIs and backend authorization independent of frontend routing.
•	Input validation, secure token/session handling and HTTPS/TLS.
•	Secure document access and role-appropriate data access.
6. Student Module
6.1 Student Journey
Register → Complete Profile → Select Target Career → Assessment → Skill Profile → Role Mapping → Skill Gap → Personalized Roadmap → Learn/Build/Practice → Internship → Apply → Track → Internship → Industry Evaluation → Verified Skill Evidence → Updated Skill Profile
6.2 Student Functions
•	Student profile: personal, institution, academic, location, bio and career-interest data.
•	Canonical skill taxonomy and skill graph with prerequisite/related/specialization relationships.
•	Technical, soft-skill, aptitude and role-specific assessments.
•	Skill profile with proficiency, evidence, source, confidence, verification status and assessment date.
•	Structured career/role mapping and deterministic skill-gap calculation.
•	Personalized roadmap using skill gap, skill graph, priority engine, RAG retrieval, LLM personalization and validation.
•	Internship/project discovery, eligibility/readiness, matching, application and tracking.
•	Hybrid matching using eligibility, skill match, proficiency, career interest, semantic similarity and evidence.
•	Internship evaluation feeding evidence into the skill profile.
•	Verified Skill Passport and portfolio.
•	Resume feedback and skill comparison.
•	Skill-centric community, resources and AI Career Coach grounded in platform/student data.
7. College / TPO Portal
7.1 Core College Journey
Student Data → Progress & Achievement → Company Opportunities → Coordination → Placement → Outcome
7.2 College Functions
•	Teacher & Trainer Connect: profiles, expertise, skills, availability, guidance and training coordination.
•	Student Achievement & Progress Dashboard: achievements, skills, projects, internships, certifications, competitions and placement progress.
•	Integrated Student, Company & Placement Management: records, company requirements, eligibility, shortlisting, recruitment stages and outcomes.
•	Smart Scheduling: interviews, assessments, training, mentorship and placement activities.
•	Alumni & Mentor Connect: search/filter, connections, guidance and experience sharing.
•	Engagement & Recognition: meaningful participation, milestones, badges and consistency.
•	Peer Skill Exchange: 'I can help' / 'I want to learn', resources, guidance and collaboration.
7.3 College Operations
•	College/TPO dashboard: students, departments, progress, achievements, opportunities, placement activity, schedules, mentor/alumni engagement and recognition.
•	Teacher/Trainer dashboard: expertise, availability, connected students, training/mentorship and schedules.
•	Search/filter students, teachers/trainers, alumni/mentors and companies using relevant attributes.
•	Role-based notifications for opportunities, interviews, assessments, training, mentorship, connections and recognition.
8. Industry / Company Module
8.1 Industry Sections
•	Company Profile
•	Job/Internship Posting
•	Assessment
•	Training Programs / Workshops / Certifications
•	Recruitment Dashboard
•	Virtual Drives / GDs / Interviews
•	Offers, Onboarding & Documents
•	ATS
•	Competitions & Hackathons
•	AI-Based Regional Hiring
•	College Invitations
•	Intern Management
•	Contribution / Donation / Sponsorship Tracking
8.2 Industry Functions
•	Create/edit company profile with identity, industry, locations, size and contact information.
•	Create/edit/close internship and job postings with skills, role, duration, stipend/salary and eligibility.
•	Create posting-linked assessments with MCQ/coding/aptitude and cutoff-based auto-evaluation.
•	Create training, workshop and certification programs.
•	View recruitment statistics, hiring history and skill/college trends.
•	Schedule virtual drives, GDs and interviews with optional recording.
•	Generate offers, verify documents and complete onboarding.
•	Track applications through ATS: Applied → Shortlisted → Interviewed → Offered → Rejected → Hired.
•	Create competitions/hackathons with rules, timeline, eligibility and results.
•	Apply regional hiring filter only after base eligibility criteria are satisfied.
•	Invite colleges for campus drives and track responses.
•	Track interns and send performance reports to associated colleges.
•	Log donation/sponsorship contributions; actual payment gateway is outside stated V1 scope.
9. Cross-Module Integration
•	Authentication → Role detection → Appropriate dashboard.
•	Industry posting → Student discovery/recommendation → Application → Industry ATS.
•	Industry assessment → Results → Student skill profile.
•	College invitation → College/TPO → Campus drive coordination.
•	Intern performance report → College Portal → Student development record.
•	Student profile/skills → Industry matching and eligibility.
•	Placement status → Student and College/TPO tracking.
•	Teacher/trainer/mentor connections → Student development and scheduling.
10. End-to-End Platform Flow
Public Website → Registration/Login → RBAC Dashboard → Student / College / Industry Workflows → Skill & Opportunity Data Exchange → Internship/Placement → Evaluation & Outcomes → Updated Skill Intelligence
11. Core API Domains
•	/api/v1/auth
•	/api/v1/students
•	/api/v1/skills
•	/api/v1/assessments
•	/api/v1/careers
•	/api/v1/skill-gaps
•	/api/v1/roadmaps
•	/api/v1/recommendations
•	/api/v1/internships
•	/api/v1/applications
•	/api/v1/evaluations
•	/api/v1/portfolio
•	/api/v1/community
•	/api/v1/ai
•	College/TPO APIs for student, company, placement, scheduling and mentorship workflows.
•	Industry APIs for profile, postings, assessments, ATS, drives, onboarding and intern reporting.
12. Technical Architecture
•	Frontend: React.js
•	Backend: Python + FastAPI
•	Database: PostgreSQL
•	Semantic search: pgvector where required
•	Authentication: JWT + RBAC
•	Secure object/file storage for resumes, certificates and supporting documents
•	Dockerized deployment with gradual horizontal scaling
•	Caching/background processing where required
High-level flow: React.js → FastAPI → PostgreSQL
Supporting services: FastAPI → Secure Storage / Notifications / AI & Retrieval Components
13. Non-Functional Requirements
•	Security: JWT, RBAC, secure password hashing, HTTPS/TLS, input validation, API authorization, data isolation and secure documents.
•	Performance: pagination, indexing, efficient search/filtering, caching and asynchronous processing for expensive operations.
•	Scalability: stateless FastAPI, PostgreSQL source of truth, pgvector and gradual horizontal scaling.
•	Reliability: error handling, transactions where required, background processing, logging and monitoring.
•	Usability: responsive UI, role-specific dashboards, clear loading/empty/error states and minimal steps for common operations.
•	Maintainability: modular frontend/backend, reusable components, documented API contracts and integration-friendly design.
14. MVP Priorities
•	P0 – Must Have: public website, registration/login, RBAC, student profile, skill taxonomy, career mapping, assessment, skill profile/gap, internship discovery/matching, applications and core college/company operations.
•	P1 – Core Differentiation: personalized roadmap, RAG resources, AI career coach, digital portfolio, internship evaluation, Verified Skill Passport, mentorship, recognition and peer exchange.
•	P2 – Post-MVP: expanded community/resource sharing, competitions, newsletter, external integrations and advanced automation/analytics.
15. Combined Acceptance Criteria
•	Public pages work without authentication.
•	Registration validates inputs and prevents duplicates.
•	Login authenticates and redirects by role.
•	Unauthorized users cannot access protected pages/APIs.
•	Students can profile, assess skills, view gaps, receive recommendations and apply to internships.
•	Students can track applications and internship evaluation/evidence.
•	College/TPO can manage student/company/placement information and schedules.
•	Teachers/trainers/alumni/mentors can participate in guidance workflows.
•	Companies can create profiles, post opportunities, assess/shortlist candidates, manage ATS and onboarding.
•	Industry evaluations can feed student evidence/skill records.
•	Cross-module APIs exchange required data successfully.
•	Responsive UI, validation, security, error handling and testing are implemented.
16. Definition of Done
•	Database model exists.
•	API exists and is documented.
•	Validation and authorization exist.
•	Business logic exists.
•	Frontend exists and is API-integrated.
•	Loading/empty/error states exist.
•	Tests exist.
•	Documentation exists.
•	Code review is completed.
•	Dependent modules are integrated.
•	Relevant end-to-end workflow works successfully.
17. Out of Scope / Deferred
•	Admin panel beyond the stated modules.
•	Features assigned to other modules.
•	External job portal integrations unless later approved.
•	Actual payment gateway for donation/sponsorship in V1.
•	Custom-built video conferencing engine; third-party embed assumed.
•	Advanced deep-learning regional hiring models; V1 specifies rule-based/basic ML.
•	Unrestricted copyrighted-book sharing.
•	Unnecessary advanced analytics or AI automation outside defined workflows.
18. Product Principles
•	Student development first.
•	One centralized workspace.
•	Skill-driven workflows.
•	Operational simplicity.
•	Meaningful recognition.
•	Free student participation for core participation.
•	Collaborative ecosystem.
•	Privacy and access control.
•	Scalable architecture.
•	AI should support structured platform data and evidence rather than replace authoritative data.
19. Final Value Proposition
SKILLY connects public access, secure identity, student skill development, college operations, industry requirements, internships, mentorship, recruitment and placement into one continuous academia–industry ecosystem.
Source basis: combined from the supplied Public Website/Login/Registration PRD, Student Module PRD, College Portal PRD and Industry Module PRD.
