import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  GraduationCap, 
  Target, 
  Award, 
  Briefcase, 
  Compass, 
  Sparkles, 
  CheckCircle2, 
  Clock, 
  ArrowRight, 
  AlertCircle, 
  Building2, 
  Layers, 
  TrendingUp, 
  BookOpen, 
  Users, 
  ChevronRight,
  Bell
} from 'lucide-react';
import api from '../../../lib/api';
import useAuth from '../../../hooks/useAuth';
import Button from '../../../components/Button';
import Loading from '../../../components/Loading';

export default function StudentDashboard() {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        setErrorMsg(null);
        const res = await api.get('/student/dashboard');
        setDashboardData(res.data);
      } catch (err) {
        console.error('Failed to load student dashboard:', err);
        setErrorMsg(err.response?.data?.detail || 'Failed to load student dashboard.');
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, []);

  if (loading) {
    return (
      <div className="min-h-[400px] flex items-center justify-center">
        <Loading message="Loading student dashboard metrics..." />
      </div>
    );
  }

  if (errorMsg) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-2xl flex items-center justify-between text-red-800">
        <div className="flex items-center gap-3">
          <AlertCircle className="w-6 h-6 text-red-600 shrink-0" />
          <div>
            <h3 className="font-bold text-sm">Dashboard Error</h3>
            <p className="text-xs text-red-700 mt-0.5">{errorMsg}</p>
          </div>
        </div>
        <Button onClick={() => window.location.reload()} variant="outline" size="sm">
          Retry
        </Button>
      </div>
    );
  }

  const u = dashboardData?.user || user;
  const p = u?.profile;
  const a = dashboardData?.academic_profile;
  const metrics = dashboardData?.metrics || {};
  const journey = dashboardData?.journey_status || {};

  const displayName = p?.first_name ? `${p.first_name} ${p.last_name || ''}`.trim() : u?.username || 'Student';
  const hasAcademicAffiliation = Boolean(a?.institution && a?.department);
  const targetRoleTitle = a?.target_career_role?.title;

  const journeySteps = [
    {
      id: 1,
      title: 'Profile & Academics',
      desc: hasAcademicAffiliation ? `${a.institution.name} • ${a.department.name}` : 'Setup college affiliation',
      isCompleted: Boolean(journey.profile_completed),
      link: '/student/profile',
    },
    {
      id: 2,
      title: 'Target Career Goal',
      desc: targetRoleTitle ? `Targeting: ${targetRoleTitle}` : 'Select your dream role',
      isCompleted: Boolean(journey.target_role_selected),
      link: '/student/careers',
    },

    {
      id: 3,
      title: 'Skill Assessment',
      desc: metrics.assessed_skills_count > 0 ? `${metrics.assessed_skills_count} skills verified` : 'Take diagnostic test',
      isCompleted: Boolean(journey.skills_assessed),
      link: '/student/assessments',
    },
    {
      id: 4,
      title: 'Roadmap & Learning',
      desc: metrics.active_roadmaps_count > 0 ? `${metrics.active_roadmaps_count} active roadmaps` : 'Follow tailored milestones',
      isCompleted: Boolean(journey.roadmap_active),
      link: '/student/roadmaps',
    },
    {
      id: 5,
      title: 'Internships & Placement',
      desc: metrics.applications_count > 0 ? `${metrics.applications_count} applications submitted` : 'Apply to live openings',
      isCompleted: Boolean(journey.internship_active),
      link: '/student/internships',
    },
  ];

  return (
    <div className="space-y-6 sm:space-y-8 animate-fadeIn">
      
      {/* 1. WELCOME & ACADEMIC BANNER */}
      <div className="bg-gradient-to-r from-blue-700 via-indigo-700 to-slate-900 rounded-3xl p-6 sm:p-8 text-white shadow-xl shadow-blue-900/10 relative overflow-hidden">
        {/* Background Accent Gradients */}
        <div className="absolute top-0 right-0 -mt-8 -mr-8 w-64 h-64 bg-blue-500/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-1/3 -mb-12 w-64 h-64 bg-indigo-500/20 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md border border-white/15 text-xs font-semibold text-blue-200">
              <Sparkles className="w-3.5 h-3.5 text-blue-300" />
              <span>SKILLY Student Career Hub</span>
            </div>
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-black tracking-tight">
              Welcome back, {displayName}!
            </h1>
            <p className="text-xs sm:text-sm text-blue-100/80 max-w-xl leading-relaxed">
              Track your verified competency passport, analyze skill gaps against target industry roles, and discover curated internships.
            </p>

            {/* Affiliation Badge */}
            <div className="pt-2 flex flex-wrap items-center gap-2 text-xs">
              {hasAcademicAffiliation ? (
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-white/15 border border-white/20 text-white font-medium">
                  <Building2 className="w-3.5 h-3.5 text-blue-300" />
                  <span>{a.institution.name} ({a.department.code})</span>
                  <span className="text-blue-200/60">•</span>
                  <span>Sem {a.current_semester}</span>
                  {a.cgpa && (
                    <>
                      <span className="text-blue-200/60">•</span>
                      <span>CGPA {a.cgpa}</span>
                    </>
                  )}
                </div>
              ) : (
                <Link
                  to="/student/profile"
                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-amber-400/20 border border-amber-400/40 text-amber-200 hover:bg-amber-400/30 transition-colors font-semibold"
                >
                  <AlertCircle className="w-3.5 h-3.5" />
                  <span>Complete Academic Profile</span>
                  <ChevronRight className="w-3 h-3" />
                </Link>
              )}

              {targetRoleTitle && (
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-emerald-400/20 border border-emerald-400/30 text-emerald-200 font-medium">
                  <Target className="w-3.5 h-3.5" />
                  <span>Target Role: {targetRoleTitle}</span>
                </div>
              )}
            </div>
          </div>

          {/* Quick Action Button */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 shrink-0">
            <Button to="/student/profile" variant="white" size="md" className="shadow-md">
              <span>Edit Profile</span>
              <ArrowRight className="w-4 h-4 ml-1.5" />
            </Button>
          </div>
        </div>
      </div>

      {/* 2. LIVE METRICS GRID (ZERO FAKE DATA) */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
        
        {/* Assessed Skills */}
        <div className="bg-white p-4 sm:p-5 rounded-2xl border border-slate-200/80 shadow-soft flex flex-col justify-between">
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mb-3">
            <Award className="w-5 h-5" />
          </div>
          <div>
            <div className="text-2xl font-black text-slate-900">{metrics.assessed_skills_count}</div>
            <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500 mt-0.5">Assessed Skills</div>
          </div>
        </div>

        {/* Skill Gaps */}
        <div className="bg-white p-4 sm:p-5 rounded-2xl border border-slate-200/80 shadow-soft flex flex-col justify-between">
          <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center mb-3">
            <TrendingUp className="w-5 h-5" />
          </div>
          <div>
            <div className="text-2xl font-black text-slate-900">{metrics.active_skill_gaps_count}</div>
            <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500 mt-0.5">Identified Gaps</div>
          </div>
        </div>

        {/* Roadmaps */}
        <div className="bg-white p-4 sm:p-5 rounded-2xl border border-slate-200/80 shadow-soft flex flex-col justify-between">
          <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center mb-3">
            <Compass className="w-5 h-5" />
          </div>
          <div>
            <div className="text-2xl font-black text-slate-900">{metrics.active_roadmaps_count}</div>
            <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500 mt-0.5">Active Roadmaps</div>
          </div>
        </div>

        {/* Applications */}
        <div className="bg-white p-4 sm:p-5 rounded-2xl border border-slate-200/80 shadow-soft flex flex-col justify-between">
          <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-3">
            <Briefcase className="w-5 h-5" />
          </div>
          <div>
            <div className="text-2xl font-black text-slate-900">{metrics.applications_count}</div>
            <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500 mt-0.5">Applications</div>
          </div>
        </div>

        {/* Internships */}
        <div className="bg-white p-4 sm:p-5 rounded-2xl border border-slate-200/80 shadow-soft flex flex-col justify-between">
          <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center mb-3">
            <GraduationCap className="w-5 h-5" />
          </div>
          <div>
            <div className="text-2xl font-black text-slate-900">{metrics.active_internships_count}</div>
            <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500 mt-0.5">Active Internships</div>
          </div>
        </div>

        {/* Recognitions */}
        <div className="bg-white p-4 sm:p-5 rounded-2xl border border-slate-200/80 shadow-soft flex flex-col justify-between">
          <div className="w-10 h-10 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center mb-3">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="text-2xl font-black text-slate-900">{metrics.recognitions_count}</div>
            <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500 mt-0.5">Achievements</div>
          </div>
        </div>

      </div>

      {/* 3. CAREER JOURNEY PROGRESS CARD */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-6 sm:p-8 shadow-soft space-y-5">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 border-b border-slate-100 pb-4">
          <div>
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Compass className="w-5 h-5 text-blue-600" />
              <span>Career Journey Roadmap</span>
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Follow the 5 progressive stages from foundational profile to campus & off-campus placement.
            </p>
          </div>
          <Link to="/student/journey" className="text-xs font-bold text-blue-600 hover:text-blue-700 flex items-center gap-1">
            <span>View Full Journey</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {/* Journey Timeline */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          {journeySteps.map((step) => (
            <Link
              key={step.id}
              to={step.link}
              className={`p-4 rounded-xl border text-left transition-all group flex flex-col justify-between ${
                step.isCompleted
                  ? 'border-emerald-200 bg-emerald-50/50 hover:bg-emerald-50'
                  : 'border-slate-200 hover:border-blue-300 hover:bg-slate-50'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className={`text-[10px] font-black uppercase tracking-wider px-2 py-0.5 rounded-md ${
                    step.isCompleted ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-700'
                  }`}>
                    Stage 0{step.id}
                  </span>
                  {step.isCompleted ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  ) : (
                    <Clock className="w-4 h-4 text-slate-400 group-hover:text-blue-600" />
                  )}
                </div>
                <h4 className="text-xs font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                  {step.title}
                </h4>
                <p className="text-[11px] text-slate-500 mt-1 leading-tight line-clamp-2">
                  {step.desc}
                </p>
              </div>

              <div className="pt-3 mt-2 border-t border-slate-200/60 flex items-center justify-between text-[10px] font-semibold text-slate-500 group-hover:text-blue-600">
                <span>{step.isCompleted ? 'Completed' : 'Action Required'}</span>
                <ChevronRight className="w-3 h-3" />
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* 4. TWO-COLUMN WORKSPACE: TARGET GOAL & ROADMAP */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Target Role & Skill Gap Card */}
        <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-soft space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Target className="w-4 h-4 text-blue-600" />
                <span>Target Career Benchmark</span>
              </h3>
              <Link to="/student/skill-gaps" className="text-xs text-blue-600 hover:text-blue-700 font-semibold">
                Skill Gaps
              </Link>
            </div>

            {targetRoleTitle ? (
              <div className="mt-4 p-4 rounded-xl bg-blue-50/70 border border-blue-100 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-900">{targetRoleTitle}</span>
                  <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-blue-600 text-white">
                    {a.target_career_role?.industry_domain || 'Tech'}
                  </span>
                </div>
                <p className="text-xs text-slate-600">
                  {a.target_career_role?.description || 'Personalized career benchmark linked to your profile.'}
                </p>
                <div className="pt-2 text-xs font-semibold text-blue-700 flex items-center justify-between">
                  <span>Skill gaps calculated: {metrics.active_skill_gaps_count}</span>
                  <Link to="/student/skill-gaps" className="hover:underline">
                    View Gap Analysis →
                  </Link>
                </div>
              </div>
            ) : (
              <div className="mt-4 p-6 rounded-xl border border-dashed border-slate-300 text-center space-y-3">
                <div className="w-10 h-10 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center mx-auto">
                  <Target className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-900">No Target Career Role Selected</h4>
                  <p className="text-[11px] text-slate-500 max-w-xs mx-auto mt-0.5">
                    Select a target role in your profile to trigger automatic skill gap analysis and tailored milestone roadmaps.
                  </p>
                </div>
                <Button to="/student/careers" variant="primary" size="sm">
                  Select Target Role
                </Button>

              </div>
            )}
          </div>

          <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
            <span>Powered by SKILLY Assessment Engine</span>
            <Link to="/student/assessments" className="text-blue-600 hover:underline font-medium">
              Take Diagnostic Test →
            </Link>
          </div>
        </div>

        {/* Active Learning Roadmap Card */}
        <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-soft space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Compass className="w-4 h-4 text-blue-600" />
                <span>Learning & Roadmap Progress</span>
              </h3>
              <Link to="/student/roadmaps" className="text-xs text-blue-600 hover:text-blue-700 font-semibold">
                All Roadmaps
              </Link>
            </div>

            {metrics.active_roadmaps_count > 0 ? (
              <div className="mt-4 p-4 rounded-xl bg-indigo-50/70 border border-indigo-100 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-900">Active Milestone Roadmap</span>
                  <span className="text-xs font-semibold text-indigo-700">
                    {metrics.completed_roadmap_steps_count} / {metrics.total_roadmap_steps_count} Completed
                  </span>
                </div>
                {/* Progress bar */}
                <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                  <div
                    className="bg-indigo-600 h-full rounded-full transition-all"
                    style={{
                      width: `${
                        metrics.total_roadmap_steps_count > 0
                          ? (metrics.completed_roadmap_steps_count / metrics.total_roadmap_steps_count) * 100
                          : 0
                      }%`,
                    }}
                  />
                </div>
                <div className="text-xs text-slate-600 flex items-center justify-between">
                  <span>Continue next milestone checkpoint</span>
                  <Link to="/student/roadmaps" className="text-indigo-600 hover:underline font-semibold">
                    Open Roadmap →
                  </Link>
                </div>
              </div>
            ) : (
              <div className="mt-4 p-6 rounded-xl border border-dashed border-slate-300 text-center space-y-3">
                <div className="w-10 h-10 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center mx-auto">
                  <Compass className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-900">No Active Roadmaps</h4>
                  <p className="text-[11px] text-slate-500 max-w-xs mx-auto mt-0.5">
                    Generate your structured skill development roadmap based on your diagnostic results.
                  </p>
                </div>
                <Button to="/student/roadmaps" variant="outline" size="sm">
                  Explore Roadmaps
                </Button>
              </div>
            )}
          </div>

          <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
            <span>Module 08 Skill Progression Engine</span>
            <Link to="/student/learning" className="text-blue-600 hover:underline font-medium">
              Browse Training Programs →
            </Link>
          </div>
        </div>

      </div>

      {/* 5. QUICK SHORTCUT CARDS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link
          to="/student/assessments"
          className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-soft hover:border-blue-300 hover:shadow-md transition-all group"
        >
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mb-3 group-hover:bg-blue-600 group-hover:text-white transition-colors">
            <Award className="w-5 h-5" />
          </div>
          <h4 className="text-sm font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
            Skill Assessment
          </h4>
          <p className="text-xs text-slate-500 mt-1 leading-relaxed">
            Take adaptive assessments to benchmark your competencies and verify skills.
          </p>
        </Link>

        <Link
          to="/student/internships"
          className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-soft hover:border-blue-300 hover:shadow-md transition-all group"
        >
          <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-3 group-hover:bg-emerald-600 group-hover:text-white transition-colors">
            <Briefcase className="w-5 h-5" />
          </div>
          <h4 className="text-sm font-bold text-slate-900 group-hover:text-emerald-600 transition-colors">
            Internships & Projects
          </h4>
          <p className="text-xs text-slate-500 mt-1 leading-relaxed">
            Discover matched industry internships, micro-projects, and campus hiring drives.
          </p>
        </Link>

        <Link
          to="/student/mentorship"
          className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-soft hover:border-blue-300 hover:shadow-md transition-all group"
        >
          <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center mb-3 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
            <Users className="w-5 h-5" />
          </div>
          <h4 className="text-sm font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">
            Expert Mentorship
          </h4>
          <p className="text-xs text-slate-500 mt-1 leading-relaxed">
            Book 1-on-1 career guidance sessions with verified alumni and industry leaders.
          </p>
        </Link>

        <Link
          to="/student/portfolio"
          className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-soft hover:border-blue-300 hover:shadow-md transition-all group"
        >
          <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center mb-3 group-hover:bg-purple-600 group-hover:text-white transition-colors">
            <Layers className="w-5 h-5" />
          </div>
          <h4 className="text-sm font-bold text-slate-900 group-hover:text-purple-600 transition-colors">
            Verified Passport
          </h4>
          <p className="text-xs text-slate-500 mt-1 leading-relaxed">
            Maintain your shareable digital skill portfolio and cryptographic resume versions.
          </p>
        </Link>
      </div>

    </div>
  );
}
