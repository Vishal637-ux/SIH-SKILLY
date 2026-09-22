import React from 'react';
import PageContainer from '../components/PageContainer';
import Button from '../components/Button';
import { 
  Building2, 
  Briefcase, 
  Target, 
  Users, 
  Sparkles, 
  FileCheck, 
  Code2, 
  CheckCircle2,
  ArrowRight
} from 'lucide-react';

export default function ForIndustry() {
  const industryPillars = [
    {
      title: 'Precision Skill Matching',
      desc: 'Define your exact tech stacks and required proficiency cutoffs to instantly match with pre-assessed candidates.',
      icon: Target,
    },
    {
      title: 'Direct Internship & Job Posting',
      desc: 'Publish openings directly to partnered academic institutions and receive applications backed by verifiable proof.',
      icon: Briefcase,
    },
    {
      title: 'Sponsor Real-World Projects',
      desc: 'Provide problem statements and challenges to student cohorts to evaluate engineering ability in realistic contexts.',
      icon: Code2,
    },
    {
      title: 'Streamlined Campus Drives',
      desc: 'Coordinate joint placement drives across multiple accredited colleges without fragmented email chains.',
      icon: Building2,
    },
    {
      title: 'Verified Candidate Portfolios',
      desc: 'Review authenticated Git repositories, rubric ratings, and skill passport records before the first interview.',
      icon: FileCheck,
    },
    {
      title: 'Industry Mentorship & Workshops',
      desc: 'Engage your senior engineers as mentors, hosting masterclasses and building employer brand loyalty.',
      icon: Users,
    },
  ];

  return (
    <PageContainer
      badge="Corporate & Recruiting Suite"
      title="For Industry & Enterprise Hiring Partners"
      subtitle="Hire early-career talent with confidence. Access pre-assessed candidates, evaluate practical project evidence, and build direct pipelines with leading institutions."
    >
      <div className="space-y-16">
        
        {/* Hero Card */}
        <div className="bg-gradient-to-r from-slate-900 to-blue-950 text-white rounded-2xl p-8 sm:p-12">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            <div className="lg:col-span-8 space-y-4">
              <span className="badge-blue bg-blue-900 text-blue-200 border-blue-700">Talent Acquisition</span>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
                Eliminate Resume Guesswork with Verifiable Proof
              </h2>
              <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
                Traditional hiring is bogged down by unvetted resumes and high screening costs. SKILLY provides recruiters with direct access to pre-evaluated student competencies, verified repository evidence, and direct campus pipelines.
              </p>
              <div className="pt-2 flex flex-wrap gap-4">
                <Button to="/register" variant="primary" size="lg">
                  <span>Register Company Profile</span>
                  <ArrowRight className="w-4 h-4 ml-1.5" />
                </Button>
                <Button to="/contact" variant="outline" size="lg" className="bg-slate-800 text-white border-slate-700 hover:bg-slate-700">
                  Talk to Enterprise Team
                </Button>
              </div>
            </div>

            <div className="lg:col-span-4 bg-slate-800/80 rounded-xl p-6 border border-slate-700 space-y-3 text-xs">
              <div className="font-bold text-slate-200 uppercase tracking-wider pb-2 border-b border-slate-700">
                Recruiter Advantages
              </div>
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-blue-400 shrink-0" />
                <span>Zero Self-Reported Resume Inflation</span>
              </div>
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-blue-400 shrink-0" />
                <span>Standardized Technical Benchmarks</span>
              </div>
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-blue-400 shrink-0" />
                <span>Direct Access to Top Academic Cohorts</span>
              </div>
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-blue-400 shrink-0" />
                <span>Lower Time-to-Hire & Higher Retention</span>
              </div>
            </div>
          </div>
        </div>

        {/* 6 Industry Pillars */}
        <div>
          <div className="text-center max-w-2xl mx-auto mb-12 space-y-2">
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">
              Complete Corporate Engagement Toolkit
            </h2>
            <p className="text-slate-600 text-sm sm:text-base">
              Everything required to source, evaluate, and onboard fresh graduates and interns.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
            {industryPillars.map((item, idx) => {
              const Icon = item.icon;
              return (
                <div key={idx} className="bg-white rounded-2xl border border-slate-200/80 p-6 sm:p-7 card-hover shadow-xs">
                  <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mb-4 border border-blue-100">
                    <Icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-lg font-bold text-slate-900 mb-2">
                    {item.title}
                  </h3>
                  <p className="text-sm text-slate-600 leading-relaxed">
                    {item.desc}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

      </div>
    </PageContainer>
  );
}
