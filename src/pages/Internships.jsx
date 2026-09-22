import React from 'react';
import PageContainer from '../components/PageContainer';
import Button from '../components/Button';
import { Briefcase, ArrowLeft, Clock, Building2, MapPin, DollarSign } from 'lucide-react';

export default function Internships() {
  return (
    <PageContainer
      badge="Platform Module"
      title="Internships & Projects Hub"
      subtitle="Discover practical assignments, verified company internships, and industry capstones."
    >
      <div className="space-y-10">
        
        {/* Module Status Card */}
        <div className="bg-white rounded-2xl border border-slate-200/80 p-8 text-center max-w-2xl mx-auto shadow-sm space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto border border-emerald-200">
            <Briefcase className="w-7 h-7" />
          </div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-50 text-amber-700 border border-amber-200 text-xs font-semibold">
            <Clock className="w-3.5 h-3.5" />
            <span>Module In Development</span>
          </div>
          <h2 className="text-2xl font-bold text-slate-900">Internship & Project Matching Hub</h2>
          <p className="text-sm text-slate-600 leading-relaxed">
            The internship listing portal, direct application engine, and corporate challenge submission portal will be implemented here.
          </p>
          <div className="pt-2">
            <Button to="/" variant="outline" size="md">
              <ArrowLeft className="w-4 h-4 mr-1.5" />
              <span>Back to Home</span>
            </Button>
          </div>
        </div>

        {/* Informative Structure Preview */}
        <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 sm:p-8 max-w-3xl mx-auto">
          <h3 className="text-base font-bold text-slate-900 mb-3">
            How Internships Work on SKILLY
          </h3>
          <ul className="space-y-2 text-xs sm:text-sm text-slate-600">
            <li className="flex items-start gap-2">
              <span className="font-bold text-blue-600 shrink-0">•</span>
              <span><strong>Skill-Matched Opportunities:</strong> Roles are dynamically displayed based on your verified skill score cutoff.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold text-blue-600 shrink-0">•</span>
              <span><strong>Verified Submission:</strong> Submit real Git repository links, live demos, and documentation directly for evaluation.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold text-blue-600 shrink-0">•</span>
              <span><strong>College Credits & Tracking:</strong> Automatically report verified internship milestones back to your college TPO.</span>
            </li>
          </ul>
        </div>

      </div>
    </PageContainer>
  );
}
