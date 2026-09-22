import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  Layers, 
  Sparkles, 
  CheckCircle2, 
  ExternalLink,
  ShieldCheck
} from 'lucide-react';
import Button from '../../../components/Button';

export default function StudentModulePlaceholder({
  title,
  subtitle,
  icon: Icon = Layers,
  domainModule,
  domainDescription,
  features = [],
  actionText = "Back to Dashboard",
  actionLink = "/student",
}) {
  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Module Header Card */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-6 sm:p-8 shadow-soft">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-slate-100">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center border border-blue-200/60 shadow-xs">
              <Icon className="w-7 h-7" />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="px-2.5 py-0.5 rounded-full bg-blue-100/80 text-blue-700 text-[11px] font-bold tracking-wide uppercase">
                  {domainModule || 'Domain Module'}
                </span>
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-[11px] font-semibold">
                  <ShieldCheck className="w-3 h-3" />
                  <span>Integration Boundary Ready</span>
                </span>
              </div>
              <h1 className="text-2xl font-black tracking-tight text-slate-900">{title}</h1>
              <p className="text-xs sm:text-sm text-slate-500 mt-0.5">{subtitle}</p>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <Button to="/student" variant="outline" size="sm">
              <ArrowLeft className="w-3.5 h-3.5 mr-1.5" />
              <span>Dashboard</span>
            </Button>
            <Button to="/student/profile" variant="primary" size="sm">
              Update Profile
            </Button>
          </div>
        </div>

        {/* Integration Architecture Notice */}
        <div className="mt-6 bg-slate-50 rounded-xl p-5 border border-slate-200/80 space-y-3">
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-lg bg-blue-600 text-white shrink-0 mt-0.5">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-xs sm:text-sm font-bold text-slate-900">
                Architectural Domain Integration Notice
              </h3>
              <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                {domainDescription || 
                  "This area is the student-facing presentation entrypoint. Its domain business logic, state machines, and algorithms are encapsulated within their respective domain engines."}
              </p>
            </div>
          </div>

          {/* Planned Features in this Domain */}
          {features.length > 0 && (
            <div className="pt-3 border-t border-slate-200">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2.5">
                Domain Capabilities in this Area:
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {features.map((feat, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-xs text-slate-700 bg-white p-2.5 rounded-lg border border-slate-200/60">
                    <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                    <span>{feat}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
