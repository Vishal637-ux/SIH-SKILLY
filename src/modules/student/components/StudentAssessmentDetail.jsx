import React, { useState, useEffect } from 'react';
import { 
  Award, 
  Clock, 
  HelpCircle, 
  CheckCircle2, 
  AlertCircle, 
  PlayCircle, 
  ArrowLeft, 
  ShieldCheck, 
  BookOpen 
} from 'lucide-react';
import api from '../../../lib/api';
import Button from '../../../components/Button';
import Loading from '../../../components/Loading';

export default function StudentAssessmentDetail({ assessmentId, onBack, onStartAttempt }) {
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  useEffect(() => {
    const fetchDetail = async () => {
      try {
        setLoading(true);
        setErrorMsg(null);
        const res = await api.get(`/student/assessments/${assessmentId}`);
        setDetail(res.data);
      } catch (err) {
        console.error('Failed to load assessment detail:', err);
        setErrorMsg(err.response?.data?.detail || 'Failed to load assessment details.');
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
  }, [assessmentId]);

  const handleStart = async () => {
    try {
      setStarting(true);
      setErrorMsg(null);
      const res = await api.post(`/student/assessments/${assessmentId}/start`);
      onStartAttempt(res.data.id);
    } catch (err) {
      console.error('Failed to start assessment:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to start assessment session.');
      setStarting(false);
    }
  };

  if (loading) {
    return <Loading label="Loading assessment instructions & parameters..." />;
  }

  if (!detail) {
    return (
      <div className="p-6 bg-white rounded-2xl border border-slate-200 text-center space-y-4">
        <p className="text-slate-600 text-sm">Assessment details could not be loaded.</p>
        <Button variant="outline" size="sm" onClick={onBack} icon={<ArrowLeft className="w-4 h-4" />}>
          Back to Catalog
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Back Button */}
      <button
        onClick={onBack}
        className="inline-flex items-center space-x-1.5 text-sm font-semibold text-slate-500 hover:text-slate-800 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Catalog</span>
      </button>

      {/* Error Notification */}
      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-sm flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0" />
            <span className="font-medium">{errorMsg}</span>
          </div>
        </div>
      )}

      {/* Card Header */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-100">
              {detail.assessment_type}
            </span>
            <h1 className="text-2xl font-bold text-slate-900 pt-1">{detail.title}</h1>
            {detail.target_skill && (
              <p className="text-sm font-semibold text-slate-500">
                Target Skill: <span className="text-slate-800">{detail.target_skill.name}</span> ({detail.target_skill.category})
              </p>
            )}
          </div>

          <div className="p-3 bg-blue-50 text-blue-600 rounded-2xl">
            <Award className="w-8 h-8" />
          </div>
        </div>

        {/* Test Parameters Grid */}
        <div className="grid grid-cols-3 gap-4 pt-4 border-t border-slate-100">
          <div className="p-4 bg-slate-50 rounded-xl text-center border border-slate-100">
            <Clock className="w-5 h-5 text-amber-500 mx-auto mb-1" />
            <span className="block text-xs font-semibold text-slate-400 uppercase">Duration</span>
            <strong className="text-base text-slate-900">{detail.duration_minutes} Minutes</strong>
          </div>

          <div className="p-4 bg-slate-50 rounded-xl text-center border border-slate-100">
            <HelpCircle className="w-5 h-5 text-blue-500 mx-auto mb-1" />
            <span className="block text-xs font-semibold text-slate-400 uppercase">Questions</span>
            <strong className="text-base text-slate-900">{detail.total_questions} Questions</strong>
          </div>

          <div className="p-4 bg-slate-50 rounded-xl text-center border border-slate-100">
            <CheckCircle2 className="w-5 h-5 text-emerald-500 mx-auto mb-1" />
            <span className="block text-xs font-semibold text-slate-400 uppercase">Passing Score</span>
            <strong className="text-base text-slate-900">{detail.passing_score}%</strong>
          </div>
        </div>

        {/* Test Instructions */}
        <div className="space-y-3 pt-4 border-t border-slate-100">
          <h3 className="font-bold text-slate-900 text-sm flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-blue-600" />
            <span>Test Guidelines & Regulations</span>
          </h3>

          <ul className="space-y-2 text-xs text-slate-600 list-disc list-inside leading-relaxed">
            <li>Ensure a stable internet connection before launching the test session.</li>
            <li>The test timer starts immediately upon clicking <strong>"Begin Diagnostic Test Session"</strong>.</li>
            <li>You may navigate between questions and update your selections prior to submission.</li>
            <li>Passing this diagnostic assessment (Score &ge; {detail.passing_score}%) earns a verified skill badge and updates your career roadmap.</li>
            <li>Once submitted, test results are graded deterministically and saved permanently.</li>
          </ul>
        </div>

        {/* Action Button */}
        <div className="pt-4 border-t border-slate-100 flex items-center justify-end space-x-3">
          <Button variant="outline" size="sm" onClick={onBack}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleStart}
            loading={starting}
            icon={<PlayCircle className="w-4 h-4" />}
          >
            Begin Diagnostic Test Session
          </Button>
        </div>
      </div>
    </div>
  );
}
