import React from 'react';
import PageContainer from '../components/PageContainer';
import Button from '../components/Button';
import { 
  CheckCircle2, 
  Target, 
  Compass, 
  FileCheck, 
  Briefcase, 
  Users, 
  Award, 
  Sparkles,
  TrendingUp,
  ArrowRight
} from 'lucide-react';

export default function ForStudents() {
  const benefits = [
    {
      title: 'Real Skill Awareness',
      desc: 'Understand exactly where your strengths lie and what areas need development through standardized assessments.',
      icon: Target,
    },
    {
      title: 'Skill Gap Identification',
      desc: 'See the exact delta between what you learn in class and what top tech companies require for hire.',
      icon: Compass,
    },
    {
      title: 'Actionable Roadmaps',
      desc: 'Follow clear, milestone-driven step-by-step paths designed by industry practitioners.',
      icon: TrendingUp,
    },
    {
      title: 'Verified Skill Passport',
      desc: 'Build a tamper-proof digital profile featuring verified project work and assessment scores.',
      icon: FileCheck,
    },
    {
      title: 'Real Internship Opportunities',
      desc: 'Apply directly for internships where your demonstrated skills match company requirements.',
      icon: Briefcase,
    },
    {
      title: 'Alumni & Peer Mentorship',
      desc: 'Connect with alumni who landed top jobs and receive direct feedback on your projects.',
      icon: Users,
    },
    {
      title: 'Placement Readiness',
      desc: 'Stand out during campus placement drives with verified competency proof instead of just resume claims.',
      icon: Award,
    },
    {
      title: 'AI Smart Guidance',
      desc: 'Receive tailored recommendations on the next high-value topic or project to tackle next.',
      icon: Sparkles,
    },
  ];

  return (
    <PageContainer
      badge="Student Career Pathway"
      title="For Students: Turn Your Hard Work Into Real Proof"
      subtitle="Say goodbye to confusing career advice and unverified resumes. SKILLY gives you a clear roadmap, verified skill credentials, and direct links to internships and placements."
    >
      <div className="space-y-16">
        
        {/* Core Value Proposition Box */}
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50/50 rounded-2xl border border-blue-200/80 p-8 sm:p-10">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            <div className="lg:col-span-8 space-y-4">
              <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
                Why Students Love SKILLY
              </h2>
              <p className="text-slate-600 text-base leading-relaxed">
                Whether you are in your first year exploring interests or in your final year preparing for campus placement drives, SKILLY guides you every step of the way with verified milestones and direct employer visibility.
              </p>
              <div className="pt-2">
                <Button to="/register" variant="primary" size="lg">
                  <span>Create Free Student Profile</span>
                  <ArrowRight className="w-4 h-4 ml-1.5" />
                </Button>
              </div>
            </div>
            
            <div className="lg:col-span-4 bg-white rounded-xl p-6 border border-slate-200/80 shadow-xs space-y-3">
              <div className="text-xs font-bold uppercase tracking-wider text-blue-600">Student Milestones</div>
              <div className="flex items-center gap-2.5 text-xs text-slate-700 font-medium">
                <span className="w-6 h-6 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-[11px]">1</span>
                <span>Self-Assessment & Diagnostic</span>
              </div>
              <div className="flex items-center gap-2.5 text-xs text-slate-700 font-medium">
                <span className="w-6 h-6 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-[11px]">2</span>
                <span>Milestone Project Completion</span>
              </div>
              <div className="flex items-center gap-2.5 text-xs text-slate-700 font-medium">
                <span className="w-6 h-6 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-[11px]">3</span>
                <span>Verified Skill Passport Issued</span>
              </div>
              <div className="flex items-center gap-2.5 text-xs text-slate-700 font-medium">
                <span className="w-6 h-6 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-[11px]">4</span>
                <span>Internship & Job Match</span>
              </div>
            </div>
          </div>
        </div>

        {/* 8 Benefit Cards */}
        <div>
          <div className="text-center max-w-2xl mx-auto mb-12 space-y-2">
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">
              Everything You Need to Succeed
            </h2>
            <p className="text-slate-600 text-sm sm:text-base">
              Explore key platform pillars engineered specifically for ambitious learners.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {benefits.map((item, idx) => {
              const Icon = item.icon;
              return (
                <div key={idx} className="bg-white rounded-2xl border border-slate-200/80 p-6 card-hover shadow-xs">
                  <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mb-4 border border-blue-100">
                    <Icon className="w-5 h-5" />
                  </div>
                  <h3 className="text-base font-bold text-slate-900 mb-2">
                    {item.title}
                  </h3>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    {item.desc}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Student FAQ / Callout */}
        <div className="bg-white rounded-2xl border border-slate-200 p-8 sm:p-10 shadow-sm">
          <div className="max-w-3xl space-y-4">
            <h3 className="text-xl sm:text-2xl font-bold text-slate-900">
              How does the Skill Passport help with job interviews?
            </h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Recruiters spend an average of 6 seconds skimming traditional resumes. A SKILLY Skill Passport gives recruiters direct, authenticated evidence of completed project code, rubric evaluations, and assessment scores, making it significantly easier to prove your capabilities and skip generic screening rounds.
            </p>
            <div className="pt-2">
              <Button to="/portfolio" variant="secondary" size="md">
                View Sample Skill Passport Structure
              </Button>
            </div>
          </div>
        </div>

      </div>
    </PageContainer>
  );
}
