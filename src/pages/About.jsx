import React from 'react';
import PageContainer from '../components/PageContainer';
import Button from '../components/Button';
import { 
  Building2, 
  GraduationCap, 
  Target, 
  Users, 
  ShieldCheck, 
  Sparkles,
  CheckCircle2,
  Compass
} from 'lucide-react';

export default function About() {
  return (
    <PageContainer
      badge="About Platform"
      title="About SKILLY"
      subtitle="Connecting higher education with industry demands through verified proof of skill, actionable learning roadmaps, and experiential career acceleration."
    >
      <div className="space-y-16">
        
        {/* What is SKILLY */}
        <div className="bg-white rounded-2xl border border-slate-200/80 p-8 sm:p-10 shadow-sm">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            <div className="lg:col-span-7 space-y-4">
              <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">
                What is SKILLY?
              </h2>
              <p className="text-slate-600 leading-relaxed text-base">
                SKILLY is an integrated Academia–Industry collaboration platform built to close the gap between educational curricula and modern employer expectations. Rather than relying on unverified resumes or generic grades, SKILLY establishes a transparent, continuous ecosystem.
              </p>
              <p className="text-slate-600 leading-relaxed text-base">
                From initial skill assessment to gap analysis, roadmap navigation, hands-on projects, industry internships, and campus placement drives, SKILLY aligns all five key stakeholders in one cohesive platform.
              </p>
            </div>

            <div className="lg:col-span-5 bg-blue-50/70 border border-blue-100 rounded-xl p-6 space-y-3">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold">
                  <GraduationCap className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-slate-900">Academia</h4>
                  <p className="text-xs text-slate-500">Colleges, TPOs & Faculty</p>
                </div>
              </div>
              <div className="text-center text-blue-600 font-bold text-xs">↕ Unified Bridge ↕</div>
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-bold">
                  <Building2 className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-slate-900">Industry</h4>
                  <p className="text-xs text-slate-500">Enterprises, Startups & Recruiters</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Problem Being Addressed */}
        <div>
          <div className="text-center max-w-2xl mx-auto mb-10 space-y-2">
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">
              The Problem We Address
            </h2>
            <p className="text-slate-600 text-sm sm:text-base">
              Traditional campus-to-corporate pipelines face systemic challenges on both sides.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm">
              <div className="w-10 h-10 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center mb-4 border border-rose-200">
                <Target className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">The Skill Gap</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Students often lack clear visibility into which specific tools, frameworks, and practical skills are currently demanded by hiring companies.
              </p>
            </div>

            <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm">
              <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center mb-4 border border-amber-200">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">Unverified Proof</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Recruiters struggle with self-reported resume claims and lack reliable evidence of real project experience or code proficiency.
              </p>
            </div>

            <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm">
              <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mb-4 border border-blue-200">
                <Users className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">Fragmented Coordination</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Colleges, trainers, alumni mentors, and corporate recruiters operate in disconnected silos without a unified communication loop.
              </p>
            </div>
          </div>
        </div>

        {/* Platform Vision */}
        <div className="bg-slate-900 text-white rounded-2xl p-8 sm:p-12">
          <div className="max-w-3xl space-y-4">
            <span className="text-xs font-bold uppercase tracking-wider text-blue-400">Our Vision</span>
            <h2 className="text-2xl sm:text-3xl font-extrabold">
              Empowering Every Student with a Verifiable Pathway to Career Success
            </h2>
            <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
              We envision a future where education outcomes are measured by real capability and continuous career readiness. By combining assessment, roadmaps, internships, and transparent industry linkages, SKILLY transforms how talent is developed and discovered.
            </p>
            <div className="pt-4 flex flex-wrap gap-4">
              <Button to="/register" variant="primary" size="md">
                Join the Platform
              </Button>
              <Button to="/how-it-works" variant="outline" size="md" className="bg-slate-800 text-white border-slate-700 hover:bg-slate-700">
                Discover How It Works
              </Button>
            </div>
          </div>
        </div>

      </div>
    </PageContainer>
  );
}
