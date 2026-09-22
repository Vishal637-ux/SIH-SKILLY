import React from 'react';
import { Link } from 'react-router-dom';
import { Check, Sparkles, Building2, GraduationCap, ArrowRight } from 'lucide-react';
import Button from '../components/Button';

export default function Pricing() {
  const plans = [
    {
      name: 'Students',
      desc: 'Complete personal skill passport, milestone learning, & placement matching.',
      price: 'Free',
      period: 'Forever',
      badge: 'Popular for Learners',
      features: [
        'Personalized Skill Gap Diagnostic',
        'Unlimited Skill Roadmap Access',
        'Verified Skill Passport & Portfolio',
        'Internship & Entry Level Job Applications',
        'Community & Alumni Mentorship Access'
      ],
      buttonText: 'Build Free Skill Profile',
      buttonVariant: 'primary',
      highlight: false
    },
    {
      name: 'Colleges & TPOs',
      desc: 'Institutional cohort skill analytics, AICTE/NAAC audit trails, & drive automation.',
      price: 'Custom',
      period: 'Per Student / Year',
      badge: 'Most Popular for Campus',
      features: [
        'Department & Batch Level Skill Dashboards',
        'One-Click NAAC/AICTE Audit Reports',
        'Placement Drive Automation & Filtering',
        'Trainer Curriculum Sync & Grading',
        'Dedicated Campus Success Manager'
      ],
      buttonText: 'Request Campus Demo',
      buttonVariant: 'primary',
      highlight: true
    },
    {
      name: 'Industry & Partners',
      desc: 'Direct skill-backed recruitment, pre-vetted candidates, & project sponsorship.',
      price: 'Custom',
      period: 'Per Hiring Drive / Annual',
      badge: 'For Hiring Managers',
      features: [
        'Skill-Based Candidate Match Engine',
        'Verified Project & Evaluation Records',
        'Direct Campus Placement Drive Posting',
        'Custom Live Internship Sponsorship',
        'Priority Technical Screening Pipeline'
      ],
      buttonText: 'Contact Hiring Team',
      buttonVariant: 'outline',
      highlight: false
    }
  ];

  return (
    <div className="pt-10 pb-24 space-y-16">
      
      {/* Header */}
      <div className="text-center max-w-3xl mx-auto px-4 space-y-4">
        <span className="badge-blue">Transparent Ecosystem Pricing</span>
        <h1 className="text-4xl sm:text-5xl font-black text-slate-900 tracking-tight">
          Empowering Academia & Industry Together
        </h1>
        <p className="text-lg text-slate-600">
          Free for every student. Tailored institutional plans for colleges, TPOs, and corporate hiring partners.
        </p>
      </div>

      {/* Pricing Cards */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan, idx) => (
            <div 
              key={idx}
              className={`rounded-3xl border p-8 flex flex-col justify-between transition-all ${
                plan.highlight 
                  ? 'bg-slate-900 text-white border-blue-600 shadow-2xl relative scale-105' 
                  : 'bg-white text-slate-900 border-slate-200 shadow-sm hover:shadow-md'
              }`}
            >
              <div>
                {plan.badge && (
                  <span className={`inline-block text-[11px] font-bold px-3 py-1 rounded-full mb-4 ${
                    plan.highlight 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-blue-50 text-blue-700 border border-blue-200'
                  }`}>
                    {plan.badge}
                  </span>
                )}
                
                <h3 className="text-2xl font-bold mb-1">{plan.name}</h3>
                <p className={`text-xs mb-6 ${plan.highlight ? 'text-slate-300' : 'text-slate-500'}`}>
                  {plan.desc}
                </p>

                <div className="mb-6">
                  <span className="text-4xl font-extrabold">{plan.price}</span>
                  <span className={`text-xs ml-2 ${plan.highlight ? 'text-slate-400' : 'text-slate-500'}`}>
                    / {plan.period}
                  </span>
                </div>

                <ul className="space-y-3 mb-8 text-sm">
                  {plan.features.map((feat, fIdx) => (
                    <li key={fIdx} className="flex items-start gap-2.5">
                      <Check className={`w-4 h-4 mt-0.5 shrink-0 ${plan.highlight ? 'text-blue-400' : 'text-blue-600'}`} />
                      <span className={plan.highlight ? 'text-slate-200' : 'text-slate-700'}>{feat}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <Link 
                to="/register" 
                className={`w-full py-3 rounded-full text-center text-sm font-bold transition-all shadow-sm ${
                  plan.highlight 
                    ? 'bg-blue-600 hover:bg-blue-500 text-white' 
                    : 'bg-slate-900 hover:bg-slate-800 text-white'
                }`}
              >
                {plan.buttonText}
              </Link>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
