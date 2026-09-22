import React from 'react';
import PageContainer from '../components/PageContainer';
import Button from '../components/Button';
import { MessageSquare, ArrowLeft, Clock, Users, Sparkles } from 'lucide-react';

export default function Community() {
  return (
    <PageContainer
      badge="Platform Module"
      title="Community & Networking"
      subtitle="Peer study groups, technical forums, alumni Q&A sessions, and campus events."
    >
      <div className="space-y-10">
        
        {/* Module Status Card */}
        <div className="bg-white rounded-2xl border border-slate-200/80 p-8 text-center max-w-2xl mx-auto shadow-sm space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-purple-50 text-purple-600 flex items-center justify-center mx-auto border border-purple-200">
            <MessageSquare className="w-7 h-7" />
          </div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-50 text-amber-700 border border-amber-200 text-xs font-semibold">
            <Clock className="w-3.5 h-3.5" />
            <span>Module In Development</span>
          </div>
          <h2 className="text-2xl font-bold text-slate-900">Community & Forum Hub</h2>
          <p className="text-sm text-slate-600 leading-relaxed">
            The collaborative student forums, topic-specific discussion channels, and live Ask-Me-Anything (AMA) events will be implemented here.
          </p>
          <div className="pt-2">
            <Button to="/" variant="outline" size="md">
              <ArrowLeft className="w-4 h-4 mr-1.5" />
              <span>Back to Home</span>
            </Button>
          </div>
        </div>

      </div>
    </PageContainer>
  );
}
