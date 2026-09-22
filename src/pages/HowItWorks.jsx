import React from 'react';
import PageContainer from '../components/PageContainer';
import Button from '../components/Button';
import { 
  Target, 
  GitPullRequest, 
  Compass, 
  BookOpen, 
  Briefcase, 
  Users, 
  Award, 
  TrendingUp,
  CheckCircle2,
  ArrowDown
} from 'lucide-react';

export default function HowItWorks() {
  const steps = [
    {
      num: '01',
      title: 'Skill Assessment',
      subtitle: 'Benchmark your current foundational and technical capabilities.',
      icon: Target,
      desc: 'Students participate in standardized diagnostic evaluations across fundamental computer science, software engineering, domain subjects, and problem-solving. This sets the verified baseline.',
      keyOutcomes: ['Baseline competency score', 'Subject strength breakdown', 'Initial profile creation'],
    },
    {
      num: '02',
      title: 'Skill Gap Analysis',
      subtitle: 'Compare personal benchmarks against industry role expectations.',
      icon: GitPullRequest,
      desc: 'The platform analyzes the differences between current student proficiencies and target industry job criteria, highlighting exact topics, tools, and practices needed to become job-ready.',
      keyOutcomes: ['Target role competency map', 'Identified skill bottlenecks', 'Priority focus list'],
    },
    {
      num: '03',
      title: 'Career Roadmap',
      subtitle: 'Receive a personalized, milestone-driven progression trajectory.',
      icon: Compass,
      desc: 'A structured sequential roadmap is generated to navigate from baseline to career readiness, organized into practical checkpoints and manageable learning phases.',
      keyOutcomes: ['Phase-by-phase timeline', 'Milestone checkpoints', 'Curriculum alignment'],
    },
    {
      num: '04',
      title: 'Targeted Learning',
      subtitle: 'Acquire knowledge through verified course modules and trainer sync.',
      icon: BookOpen,
      desc: 'Students work through curated learning content, college courses, and trainer-led workshops that directly target the identified gaps.',
      keyOutcomes: ['Modular concept completion', 'Trainer feedback', 'Formative check quizzes'],
    },
    {
      num: '05',
      title: 'Internships & Projects',
      subtitle: 'Build tangible, verifiable project evidence and gain work experience.',
      icon: Briefcase,
      desc: 'Put theory into practice by developing capstone projects or securing verified corporate internships through the platform, adding verifiable evidence to the Skill Passport.',
      keyOutcomes: ['Verified repository commits', 'Employer project evaluations', 'Skill Passport credential updates'],
    },
    {
      num: '06',
      title: 'Mentorship',
      subtitle: 'Get actionable guidance from experienced alumni and industry mentors.',
      icon: Users,
      desc: 'Connect directly with senior professionals and alumni who have walked the same path, receiving code reviews, mock interview feedback, and career guidance.',
      keyOutcomes: ['1-on-1 feedback sessions', 'Portfolio critique', 'Industry perspective'],
    },
    {
      num: '07',
      title: 'Placement Drives',
      subtitle: 'Participate in skill-matched recruitment drives.',
      icon: Award,
      desc: 'TPOs and corporate recruiters use verified student skill passports to shortlist candidates for on-campus and off-campus recruitment drives based on demonstrated proof.',
      keyOutcomes: ['Role-matched interview calls', 'Verified skill endorsement', 'Job offer tracking'],
    },
    {
      num: '08',
      title: 'Continuous Career Growth',
      subtitle: 'Stay connected, upskill continuously, and give back as an alumnus.',
      icon: TrendingUp,
      desc: 'Even after securing a role, the SKILLY journey continues as graduates upskill for advanced roles and return to mentor upcoming batches.',
      keyOutcomes: ['Alumni network access', 'Advanced skill upskilling', 'Giving back as a mentor'],
    },
  ];

  return (
    <PageContainer
      badge="Step-by-Step Methodology"
      title="How SKILLY Works"
      subtitle="A seamless 8-stage lifecycle converting education into verifiable capability, industry experience, and lifelong career growth."
    >
      <div className="space-y-12">
        
        {/* Step-by-Step Pathway */}
        <div className="space-y-8 relative">
          {steps.map((step, idx) => {
            const Icon = step.icon;
            return (
              <div key={idx} className="relative">
                <div className="bg-white rounded-2xl border border-slate-200/80 p-6 sm:p-8 shadow-xs hover:border-blue-200 transition-colors">
                  <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
                    
                    {/* Step Number & Icon */}
                    <div className="lg:col-span-1 flex items-center lg:flex-col justify-between lg:justify-start gap-3">
                      <span className="text-3xl font-black text-blue-600">{step.num}</span>
                      <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center border border-blue-100">
                        <Icon className="w-5 h-5" />
                      </div>
                    </div>

                    {/* Step Main Details */}
                    <div className="lg:col-span-7 space-y-2">
                      <h3 className="text-xl font-bold text-slate-900">{step.title}</h3>
                      <p className="text-sm font-medium text-blue-600">{step.subtitle}</p>
                      <p className="text-sm text-slate-600 leading-relaxed pt-1">{step.desc}</p>
                    </div>

                    {/* Key Outcomes Box */}
                    <div className="lg:col-span-4 bg-slate-50 rounded-xl p-4 border border-slate-200/70">
                      <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                        Key Deliverables
                      </h4>
                      <ul className="space-y-1.5 text-xs text-slate-600">
                        {step.keyOutcomes.map((item, oIdx) => (
                          <li key={oIdx} className="flex items-center gap-2">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                  </div>
                </div>

                {/* Connecting arrow if not last item */}
                {idx < steps.length - 1 && (
                  <div className="flex justify-center my-3 text-slate-300">
                    <ArrowDown className="w-5 h-5" />
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* CTA */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-8 text-center text-white space-y-4">
          <h3 className="text-2xl font-bold text-white">Begin Your SKILLY Journey Today</h3>
          <p className="text-sm text-blue-100 max-w-lg mx-auto">
            Take your first diagnostic skill assessment and unlock your personalized roadmap.
          </p>
          <div className="pt-2">
            <Button to="/register" variant="white" size="lg" className="font-bold">
              Start Free Assessment
            </Button>
          </div>
        </div>

      </div>
    </PageContainer>
  );
}
