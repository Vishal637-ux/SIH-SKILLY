# SKILLY — Module 13: AI / Recommendations

## 1. Module Overview

**Module Name:** AI / Recommendations

**Purpose:**  
The AI / Recommendations module provides intelligent analysis, matching and recommendations across the SKILLY platform. It uses student skill information, career requirements and opportunity data to support personalized career and skill-related decisions.

---

## 2. Main Areas

```text
AI / Recommendations
│
├── Skill Analysis
├── Skill Gap Analysis
├── Career Recommendations
├── Learning Recommendations
├── Internship Recommendations
├── Job Recommendations
├── Skill Matching
├── Opportunity Matching
├── Candidate Matching
├── Personalized Roadmap Support
├── AI Career Support
└── Recommendation History
```

---

## 3. Skill Analysis

Analyzes structured student skill information and assessment results.

### High-Level Inputs

- Student skills
- Assessment results
- Skill levels
- Certifications
- Projects
- Internship experience
- Other available skill evidence

### Flow

```text
Student Data
     ↓
Skill Analysis
     ↓
Skill Profile Insights
```

---

## 4. Skill Gap Analysis

Compares current student skills with required skills.

### Flow

```text
Current Skills
      +
Required Skills
      ↓
AI / Matching Analysis
      ↓
Skill Gap
      ↓
Skills to Improve
```

The detailed skill assessment and skill-gap records belong to the **Skill & Assessment** module.

---

## 5. Career Recommendations

Provides career-related recommendations based on available student information.

### Possible Inputs

- Skills
- Interests
- Career goals
- Skill gaps
- Experience
- Career role requirements

### Flow

```text
Student Profile
      ↓
AI Analysis
      ↓
Career Role Matching
      ↓
Career Recommendations
```

---

## 6. Learning Recommendations

Recommends relevant learning or skill-development activities based on identified needs.

### Flow

```text
Skill Gap
    ↓
Required Skills
    ↓
Learning Resources / Programs
    ↓
Recommended Learning
```

---

## 7. Internship Recommendations

Helps identify internship opportunities relevant to the student's skills and requirements.

### Flow

```text
Student Skill Profile
        ↓
Internship Requirements
        ↓
Matching
        ↓
Relevant Internships
```

---

## 8. Job Recommendations

Supports job discovery based on student profile and opportunity requirements.

### Flow

```text
Student Profile
      ↓
Required Skills / Eligibility
      ↓
Matching
      ↓
Relevant Jobs
```

---

## 9. Skill Matching

Matches skills between students and career or opportunity requirements.

### High-Level Flow

```text
Student Skills
      +
Required Skills
      ↓
Skill Matching
      ↓
Match Results
```

Matching can use structured rules and AI-based methods where appropriate.

---

## 10. Opportunity Matching

Connects student profiles with relevant internships, projects and jobs.

### Flow

```text
Student Profile
      ↓
Eligibility Filtering
      ↓
Skill Matching
      ↓
Recommendation
      ↓
Relevant Opportunities
```

A hybrid approach can use rule-based filtering before AI-based matching to reduce unnecessary processing.

---

## 11. Candidate Matching

Supports industry-side discovery of relevant candidates.

### Flow

```text
Industry Requirement
        ↓
Required Skills / Eligibility
        ↓
Candidate Data
        ↓
Matching
        ↓
Relevant Candidates
```

The final hiring decision remains with the authorized company/recruitment process.

---

## 12. Personalized Roadmap Support

AI can support creation or refinement of a student's learning roadmap.

### Flow

```text
Career Goal
    ↓
Required Skills
    ↓
Current Skills
    ↓
Skill Gap
    ↓
Learning Recommendations
    ↓
Personalized Roadmap
```

---

## 13. AI Career Support

Provides AI-assisted career guidance within the student's career journey.

### Possible Areas

- Career exploration
- Skill guidance
- Learning guidance
- Opportunity discovery
- Roadmap support
- Career-related questions

AI outputs should be treated as recommendations and should not replace the student's own decisions.

---

## 14. Recommendation History

Maintains records of recommendations generated for the user where required.

### Possible Information

- Recommendation type
- Recommendation result
- Related user
- Related opportunity / career / learning item
- Date / time
- Recommendation status

---

## 15. AI Processing Flow

```text
                  USER / PLATFORM DATA
                           │
                           ↓
                    Data Preparation
                           │
                           ↓
                 Rule-Based Filtering
                           │
                           ↓
                  AI / Matching Layer
                           │
             ┌─────────────┼─────────────┐
             ↓             ↓             ↓
        Skill Analysis   Matching    Recommendations
             │             │             │
             └─────────────┼─────────────┘
                           ↓
                    Recommendation
                           ↓
                         User
```

---

## 16. Hybrid AI Approach

The module can use a hybrid approach:

```text
Rule-Based Filtering
        ↓
Eligibility / Basic Conditions
        ↓
Embeddings / Vector Search
        ↓
Semantic Matching
        ↓
LLM — Only When Required
        ↓
Recommendation
```

This approach can reduce unnecessary AI processing and support scalability.

---

## 17. Integration with Other Modules

```text
                         AI / RECOMMENDATIONS
                                  │
          ┌───────────────────────┼───────────────────────┐
          ↓                       ↓                       ↓
   Skill & Assessment          Student              Industry
          │                       │                       │
          ↓                       ↓                       ↓
      Skill Data              Profile              Requirements
          │                       │                       │
          └───────────────────────┼───────────────────────┘
                                  ↓
                         AI / Matching Engine
                                  ↓
                   ┌──────────────┼──────────────┐
                   ↓              ↓              ↓
                Career        Learning       Opportunities
             Recommendations Recommendations Recommendations
```

### Connected Modules

- Student
- Skill & Assessment
- Internship & Placement
- Industry / Company
- Portfolio & Achievements
- College / TPO
- Teacher / Trainer
- Alumni / Mentor
- Notifications

---

## 18. Module Boundary

### Included

- Skill analysis
- Skill-gap analysis support
- Career recommendations
- Learning recommendations
- Internship recommendations
- Job recommendations
- Skill matching
- Opportunity matching
- Candidate matching
- Personalized roadmap support
- AI career support
- Recommendation history

### Not Included in This Module

- Core student profile management
- Core skill assessment management
- Internship management
- Placement management
- Company profile management
- Core authentication
- Detailed database schema
- Detailed API specification
- Final hiring decision

These functions belong to their respective modules.

---

## 19. High-Level Module Flow

```text
                    AI / RECOMMENDATIONS
                              │
                              ↓
                        User / Role Data
                              │
                              ↓
                         Skill Analysis
                              │
                    ┌─────────┴─────────┐
                    ↓                   ↓
                Skill Gap          Requirements
                    │                   │
                    └─────────┬─────────┘
                              ↓
                         AI Matching
                              │
              ┌───────────────┼───────────────┐
              ↓               ↓               ↓
           Career         Learning       Opportunities
        Recommendations Recommendations Recommendations
              │               │               │
              └───────────────┼───────────────┘
                              ↓
                         User Decision
```

---

## 20. Implementation Note

The AI / Recommendations module focuses on **AI-assisted analysis, skill matching and personalized recommendations** across the SKILLY career journey.

Detailed AI models, embeddings, vector search, LLM usage, prompts, evaluation metrics, APIs, database tables and cost controls will be defined separately during implementation.
