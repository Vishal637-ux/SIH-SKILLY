import React from 'react';
import PageContainer from '../components/PageContainer';
import Button from '../components/Button';
import { BookOpen, ArrowLeft, Clock, GraduationCap, CheckCircle2, Layers } from 'lucide-react';

export default function Training() {
  const trainingTracks = [
    {
      title: 'Full Stack Engineering Bootcamps',
      provider: 'College & Trainer Sync',
      type: 'Structured Cohort',
      desc: 'Hands-on training aligned with modern software stacks including React, Node.js, and cloud deployments.',
    },
    {
      title: 'Data Science & Applied ML Modules',
      provider: 'Academic Faculty & Industry Mentors',
      type: 'Hands-on Lab',
      desc: 'Practical statistical analysis, machine learning model building, and Big Data manipulation.',
    },
    {
      title: 'Core Hardware & IoT Workshops',
      provider: 'Engineering Labs',
      type: 'Practical Hardware',
      desc: 'Microcontroller programming, sensor integration, and embedded systems architecture.',
    },
  ];

  return (
    <PageContainer
      badge="Platform Module"
      title="Training Programs & Workshops"
      subtitle="Curriculum-aligned training programs, faculty-led cohorts, and skill upskilling modules."
    >
      <div className="space-y-10">
        
        {/* Module Status Card */}
        <div className="bg-white rounded-2xl border border-slate-200/80 p-8 text-center max-w-2xl mx-auto shadow-sm space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto border border-blue-200">
            <BookOpen className="w-7 h-7" />
          </div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-50 text-amber-700 border border-amber-200 text-xs font-semibold">
            <Clock className="w-3.5 h-3.5" />
            <span>Module Under Active Development</span>
          </div>
          <h2 className="text-2xl font-bold text-slate-900">Training Management Engine</h2>
          <p className="text-sm text-slate-600 leading-relaxed">
            The training enrollment system, cohort tracking, attendance verification, and trainer-led workshop hubs will be connected here in the upcoming phase.
          </p>
          <div className="pt-2">
            <Button to="/" variant="outline" size="md">
              <ArrowLeft className="w-4 h-4 mr-1.5" />
              <span>Back to Home</span>
            </Button>
          </div>
        </div>

        {/* Training Program Previews */}
        <div>
          <h3 className="text-lg font-bold text-slate-900 mb-4 text-center">
            Upcoming Training Program Types
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {trainingTracks.map((item, idx) => (
              <div key={idx} className="bg-white rounded-xl border border-slate-200 p-6 shadow-2xs space-y-3">
                <span className="badge-blue text-[11px]">{item.type}</span>
                <h4 className="text-base font-bold text-slate-900">{item.title}</h4>
                <p className="text-xs text-slate-500 leading-relaxed">{item.desc}</p>
                <div className="pt-2 text-xs text-slate-400 font-medium border-t border-slate-100 flex items-center gap-1.5">
                  <GraduationCap className="w-4 h-4 text-blue-500" />
                  <span>{item.provider}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </PageContainer>
  );
}
