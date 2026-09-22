import React from 'react';
import PageContainer from '../components/PageContainer';
import Button from '../components/Button';
import { 
  Target, 
  Compass, 
  Rocket, 
  BookOpen, 
  Briefcase, 
  Code2, 
  Users, 
  FileCheck, 
  Award, 
  Sparkles, 
  MessageSquare,
  ArrowRight
} from 'lucide-react';

export default function Features() {
  const featureList = [
    {
      title: 'Skill Assessment',
      desc: 'Accurately benchmark and evaluate student capabilities across core technical, domain-specific, and problem-solving disciplines.',
      icon: Target,
      tag: 'Diagnostics',
      details: ['Diagnostic topic quizzes', 'Coding & practical challenges', 'Standardized scoring metrics'],
    },
    {
      title: 'Skill Mapping',
      desc: 'Dynamically map individual skill proficiencies to contemporary industry role criteria and hiring requirements.',
      icon: Compass,
      tag: 'Alignment',
      details: ['Role-to-skill frameworks', 'Competency matrices', 'Marketplace alignment'],
    },
    {
      title: 'Career Roadmap',
      desc: 'Provide structured, stage-by-stage learning trajectories tailored to the specific role aspirations of each student.',
      icon: Rocket,
      tag: 'Navigation',
      details: ['Sequential milestones', 'Curated learning steps', 'Progress checkpoints'],
    },
    {
      title: 'Guided Learning',
      desc: 'Deliver targeted modular coursework and hands-on modules aligned with verified institutional curricula.',
      icon: BookOpen,
      tag: 'Education',
      details: ['Topic modules', 'Self-paced exercises', 'Faculty and trainer coordination'],
    },
    {
      title: 'Internship Discovery',
      desc: 'Connect students with vetted real-world internship opportunities corresponding to their verified skill proficiencies.',
      icon: Briefcase,
      tag: 'Experience',
      details: ['Verified company listings', 'Skill-matched applications', 'Internship milestone tracking'],
    },
    {
      title: 'Practical Projects',
      desc: 'Enable students to work on industry-sponsored and open challenge projects to build demonstrable evidence.',
      icon: Code2,
      tag: 'Proof',
      details: ['Capstone assignments', 'Repository link verification', 'Peer review rubrics'],
    },
    {
      title: 'Mentorship Network',
      desc: 'Facilitate direct 1-on-1 and group mentorship sessions with verified industry veterans and college alumni.',
      icon: Users,
      tag: 'Guidance',
      details: ['Alumni connect', 'Office hours scheduling', 'Career advice forums'],
    },
    {
      title: 'Skill Passport & Portfolio',
      desc: 'Maintain a tamper-proof digital record of verified projects, assessments, and verifiable evidence.',
      icon: FileCheck,
      tag: 'Credentials',
      details: ['Digital skill badges', 'Verified project repository', 'Shareable profile link'],
    },
    {
      title: 'Placement Coordination',
      desc: 'Streamline the recruitment pipeline for colleges and enterprises with skill-filtered candidate matching.',
      icon: Award,
      tag: 'Outcomes',
      details: ['TPO drive management', 'Candidate shortlisting', 'Interview scheduling'],
    },
    {
      title: 'AI Recommendations',
      desc: 'Leverage intelligent heuristics to suggest the optimal next learning milestone, project, or career role.',
      icon: Sparkles,
      tag: 'Intelligence',
      details: ['Next-step roadmap hints', 'Gap closure suggestions', 'Personalized track matching'],
    },
    {
      title: 'Community & Peer Networking',
      desc: 'Foster collaborative learning groups, knowledge sharing, and peer-to-peer technical discussions.',
      icon: MessageSquare,
      tag: 'Ecosystem',
      details: ['Topic-based forums', 'Study groups', 'Campus event announcements'],
    },
  ];

  return (
    <PageContainer
      badge="Platform Capabilities"
      title="Comprehensive Platform Features"
      subtitle="Discover the end-to-end suite of tools created to power skill mapping, structured roadmaps, verifiable credentials, and placement success."
    >
      <div className="space-y-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
          {featureList.map((item, idx) => {
            const Icon = item.icon;
            return (
              <div 
                key={idx} 
                className="bg-white rounded-2xl border border-slate-200/80 p-6 sm:p-7 card-hover flex flex-col justify-between shadow-xs"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center border border-blue-100">
                      <Icon className="w-6 h-6" />
                    </div>
                    <span className="badge-blue">{item.tag}</span>
                  </div>

                  <h3 className="text-xl font-bold text-slate-900 mb-2">
                    {item.title}
                  </h3>

                  <p className="text-sm text-slate-600 leading-relaxed mb-6">
                    {item.desc}
                  </p>
                </div>

                <div className="pt-4 border-t border-slate-100">
                  <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">Key Highlights</h4>
                  <ul className="space-y-1.5 text-xs text-slate-600">
                    {item.details.map((detail, dIdx) => (
                      <li key={dIdx} className="flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                        <span>{detail}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            );
          })}
        </div>

        {/* Bottom CTA */}
        <div className="bg-slate-50 border border-slate-200 rounded-2xl p-8 text-center space-y-4">
          <h3 className="text-2xl font-bold text-slate-900">
            Ready to experience these capabilities firsthand?
          </h3>
          <p className="text-sm text-slate-600 max-w-xl mx-auto">
            Create an account to get started with your personal skill assessment and customized roadmap.
          </p>
          <div className="pt-2">
            <Button to="/register" variant="primary" size="lg">
              Get Started with SKILLY
            </Button>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
