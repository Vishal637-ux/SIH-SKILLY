# SKILLY — Module 08: Skill & Assessment

## 1. Module Overview

**Module Name:** Skill & Assessment

**Purpose:**  
The Skill & Assessment module manages the student's skills, skill assessment, skill profile, skill evidence and skill-gap identification. It provides the foundation for skill-based career mapping, learning and opportunity matching.

---

## 2. Main Areas

```text
Skill & Assessment
│
├── Skill Taxonomy
├── Skill Profile
├── Skill Assessment
├── Assessment Questions
├── Assessment Attempts
├── Assessment Results
├── Skill Level
├── Skill Evidence
├── Skill Gap
├── Required Skills
├── Career Role Skills
└── Skill Progress
```

---

## 3. Skill Taxonomy

Provides a structured set of skills used across the SKILLY platform.

### Skill Areas

- Technical skills
- Soft skills
- Domain skills
- Industry-relevant skills
- Career-related skills

The skill taxonomy acts as a common reference for student profiles, assessments and opportunity requirements.

---

## 4. Skill Profile

Maintains the student's structured skill information.

### High-Level Information

- Skill
- Skill category
- Skill level
- Assessment-based evidence
- Certification / project evidence
- Skill progress

### Flow

```text
Student
   ↓
Skills
   ↓
Skill Profile
   ↓
Skill Level / Evidence
```

---

## 5. Skill Assessment

Allows students to evaluate their current skills.

### Assessment Flow

```text
Select Assessment
       ↓
Answer Questions
       ↓
Submit Assessment
       ↓
Evaluate Result
       ↓
Update Skill Profile
```

The assessment result contributes to the student's skill profile.

---

## 6. Assessment Questions

Contains questions used to evaluate skills.

### High-Level Areas

- Skill-related questions
- Question category
- Difficulty / level, where applicable
- Correct answer / evaluation criteria
- Assessment association

> Exact question format and evaluation logic will be defined during implementation.

---

## 7. Assessment Attempts

Maintains the student's assessment attempts.

### Information

- Student
- Assessment
- Attempt
- Start / completion status
- Result
- Date / time

This allows assessment activity and progress to be tracked.

---

## 8. Assessment Results

Provides the outcome of an assessment.

### High-Level Information

- Overall result
- Skill-wise result
- Identified strengths
- Areas requiring improvement
- Assessment status

---

## 9. Skill Level

Represents the student's current level for a skill.

### Example Structure

```text
Skill
  ↓
Current Level
  ↓
Evidence
  ↓
Progress
```

The exact skill-level scale will be defined during implementation.

---

## 10. Skill Evidence

Supports evidence associated with a student's skill.

### Possible Evidence

- Assessment result
- Certification
- Project
- Internship
- Achievement
- Other verified evidence

### Flow

```text
Student Skill
     ↓
Evidence
     ↓
Skill Verification / Record
```

---

## 11. Skill Gap

Identifies skills that need improvement by comparing the student's current skills with required skills.

### Flow

```text
Current Skill Profile
        +
Required Skills
        ↓
     Skill Gap
        ↓
Skills to Improve
```

The identified gaps can later support roadmap, learning and opportunity recommendations.

---

## 12. Required Skills

Represents skills required for a career role or opportunity.

### Sources

- Career role requirements
- Internship requirements
- Job requirements
- Industry requirements

These requirements can be compared with the student's skill profile.

---

## 13. Career Role Skills

Connects career roles with their required skills.

### Flow

```text
Career Role
     ↓
Required Skills
     ↓
Student Skill Comparison
     ↓
Skill Gap
```

This supports career exploration and skill-based career planning.

---

## 14. Skill Progress

Tracks changes in a student's skills over time.

### High-Level Areas

- Assessment progress
- Skill development
- Training / learning progress
- New evidence
- Skill-level changes

---

## 15. Skill Assessment & Gap Flow

```text
                  STUDENT
                     │
                     ↓
               Skill Assessment
                     │
                     ↓
              Assessment Result
                     │
                     ↓
                Skill Profile
                     │
            ┌────────┴────────┐
            ↓                 ↓
       Current Skills     Evidence
            │
            ↓
     Required Skills
            │
            ↓
         Skill Gap
            │
            ↓
      Skills to Improve
```

---

## 16. Integration with Other Modules

The Skill & Assessment module acts as a foundation for other SKILLY modules.

```text
Skill & Assessment
        │
        ├── Student
        │
        ├── Career Roadmap
        │
        ├── Internship & Placement
        │
        ├── Industry / Company
        │
        └── AI / Recommendations
```

### Example

```text
Student Skill Profile
        ↓
Required Opportunity Skills
        ↓
Skill Matching
        ↓
Relevant Opportunity
```

---

## 17. Module Boundary

### Included

- Skill taxonomy
- Skill profile
- Skill assessment
- Assessment questions
- Assessment attempts
- Assessment results
- Skill levels
- Skill evidence
- Skill gaps
- Required skills
- Career role skills
- Skill progress

### Not Included in This Module

- Student dashboard
- Detailed career roadmap
- Internship management
- Placement management
- Industry recruitment management
- Detailed AI model implementation
- Detailed database schema
- Detailed API specification

These functions belong to their respective modules.

---

## 18. High-Level Module Flow

```text
                 SKILL & ASSESSMENT
                         │
                         ↓
                  Skill Taxonomy
                         │
                         ↓
                 Skill Assessment
                         │
                         ↓
                 Assessment Result
                         │
                         ↓
                   Skill Profile
                         │
                 ┌───────┴───────┐
                 ↓               ↓
              Evidence       Skill Level
                 │               │
                 └───────┬───────┘
                         ↓
                    Skill Gap
                         ↓
                 Skills to Improve
                         ↓
             Learning / Career Roadmap
```

---

## 19. Implementation Note

The Skill & Assessment module focuses on **structured skills, assessment, skill profiling, evidence and skill-gap identification**.

Detailed screens, React components, APIs, database tables, assessment logic, scoring rules and AI implementation will be defined separately when this module is implemented.
