import React from 'react';
import PageContainer from '../components/PageContainer';
import Button from '../components/Button';
import { Target, ArrowLeft, Clock, Code2, LineChart, Cpu, Palette } from 'lucide-react';

export default function Skills() {
  const tracks = [
    { title: 'Web Development', icon: Code2, desc: 'Frontend, backend, database architectures, and REST APIs.' },
    { title: 'Data Science & AI', icon: LineChart, desc: 'Analytics, machine learning models, and data pipelines.' },
    { title: 'Core Engineering', icon: Cpu, desc: 'Embedded systems, IoT, electronics, and robotics.' },
    { title: 'Design & Product', icon: Palette, desc: 'UI/UX workflows, Figma prototypes, and design systems.' },
  ];

  return (
    <PageContainer
      badge="Platform Module"
      title="Skills & Assessment Engine"
      subtitle="Standardized competency assessments, skill gap mapping, and benchmark analytics."
    >
      <div className="space-y-10">
        
        {/* Module Status Card */}
        <div className="bg-white rounded-2xl border border-slate-200/80 p-8 text-center max-w-2xl mx-auto shadow-sm space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto border border-blue-200">
            <Target className="w-7 h-7" />
          </div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-50 text-amber-700 border border-amber-200 text-xs font-semibold">
            <Clock className="w-3.5 h-3.5" />
            <span>Module In Development</span>
          </div>
          <h2 className="text-2xl font-bold text-slate-900">Skill Assessment Portal</h2>
          <p className="text-sm text-slate-600 leading-relaxed">
            The full interactive assessment engine, timed coding challenges, and adaptive diagnostic tests will be connected here in the next phase.
          </p>
          <div className="pt-2">
            <Button to="/" variant="outline" size="md">
              <ArrowLeft className="w-4 h-4 mr-1.5" />
              <span>Back to Home</span>
            </Button>
          </div>
        </div>

        {/* Preview of Tracks */}
        <div>
          <h3 className="text-lg font-bold text-slate-900 mb-4 text-center">
            Upcoming Assessment Tracks
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {tracks.map((t, idx) => {
              const Icon = t.icon;
              return (
                <div key={idx} className="bg-white rounded-xl border border-slate-200 p-5 shadow-2xs">
                  <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center mb-3">
                    <Icon className="w-5 h-5" />
                  </div>
                  <h4 className="text-base font-bold text-slate-900 mb-1">{t.title}</h4>
                  <p className="text-xs text-slate-500 leading-relaxed">{t.desc}</p>
                </div>
              );
            })}
          </div>
        </div>

      </div>
    </PageContainer>
  );
}
