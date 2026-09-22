import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Award, 
  CheckCircle2, 
  XCircle, 
  ArrowLeft, 
  Compass, 
  Layers, 
  ShieldCheck, 
  Sparkles, 
  ArrowRight 
} from 'lucide-react';
import api from '../../../lib/api';
import Button from '../../../components/Button';
import Loading from '../../../components/Loading';

export default function StudentAssessmentResult({ attemptId, onBack }) {
  const [attemptData, setAttemptData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);

  useEffect(() => {
    const fetchAttempt = async () => {
      try {
        setLoading(true);
        setErrorMsg(null);
        const res = await api.get(`/student/assessment-attempts/${attemptId}`);
        setAttemptData(res.data);
      } catch (err) {
        console.error('Failed to load assessment result:', err);
        setErrorMsg(err.response?.data?.detail || 'Failed to load test result.');
      } finally {
        setLoading(false);
      }
    };
    fetchAttempt();
  }, [attemptId]);

  if (loading) {
    return <Loading label="Retrieving diagnostic test evaluation & proficiency badge..." />;
  }

  if (!attemptData) {
    return (
      <div className="p-6 bg-white rounded-2xl border border-slate-200 text-center space-y-4">
        <p className="text-slate-600 text-sm">Attempt result data could not be found.</p>
        <Button variant="outline" size="sm" onClick={onBack}>
          Back to Catalog
        </Button>
      </div>
    );
  }

  const assessment = attemptData.assessment || {};
  const pct = Number(attemptData.percentage || 0);
  const isPassed = attemptData.is_passed;

  // Deriving proficiency level locally if missing
  let profLevel = 'BEGINNER';
  if (pct >= 90) profLevel = 'EXPERT';
  else if (pct >= 75) profLevel = 'ADVANCED';
  else if (pct >= 60) profLevel = 'INTERMEDIATE';

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Back Button */}
      <button
        onClick={onBack}
        className="inline-flex items-center space-x-1.5 text-sm font-semibold text-slate-500 hover:text-slate-800 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Assessments</span>
      </button>

      {/* Main Result Card */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 md:p-8 shadow-sm text-center space-y-6">
        {/* Outcome Icon */}
        <div
          className={`w-20 h-20 rounded-full flex items-center justify-center mx-auto shadow-sm ${
            isPassed ? 'bg-emerald-100 text-emerald-600' : 'bg-rose-100 text-rose-600'
          }`}
        >
          {isPassed ? <CheckCircle2 className="w-10 h-10" /> : <XCircle className="w-10 h-10" />}
        </div>

        <div>
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            {assessment.title || 'Diagnostic Assessment'}
          </span>
          <h1 className="text-2xl font-bold text-slate-900 mt-1">
            {isPassed ? 'Assessment Passed Successfully!' : 'Assessment Attempt Complete'}
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            {isPassed
              ? 'Your score has satisfied the passing threshold and earned a verified skill badge.'
              : 'Review your areas for improvement and retake the assessment when ready.'}
          </p>
        </div>

        {/* Score & Proficiency Grid */}
        <div className="grid grid-cols-2 gap-4 py-4 border-y border-slate-100">
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-100 text-center">
            <span className="block text-xs font-semibold text-slate-400 uppercase">Score Achieved</span>
            <span className={`text-3xl font-extrabold ${isPassed ? 'text-emerald-600' : 'text-slate-900'}`}>
              {pct}%
            </span>
            <span className="block text-xs text-slate-400 font-medium mt-0.5">Passing: {assessment.passing_score}%</span>
          </div>

          <div className="p-4 bg-slate-50 rounded-xl border border-slate-100 text-center">
            <span className="block text-xs font-semibold text-slate-400 uppercase">Proficiency Level</span>
            <span className="text-2xl font-extrabold text-blue-600 mt-1 block">
              {profLevel}
            </span>
            <span className="block text-xs text-slate-400 font-medium mt-0.5">Verified Status: ASSESSED</span>
          </div>
        </div>

        {/* Impact Notice */}
        <div className="p-4 bg-blue-50/50 border border-blue-100 rounded-xl text-left space-y-2 text-xs text-blue-900">
          <h4 className="font-bold flex items-center space-x-1 text-sm text-blue-950">
            <ShieldCheck className="w-4 h-4 text-blue-600" />
            <span>Automated Profile & Skill Passport Updates</span>
          </h4>
          <ul className="space-y-1 list-disc list-inside text-slate-700">
            <li>Skill passport entry updated with level <strong>{profLevel}</strong>.</li>
            <li>Verified digital evidence record added to your skill portfolio.</li>
            {isPassed && <li>Matching milestone checkpoints in your career roadmap auto-completed.</li>}
          </ul>
        </div>

        {/* Actions */}
        <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3">
          <Button variant="outline" size="sm" onClick={onBack} fullWidth className="sm:w-auto">
            Back to Catalog
          </Button>
          <Link to="/student/roadmaps" className="w-full sm:w-auto">
            <Button variant="primary" size="sm" icon={<Compass className="w-4 h-4" />} fullWidth>
              View Updated Career Roadmap
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
