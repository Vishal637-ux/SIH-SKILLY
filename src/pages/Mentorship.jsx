import React from 'react';
import PageContainer from '../components/PageContainer';
import Button from '../components/Button';
import { Users, ArrowLeft, Clock, MessageSquare, Calendar, Star } from 'lucide-react';

export default function Mentorship() {
  const mentorTracks = [
    {
      title: '1-on-1 Guidance Sessions',
      desc: 'Schedule dedicated office hours with experienced alumni and industry senior engineers for personalized advice.',
      icon: Calendar,
    },
    {
      title: 'Project & Code Reviews',
      desc: 'Submit repository links and capstone projects for thorough rubric-based critique from domain veterans.',
      icon: Star,
    },
    {
      title: 'Ask-Me-Anything & Webinars',
      desc: 'Join interactive group AMAs covering specific career trajectories, interview prep, and industry trends.',
      icon: MessageSquare,
    },
  ];

  return (
    <PageContainer
      badge="Platform Module"
      title="Mentorship & Expert Network"
      subtitle="Connect with experienced alumni, industry practitioners, and specialized technical mentors."
    >
      <div className="space-y-10">
        
        {/* Module Status Card */}
        <div className="bg-white rounded-2xl border border-slate-200/80 p-8 text-center max-w-2xl mx-auto shadow-sm space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-purple-50 text-purple-600 flex items-center justify-center mx-auto border border-purple-200">
            <Users className="w-7 h-7" />
          </div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-50 text-amber-700 border border-amber-200 text-xs font-semibold">
            <Clock className="w-3.5 h-3.5" />
            <span>Module Under Active Development</span>
          </div>
          <h2 className="text-2xl font-bold text-slate-900">Mentorship Management Hub</h2>
          <p className="text-sm text-slate-600 leading-relaxed">
            The mentor directory, session scheduling calendar, video room integrations, and review feedback tracking will be implemented here.
          </p>
          <div className="pt-2">
            <Button to="/" variant="outline" size="md">
              <ArrowLeft className="w-4 h-4 mr-1.5" />
              <span>Back to Home</span>
            </Button>
          </div>
        </div>

        {/* Feature Highlights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {mentorTracks.map((item, idx) => {
            const Icon = item.icon;
            return (
              <div key={idx} className="bg-white rounded-xl border border-slate-200 p-6 shadow-2xs space-y-2">
                <div className="w-10 h-10 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center mb-3">
                  <Icon className="w-5 h-5" />
                </div>
                <h4 className="text-base font-bold text-slate-900">{item.title}</h4>
                <p className="text-xs text-slate-500 leading-relaxed">{item.desc}</p>
              </div>
            );
          })}
        </div>

      </div>
    </PageContainer>
  );
}
