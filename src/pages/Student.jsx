import React from 'react';
import { useLocation } from 'react-router-dom';
import { 
  Award, 
  Layers, 
  TrendingUp, 
  Target, 
  Compass, 
  BookOpen, 
  Briefcase, 
  FileText, 
  Building2, 
  Users, 
  MessageSquare, 
  Trophy, 
  Sparkles, 
  Bot, 
  Bell
} from 'lucide-react';
import { 
  StudentLayout, 
  StudentDashboard, 
  StudentProfile, 
  StudentCareerWorkspace,
  StudentRoadmapWorkspace,
  StudentLearningWorkspace,
  StudentAssessmentCatalog,
  StudentSkillsWorkspace,
  StudentSkillGapWorkspace,
  StudentModulePlaceholder,
  StudentInternshipsWorkspace,
  StudentPlacementWorkspace,
  StudentMentorshipWorkspace,
  StudentCommunityWorkspace,
  StudentCompetitionsWorkspace
} from '../modules/student';
import NotificationCenter from '../components/NotificationCenter';
import RecommendationWorkspace from '../components/RecommendationWorkspace';


export default function Student() {
  const location = useLocation();
  const path = location.pathname.toLowerCase().replace(/\/$/, '');

  // Subpath router inside Student Portal
  if (path === '/student' || path === '/student/dashboard') {
    return (
      <StudentLayout activeViewTitle="Dashboard">
        <StudentDashboard />
      </StudentLayout>
    );
  }

  if (path === '/student/profile') {
    return (
      <StudentLayout activeViewTitle="Profile & Academics">
        <StudentProfile />
      </StudentLayout>
    );
  }

  if (path === '/student/journey') {
    return (
      <StudentLayout activeViewTitle="Career Journey">
        <StudentModulePlaceholder
          title="Student Career Journey"
          subtitle="End-to-end pathway from foundational onboarding to institutional placement."
          icon={Compass}
          domainModule="Module 03 — Student Journey Orchestration"
          domainDescription="Brings your profile, verified competencies, skill gap diagnostics, milestone roadmaps, project internships, mentorship sessions, and campus drives into one continuous progressive journey."
          features={[
            "Phase 1: Institutional & Departmental Setup",
            "Phase 2: Diagnostic Skill Assessment & Benchmarking",
            "Phase 3: Automated Gap Analysis vs Industry Target Roles",
            "Phase 4: Milestone Roadmaps & Certified Training",
            "Phase 5: Corporate Internships, Live Projects & Placement Drives"
          ]}
        />
      </StudentLayout>
    );
  }

  if (path === '/student/assessments') {
    return (
      <StudentLayout activeViewTitle="Skill Assessment">
        <StudentAssessmentCatalog />
      </StudentLayout>
    );
  }

  if (path === '/student/skills') {
    return (
      <StudentLayout activeViewTitle="Skill Profile">
        <StudentSkillsWorkspace />
      </StudentLayout>
    );
  }

  if (path === '/student/skill-gaps') {
    return (
      <StudentLayout activeViewTitle="Skill Gap Analysis">
        <StudentSkillGapWorkspace />
      </StudentLayout>
    );
  }

  if (path === '/student/careers' || path === '/student/career-workspace' || path === '/student/career-explorer') {
    return (
      <StudentLayout activeViewTitle="Career Workspace">
        <StudentCareerWorkspace />
      </StudentLayout>
    );
  }


  if (path === '/student/roadmaps') {
    return (
      <StudentLayout activeViewTitle="Career Roadmap">
        <StudentRoadmapWorkspace />
      </StudentLayout>
    );
  }

  if (path === '/student/learning') {
    return (
      <StudentLayout activeViewTitle="Learning & Courses">
        <StudentLearningWorkspace />
      </StudentLayout>
    );
  }

  if (path === '/student/internships') {
    return (
      <StudentLayout activeViewTitle="Internships & Projects">
        <StudentInternshipsWorkspace initialTab="opportunities" />
      </StudentLayout>
    );
  }

  if (path === '/student/applications') {
    return (
      <StudentLayout activeViewTitle="My Applications">
        <StudentInternshipsWorkspace initialTab="applications" />
      </StudentLayout>
    );
  }

  if (path === '/student/placements') {
    return (
      <StudentLayout activeViewTitle="Placement Drives">
        <StudentPlacementWorkspace />
      </StudentLayout>
    );
  }

  if (path === '/student/mentorship') {
    return (
      <StudentLayout activeViewTitle="Mentorship">
        <StudentMentorshipWorkspace />
      </StudentLayout>
    );
  }

  if (path === '/student/portfolio') {
    return (
      <StudentLayout activeViewTitle="Digital Portfolio">
        <StudentModulePlaceholder
          title="Verified Digital Skill Portfolio"
          subtitle="Comprehensive public and private career showcase for recruiters and employers."
          icon={Layers}
          domainModule="Module 10 — Portfolio & Showcase Engine"
          domainDescription="Curate your best GitHub repositories, deployed web applications, verified certifications, research papers, and competition awards into an authoritative digital portfolio."
          features={[
            "Project Showcase with GitHub & Live Demo Links",
            "Verified Skill Endorsement Seals",
            "Interactive Timeline of Achievements",
            "Public Shareable Portfolio URL with Privacy Controls",
            "Direct Export to PDF & Recruiter Dossier"
          ]}
        />
      </StudentLayout>
    );
  }

  if (path === '/student/resume') {
    return (
      <StudentLayout activeViewTitle="Resume Versions">
        <StudentModulePlaceholder
          title="Resume Management & Tailoring"
          subtitle="Create and manage tailored resume versions optimized for specific career roles."
          icon={FileText}
          domainModule="Module 10 — Resume Engine"
          domainDescription="Build ATS-friendly resume versions synced directly with your verified skill profile, project catalog, and academic milestones with cryptographic verification badges."
          features={[
            "Role-Targeted Resume Versioning",
            "ATS Compatibility & Keyword Verification",
            "One-Click Sync with Live Platform Portfolio",
            "Export to PDF and JSON Resume Standards",
            "Recruiter QR-Code Verification"
          ]}
        />
      </StudentLayout>
    );
  }

  if (path === '/student/achievements') {
    return (
      <StudentLayout activeViewTitle="Achievements">
        <StudentModulePlaceholder
          title="Recognitions & Achievements"
          subtitle="Maintain an official ledger of hackathon podiums, research recognitions, and awards."
          icon={Sparkles}
          domainModule="Module 10 — Recognition Registry"
          domainDescription="Record and verify academic honors, competition prizes, collegiate hackathon victories, patent filings, and co-curricular milestones."
          features={[
            "Verified Achievement Badges & Certificates",
            "Hackathon & Coding Contest Awards",
            "Institutional Honors & Dean's List Recognitions",
            "Social Sharing & LinkedIn Integration",
            "Automatic Portfolio Inclusion"
          ]}
        />
      </StudentLayout>
    );
  }

  if (path === '/student/community') {
    return (
      <StudentLayout activeViewTitle="Community">
        <StudentCommunityWorkspace />
      </StudentLayout>
    );
  }

  if (path === '/student/competitions') {
    return (
      <StudentLayout activeViewTitle="Competitions">
        <StudentCompetitionsWorkspace />
      </StudentLayout>
    );
  }

  if (path === '/student/ai-support' || path === '/student/recommendations') {
    return (
      <StudentLayout activeViewTitle="AI Recommendations">
        <RecommendationWorkspace />
      </StudentLayout>
    );
  }

  if (path === '/student/notifications') {
    return (
      <StudentLayout activeViewTitle="Notifications">
        <NotificationCenter userRole="STUDENT" />
      </StudentLayout>
    );
  }

  // Fallback to Dashboard
  return (
    <StudentLayout activeViewTitle="Dashboard">
      <StudentDashboard />
    </StudentLayout>
  );
}
