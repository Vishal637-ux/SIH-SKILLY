import React from 'react';
import PageContainer from '../components/PageContainer';
import Button from '../components/Button';
import { 
  Trophy, 
  ArrowLeft, 
  Clock, 
  Users, 
  Code2, 
  Calendar, 
  Medal, 
  UserPlus, 
  Sparkles,
  CheckCircle2
} from 'lucide-react';

export default function Competitions() {
  const pillars = [
    {
      title: 'Competitions & Challenges',
      desc: 'Industry-sponsored engineering competitions and algorithm tournaments with verified judging criteria.',
      icon: Trophy,
      tag: 'Competitions',
    },
    {
      title: 'Hackathons & Sprints',
      desc: 'Timed 24-48h hackathons solving real problem statements proposed by partnered companies and colleges.',
      icon: Code2,
      tag: 'Hackathons',
    },
    {
      title: 'Registration & Eligibility',
      desc: 'Seamless one-click student registration with automated eligibility verification based on skill levels.',
      icon: UserPlus,
      tag: 'Registration',
    },
    {
      title: 'Team Formation & Collaboration',
      desc: 'Create multi-disciplinary teams, invite peers across departments, and coordinate repository submissions.',
      icon: Users,
      tag: 'Teams',
    },
    {
      title: 'Active Participation & Submissions',
      desc: 'Submit deliverables, GitHub repositories, live demo URLs, and presentation slide decks in real-time.',
      icon: Calendar,
      tag: 'Participation',
    },
    {
      title: 'Results & Verified Recognition',
      desc: 'Rankings, judge evaluations, digital certificates, and direct Skill Passport achievement badges.',
      icon: Medal,
      tag: 'Recognition',
    },
  ];

  return (
    <PageContainer
      badge="Platform Module"
      title="Competitions & Hackathons Hub"
      subtitle="Participate in collegiate hackathons, form student teams, submit practical solutions, and earn verified recognition."
    >
      <div className="space-y-12">
        
        {/* Module Status Card */}
        <div className="bg-white rounded-2xl border border-slate-200/80 p-8 text-center max-w-2xl mx-auto shadow-sm space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center mx-auto border border-amber-200">
            <Trophy className="w-7 h-7" />
          </div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-50 text-amber-700 border border-amber-200 text-xs font-semibold">
            <Clock className="w-3.5 h-3.5" />
            <span>Module Under Active Development</span>
          </div>
          <h2 className="text-2xl font-bold text-slate-900">Competition & Hackathon Engine</h2>
          <p className="text-sm text-slate-600 leading-relaxed">
            The full interactive hackathon registration, matchmaking team builder, live leaderboard, and judge evaluation portal will be implemented here.
          </p>
          <div className="pt-2">
            <Button to="/" variant="outline" size="md">
              <ArrowLeft className="w-4 h-4 mr-1.5" />
              <span>Back to Home</span>
            </Button>
          </div>
        </div>

        {/* 6 Core Functional Areas */}
        <div>
          <div className="text-center max-w-2xl mx-auto mb-8 space-y-2">
            <h3 className="text-2xl font-bold text-slate-900">Supported Competition Workflow</h3>
            <p className="text-sm text-slate-600">
              Complete end-to-end framework from event discovery to verified digital badges.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {pillars.map((item, idx) => {
              const Icon = item.icon;
              return (
                <div key={idx} className="bg-white rounded-2xl border border-slate-200/80 p-6 card-hover shadow-xs flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center border border-amber-100">
                        <Icon className="w-5 h-5" />
                      </div>
                      <span className="badge-blue text-[11px]">{item.tag}</span>
                    </div>
                    <h4 className="text-base font-bold text-slate-900 mb-1.5">{item.title}</h4>
                    <p className="text-xs text-slate-600 leading-relaxed">{item.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

      </div>
    </PageContainer>
  );
}
