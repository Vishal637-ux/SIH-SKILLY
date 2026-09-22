# SKILLY — Module 09: Internship & Placement

## 1. Module Overview

**Module Name:** Internship & Placement

**Purpose:**  
The Internship & Placement module manages internship, project and placement opportunities and supports the journey from opportunity discovery and eligibility to application, selection, internship and placement.

---

## 2. Main Areas

```text
Internship & Placement
│
├── Opportunities
├── Internship
├── Projects
├── Jobs / Placement
├── Eligibility
├── Skill Matching
├── Applications
├── Shortlisting
├── Assessments
├── Interviews
├── Selection
├── Offers
├── Onboarding
├── Internship Progress
├── Internship Evaluation
└── Placement Tracking
```

---

## 3. Opportunities

Provides a centralized place for students to discover relevant career opportunities.

### Opportunity Types

- Internships
- Jobs
- Projects
- Apprenticeships
- Entry-level opportunities

### High-Level Information

- Opportunity title
- Company
- Description
- Required skills
- Eligibility
- Location / work mode
- Duration, where applicable
- Application details
- Selection process

---

## 4. Internship

Supports the complete internship lifecycle.

### Internship Flow

```text
Opportunity
   ↓
Eligibility
   ↓
Application
   ↓
Shortlisting
   ↓
Selection
   ↓
Internship Start
   ↓
Progress
   ↓
Evaluation
   ↓
Completion
```

### Areas

- Internship opportunities
- Required skills
- Eligibility
- Applications
- Selection
- Internship status
- Internship duration
- Progress
- Evaluation
- Completion

---

## 5. Projects

Supports practical and industry-oriented project opportunities.

### Areas

- Project opportunities
- Project requirements
- Required skills
- Eligibility
- Student applications
- Selection
- Project progress
- Project completion

---

## 6. Jobs / Placement

Supports job and placement opportunities.

### Placement Flow

```text
Job Opportunity
      ↓
Eligibility
      ↓
Skill Matching
      ↓
Application
      ↓
Shortlisting
      ↓
Assessment / Interview
      ↓
Selection
      ↓
Offer
      ↓
Placement
```

---

## 7. Eligibility

Determines whether a student meets the requirements of an opportunity.

### Possible Criteria

- Academic eligibility
- Required skills
- Course / department
- Graduation year
- Other opportunity-specific requirements

### Flow

```text
Opportunity Requirements
        ↓
Student Information
        ↓
Eligibility Check
        ↓
Eligible / Not Eligible
```

---

## 8. Skill Matching

Connects student skills with opportunity requirements.

### Flow

```text
Student Skill Profile
        +
Opportunity Required Skills
        ↓
Skill Matching
        ↓
Relevant Opportunities
```

Skill matching can support internship and placement recommendations.

---

## 9. Applications

Students can apply to relevant internship, project and placement opportunities.

### Application Flow

```text
Opportunity
   ↓
View Details
   ↓
Check Eligibility
   ↓
Apply
   ↓
Application Submitted
```

---

## 10. Shortlisting

Supports candidate shortlisting after applications.

### High-Level Flow

```text
Applications
      ↓
Eligibility
      ↓
Skill / Requirement Matching
      ↓
Assessment, where applicable
      ↓
Shortlisting
```

---

## 11. Assessments

Some opportunities may include an assessment as part of the selection process.

### Possible Flow

```text
Application
   ↓
Assessment
   ↓
Result
   ↓
Selection Process
```

The exact assessment format depends on the opportunity.

---

## 12. Interviews

Supports interview-related activities during the selection process.

### Areas

- Interview schedule
- Interview stage
- Candidate status
- Interview outcome
- Next selection stage

---

## 13. Selection

Tracks candidates through the selection process.

### High-Level Status

```text
Applied
   ↓
Shortlisted
   ↓
Interviewed
   ↓
Selected
```

Additional stages may be used depending on the opportunity.

---

## 14. Offers

Supports offer-related tracking after selection.

### Flow

```text
Selected
   ↓
Offer
   ↓
Offer Status
   ↓
Acceptance
```

---

## 15. Onboarding

Supports the transition from selection to joining.

### High-Level Flow

```text
Offer Accepted
      ↓
Required Information / Documents
      ↓
Onboarding
      ↓
Joining
```

---

## 16. Internship Progress

Tracks the student's progress during an internship.

### Areas

- Internship status
- Tasks / project work
- Progress
- Mentor / faculty interaction
- Feedback
- Completion status

---

## 17. Internship Evaluation

Supports evaluation of internship performance.

### High-Level Flow

```text
Internship
   ↓
Work / Project
   ↓
Industry Evaluation
   ↓
Performance / Skill Evidence
   ↓
Completion
```

Evaluation information can contribute to the student's skill evidence and portfolio.

---

## 18. Placement Tracking

Provides visibility into a student's placement journey.

### Tracking Flow

```text
Eligibility
   ↓
Application
   ↓
Shortlisting
   ↓
Interview
   ↓
Selection
   ↓
Offer
   ↓
Placement
```

---

## 19. Module Integration

The Internship & Placement module connects with other SKILLY modules.

```text
Skill & Assessment
        ↓
Skill Profile / Skill Gap
        ↓
Internship & Placement
        ↓
Matching
        ↓
Application
        ↓
Selection
        ↓
Internship / Placement
        ↓
Evaluation / Career Record
```

### Connected Modules

- Student
- Skill & Assessment
- Industry / Company
- College / TPO
- Teacher / Trainer
- Alumni / Mentor
- Portfolio & Achievements
- AI / Recommendations
- Notifications

---

## 20. Module Boundary

### Included

- Opportunity discovery
- Internship opportunities
- Project opportunities
- Job / placement opportunities
- Eligibility
- Skill matching
- Applications
- Shortlisting
- Assessments
- Interviews
- Selection
- Offers
- Onboarding
- Internship progress
- Internship evaluation
- Placement tracking

### Not Included in This Module

- Student profile management
- Skill assessment implementation
- Company profile management
- College / TPO administration
- Detailed portfolio management
- Core authentication implementation
- Detailed AI model implementation
- Detailed database schema
- Detailed API specification

These functions belong to their respective modules.

---

## 21. High-Level Module Flow

```text
                 INTERNSHIP & PLACEMENT
                           │
                           ↓
                     Opportunities
                           │
                  ┌────────┴────────┐
                  ↓                 ↓
              Internship          Jobs
                  │                 │
                  └────────┬────────┘
                           ↓
                       Eligibility
                           ↓
                    Skill Matching
                           ↓
                       Application
                           ↓
                      Shortlisting
                           ↓
                  Assessment / Interview
                           ↓
                       Selection
                           ↓
                         Offer
                           ↓
                       Onboarding
                           │
              ┌────────────┴────────────┐
              ↓                         ↓
         Internship                 Placement
              ↓                         ↓
          Progress                  Tracking
              ↓
         Evaluation
```

---

## 22. Implementation Note

The Internship & Placement module focuses on the **opportunity-to-career lifecycle**, connecting students, institutions and industry through internships, projects, jobs, applications, selection and placement tracking.

Detailed screens, React components, APIs, database tables, permissions, matching logic and validation rules will be defined separately when this module is implemented.
