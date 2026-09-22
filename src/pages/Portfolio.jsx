import React from 'react';
import PageContainer from '../components/PageContainer';
import Button from '../components/Button';
import { FileCheck, ArrowLeft, Clock, ShieldCheck, Award, Link2 } from 'lucide-react';

export default function Portfolio() {
  return (
    <PageContainer
      badge="Platform Module"
      title="Skill Passport & Portfolio"
      subtitle="Verified digital portfolio of assessments, project evidence, rubrics, and credentials."
    >
      <div className="space-y-10">
        
        {/* Module Status Card */}
        <div className="bg-white rounded-2xl border border-slate-200/80 p-8 text-center max-w-2xl mx-auto shadow-sm space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto border border-indigo-200">
            <FileCheck className="w-7 h-7" />
          </div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-50 text-amber-700 border border-amber-200 text-xs font-semibold">
            <Clock className="w-3.5 h-3.5" />
            <span>Module In Development</span>
          </div>
          <h2 className="text-2xl font-bold text-slate-900">Skill Passport Engine</h2>
          <p className="text-sm text-slate-600 leading-relaxed">
            The verifiable digital Skill Passport and authenticated portfolio export features will be implemented here.
          </p>
          <div className="pt-2">
            <Button to="/" variant="outline" size="md">
              <ArrowLeft className="w-4 h-4 mr-1.5" />
              <span>Back to Home</span>
            </Button>
          </div>
        </div>

        {/* Passport Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-2xs text-center space-y-2">
            <ShieldCheck className="w-8 h-8 text-blue-600 mx-auto" />
            <h4 className="text-base font-bold text-slate-900">Tamper-Proof Verification</h4>
            <p className="text-xs text-slate-500">Every project and test is verified with cryptographic signatures and timestamps.</p>
          </div>
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-2xs text-center space-y-2">
            <Award className="w-8 h-8 text-indigo-600 mx-auto" />
            <h4 className="text-base font-bold text-slate-900">Digital Badges</h4>
            <p className="text-xs text-slate-500">Earn verifiable competency badges recognized by partnered corporate recruiters.</p>
          </div>
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-2xs text-center space-y-2">
            <Link2 className="w-8 h-8 text-emerald-600 mx-auto" />
            <h4 className="text-base font-bold text-slate-900">Public Share Link</h4>
            <p className="text-xs text-slate-500">Attach your unique Skill Passport link directly onto your LinkedIn profile or resume.</p>
          </div>
        </div>

      </div>
    </PageContainer>
  );
}
