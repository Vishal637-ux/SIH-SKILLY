import React, { useState, useEffect } from 'react';
import { 
  Award, 
  Clock, 
  CheckCircle2, 
  HelpCircle, 
  PlayCircle, 
  History, 
  AlertCircle, 
  Layers, 
  Sparkles,
  ChevronRight
} from 'lucide-react';
import api from '../../../lib/api';
import Button from '../../../components/Button';
import Loading from '../../../components/Loading';
import StudentAssessmentDetail from './StudentAssessmentDetail';
import StudentAssessmentRunner from './StudentAssessmentRunner';
import StudentAssessmentResult from './StudentAssessmentResult';

export default function StudentAssessmentCatalog() {
  const [assessments, setAssessments] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);

  // Active view states: 'CATALOG', 'DETAIL', 'RUNNER', 'RESULT'
  const [activeView, setActiveView] = useState('CATALOG');
  const [selectedAssessmentId, setSelectedAssessmentId] = useState(null);
  const [activeAttemptId, setActiveAttemptId] = useState(null);

  const fetchCatalogAndHistory = async () => {
    try {
      setLoading(true);
      setErrorMsg(null);
      const [catRes, histRes] = await Promise.all([
        api.get('/student/assessments'),
        api.get('/student/assessment-history'),
      ]);
      setAssessments(catRes.data || []);
      setHistory(histRes.data || []);
    } catch (err) {
      console.error('Failed to load assessment catalog:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to load assessments data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCatalogAndHistory();
  }, []);

  const handleSelectAssessment = (assId) => {
    setSelectedAssessmentId(assId);
    setActiveView('DETAIL');
  };

  const handleStartAttempt = (attemptId) => {
    setActiveAttemptId(attemptId);
    setActiveView('RUNNER');
  };

  const handleFinishAttempt = (attemptId) => {
    setActiveAttemptId(attemptId);
    setActiveView('RESULT');
  };

  const handleBackToCatalog = () => {
    setSelectedAssessmentId(null);
    setActiveAttemptId(null);
    setActiveView('CATALOG');
    fetchCatalogAndHistory();
  };

  if (loading) {
    return <Loading label="Loading diagnostic assessments catalog..." />;
  }

  // Render Sub-Views
  if (activeView === 'DETAIL' && selectedAssessmentId) {
    return (
      <StudentAssessmentDetail
        assessmentId={selectedAssessmentId}
        onBack={handleBackToCatalog}
        onStartAttempt={handleStartAttempt}
      />
    );
  }

  if (activeView === 'RUNNER' && activeAttemptId) {
    return (
      <StudentAssessmentRunner
        attemptId={activeAttemptId}
        onFinishAttempt={handleFinishAttempt}
        onBack={handleBackToCatalog}
      />
    );
  }

  if (activeView === 'RESULT' && activeAttemptId) {
    return (
      <StudentAssessmentResult
        attemptId={activeAttemptId}
        onBack={handleBackToCatalog}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Error Banner */}
      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-sm flex items-center justify-between shadow-sm">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0" />
            <span className="font-medium">{errorMsg}</span>
          </div>
          <button onClick={() => setErrorMsg(null)} className="text-rose-500 hover:text-rose-700 font-bold">
            ×
          </button>
        </div>
      )}

      {/* Workspace Header */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-blue-50 text-blue-600 rounded-xl">
              <Award className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900">Diagnostic Skill Assessment</h1>
              <p className="text-sm text-slate-500">
                Benchmark your verified competencies, earn verified skill seals, and update your career roadmap.
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="px-4 py-2 bg-slate-50 border border-slate-100 rounded-xl text-center">
              <span className="block text-xs font-semibold text-slate-400 uppercase">Assessments Taken</span>
              <span className="text-lg font-bold text-slate-900">{history.length}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Catalog Grid */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
        <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
          <Sparkles className="w-5 h-5 text-blue-600" />
          <span>Available Assessments ({assessments.length})</span>
        </h2>

        {assessments.length === 0 ? (
          <div className="text-center py-8 bg-slate-50 rounded-xl border border-dashed border-slate-200">
            <Award className="w-10 h-10 text-slate-300 mx-auto mb-2" />
            <p className="text-slate-600 font-medium text-sm">No Active Assessments Available</p>
            <p className="text-slate-400 text-xs mt-1">Diagnostic assessments are currently being scheduled.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {assessments.map((ass) => {
              const bestScore = ass.best_score !== null ? Number(ass.best_score) : null;
              const hasTaken = ass.attempts_count > 0;

              return (
                <div
                  key={ass.id}
                  className="border border-slate-200 rounded-xl p-5 space-y-3 bg-white hover:border-blue-300 hover:shadow-sm transition-all flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between">
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-100">
                        {ass.assessment_type}
                      </span>
                      {hasTaken && (
                        <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-100">
                          Best: {bestScore}%
                        </span>
                      )}
                    </div>

                    <h3 className="font-bold text-slate-900 text-base mt-2">{ass.title}</h3>
                    
                    {ass.target_skill && (
                      <div className="flex items-center space-x-1.5 mt-1 text-xs text-slate-500 font-medium">
                        <Layers className="w-3.5 h-3.5 text-slate-400" />
                        <span>Target Skill: <strong className="text-slate-700">{ass.target_skill.name}</strong></span>
                      </div>
                    )}
                  </div>

                  <div className="space-y-3 pt-3 border-t border-slate-100">
                    <div className="grid grid-cols-3 gap-2 text-center text-xs">
                      <div className="p-1.5 bg-slate-50 rounded border border-slate-100">
                        <span className="block text-slate-400 font-medium text-[10px]">Questions</span>
                        <strong className="text-slate-700">{ass.total_questions}</strong>
                      </div>
                      <div className="p-1.5 bg-slate-50 rounded border border-slate-100">
                        <span className="block text-slate-400 font-medium text-[10px]">Duration</span>
                        <strong className="text-slate-700">{ass.duration_minutes}m</strong>
                      </div>
                      <div className="p-1.5 bg-slate-50 rounded border border-slate-100">
                        <span className="block text-slate-400 font-medium text-[10px]">Passing</span>
                        <strong className="text-slate-700">{ass.passing_score}%</strong>
                      </div>
                    </div>

                    <Button
                      fullWidth
                      variant="primary"
                      size="sm"
                      onClick={() => handleSelectAssessment(ass.id)}
                      icon={<PlayCircle className="w-3.5 h-3.5" />}
                    >
                      {hasTaken ? 'Retake Assessment' : 'Start Assessment'}
                    </Button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* History Ledger Section */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
        <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
          <History className="w-5 h-5 text-blue-600" />
          <span>My Assessment History ({history.length})</span>
        </h2>

        {history.length === 0 ? (
          <div className="text-center py-6 bg-slate-50 rounded-xl border border-dashed border-slate-200">
            <p className="text-slate-500 text-xs font-medium">No completed assessments recorded yet.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50/50 text-slate-500 text-xs uppercase font-semibold">
                  <th className="py-3 px-4">Assessment Title</th>
                  <th className="py-3 px-4">Target Skill</th>
                  <th className="py-3 px-4">Score</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Proficiency Level</th>
                  <th className="py-3 px-4 text-right">Completed Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {history.map((h) => (
                  <tr key={h.attempt_id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="py-3 px-4 font-bold text-slate-900">{h.assessment_title}</td>
                    <td className="py-3 px-4 text-slate-600 font-medium">{h.target_skill_name || 'General'}</td>
                    <td className="py-3 px-4 font-bold text-slate-900">{h.percentage}%</td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                          h.is_passed
                            ? 'bg-emerald-100 text-emerald-800'
                            : 'bg-rose-100 text-rose-800'
                        }`}
                      >
                        {h.is_passed ? 'PASSED' : 'FAILED'}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-100">
                        {h.proficiency_level}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right text-xs text-slate-500 font-medium">
                      {h.completed_at ? new Date(h.completed_at).toLocaleDateString() : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
