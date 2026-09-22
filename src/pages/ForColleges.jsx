import React from 'react';
import PageContainer from '../components/PageContainer';
import Button from '../components/Button';
import { 
  Building2, 
  BarChart3, 
  Users, 
  Briefcase, 
  GraduationCap, 
  Layers, 
  FileCheck2, 
  CheckCircle2,
  ArrowRight
} from 'lucide-react';

export default function ForColleges() {
  const collegeFeatures = [
    {
      title: 'Cohort Skill Visibility',
      desc: 'Gain real-time visibility into student skill readiness across departments, semesters, and individual batches.',
      icon: BarChart3,
    },
    {
      title: 'TPO Placement Management',
      desc: 'Easily filter eligible candidates by verified technical score cutoffs and coordinate corporate campus drives.',
      icon: Briefcase,
    },
    {
      title: 'Training & Curriculum Alignment',
      desc: 'Identify curriculum gaps early and assign targeted training modules to elevate batch-wide employability.',
      icon: Layers,
    },
    {
      title: 'Internship Oversight & Tracking',
      desc: 'Track and verify mandatory student internships, attendance, and project evaluations within a single portal.',
      icon: FileCheck2,
    },
    {
      title: 'Industry Partner Coordination',
      desc: 'Invite hiring companies to sponsor capstone challenges, review portfolios, and conduct on-campus hiring.',
      icon: Building2,
    },
    {
      title: 'Comprehensive Accreditation Reports',
      desc: 'Generate rich data reports on student skill progression and placement outcomes for accreditation bodies (e.g. NAAC, NBA).',
      icon: GraduationCap,
    },
  ];

  return (
    <PageContainer
      badge="Institutions & TPO Portal"
      title="For Colleges & Training Placement Officers"
      subtitle="Equip your institution with complete transparency into student competencies, streamline recruitment drives, and build robust industry ties."
    >
      <div className="space-y-16">
        
        {/* Banner Section */}
        <div className="bg-slate-900 text-white rounded-2xl p-8 sm:p-12">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            <div className="lg:col-span-8 space-y-4">
              <span className="badge-blue bg-blue-900 text-blue-300 border-blue-700">Higher Education Suite</span>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
                Transform Campus Placement & Skill Readiness
              </h2>
              <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
                SKILLY provides department heads, faculty trainers, and TPOs with an end-to-end management cockpit. Track skill readiness trends, manage internships seamlessly, and demonstrate tangible placement outcomes.
              </p>
              <div className="pt-2 flex flex-wrap gap-4">
                <Button to="/contact" variant="primary" size="lg">
                  Request Institution Demo
                </Button>
                <Button to="/register" variant="outline" size="lg" className="bg-slate-800 text-white border-slate-700 hover:bg-slate-700">
                  Register Institution
                </Button>
              </div>
            </div>

            <div className="lg:col-span-4 bg-slate-800/90 rounded-xl p-6 border border-slate-700 space-y-3 text-xs">
              <div className="font-bold text-slate-200 uppercase tracking-wider pb-2 border-b border-slate-700">
                Institutional Capabilities
              </div>
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Real-time Skill Gap Heatmaps</span>
              </div>
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Unified Campus Drive Coordination</span>
              </div>
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Internship Verification & Credits</span>
              </div>
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Outcome Analytics & NAAC/NBA Export</span>
              </div>
            </div>
          </div>
        </div>

        {/* Feature Grid */}
        <div>
          <div className="text-center max-w-2xl mx-auto mb-12 space-y-2">
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">
              Institutional Solutions
            </h2>
            <p className="text-slate-600 text-sm sm:text-base">
              Key operational pillars designed for placement officers, deans, and academic coordinators.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
            {collegeFeatures.map((item, idx) => {
              const Icon = item.icon;
              return (
                <div key={idx} className="bg-white rounded-2xl border border-slate-200/80 p-6 sm:p-7 card-hover shadow-xs">
                  <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center mb-4 border border-indigo-100">
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
