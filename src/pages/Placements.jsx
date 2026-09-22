import React from 'react';
import PageContainer from '../components/PageContainer';
import Button from '../components/Button';
import { Award, ArrowLeft, Clock, Building2, CheckCircle2, ShieldCheck } from 'lucide-react';

export default function Placements() {
  const placementPillars = [
    {
      title: 'Skill-Verified Shortlisting',
      desc: 'Hiring partners filter candidates based on authenticated assessment scores rather than self-declared resume claims.',
      icon: ShieldCheck,
    },
    {
      title: 'Campus & Off-Campus Drives',
      desc: 'Centralized drive management connecting TPOs and students with corporate recruitment calendars.',
      icon: Building2,
    },
    {
      title: 'Interview & Offer Tracking',
      desc: 'Full lifecycle tracking from application submission to technical interview rounds and formal offer acceptance.',
      icon: CheckCircle2,
    },
  ];

  return (
    <PageContainer
      badge="Platform Module"
      title="Placements & Recruitment Hub"
      subtitle="Corporate hiring drives, skill-matched candidate shortlisting, and placement coordination."
    >
      <div className="space-y-10">
        
        {/* Module Status Card */}
        <div className="bg-white rounded-2xl border border-slate-200/80 p-8 text-center max-w-2xl mx-auto shadow-sm space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center mx-auto border border-amber-200">
            <Award className="w-7 h-7" />
          </div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-50 text-amber-700 border border-amber-200 text-xs font-semibold">
            <Clock className="w-3.5 h-3.5" />
            <span>Module Under Active Development</span>
          </div>
          <h2 className="text-2xl font-bold text-slate-900">Placement Coordination Hub</h2>
          <p className="text-sm text-slate-600 leading-relaxed">
            The placement drive management system, recruiter shortlisting cockpit, and offer verification pipeline will be integrated here with the FastAPI backend.
          </p>
          <div className="pt-2">
            <Button to="/" variant="outline" size="md">
              <ArrowLeft className="w-4 h-4 mr-1.5" />
              <span>Back to Home</span>
            </Button>
          </div>
        </div>

        {/* Pillars Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {placementPillars.map((pillar, idx) => {
            const Icon = pillar.icon;
            return (
              <div key={idx} className="bg-white rounded-xl border border-slate-200 p-6 shadow-2xs space-y-2">
                <div className="w-10 h-10 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center mb-3">
                  <Icon className="w-5 h-5" />
                </div>
                <h4 className="text-base font-bold text-slate-900">{pillar.title}</h4>
                <p className="text-xs text-slate-500 leading-relaxed">{pillar.desc}</p>
              </div>
            );
          })}
        </div>

      </div>
    </PageContainer>
  );
}
