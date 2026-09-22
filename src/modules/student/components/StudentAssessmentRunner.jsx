import React, { useState, useEffect } from 'react';
import { 
  Clock, 
  CheckCircle2, 
  AlertCircle, 
  ChevronLeft, 
  ChevronRight, 
  Send, 
  HelpCircle, 
  ShieldAlert 
} from 'lucide-react';
import api from '../../../lib/api';
import Button from '../../../components/Button';
import Loading from '../../../components/Loading';

export default function StudentAssessmentRunner({ attemptId, onFinishAttempt, onBack }) {
  const [attemptData, setAttemptData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  // Active question index
  const [currentQIndex, setCurrentQIndex] = useState(0);

  // Student selected responses: { [question_id]: option_id_or_text }
  const [responses, setResponses] = useState({});

  // Countdown timer state in seconds
  const [secondsRemaining, setSecondsRemaining] = useState(null);

  useEffect(() => {
    const fetchAttempt = async () => {
      try {
        setLoading(true);
        setErrorMsg(null);
        const res = await api.get(`/student/assessment-attempts/${attemptId}`);
        const data = res.data;
        setAttemptData(data);

        // Pre-populate responses if present
        if (data.responses && typeof data.responses === 'object') {
          setResponses(data.responses);
        }

        // Initialize countdown timer
        if (data.assessment && data.assessment.duration_minutes) {
          const totalSecs = data.assessment.duration_minutes * 60;
          setSecondsRemaining(totalSecs);
        }
      } catch (err) {
        console.error('Failed to load assessment attempt:', err);
        setErrorMsg(err.response?.data?.detail || 'Failed to load test session.');
      } finally {
        setLoading(false);
      }
    };
    fetchAttempt();
  }, [attemptId]);

  // Countdown timer effect
  useEffect(() => {
    if (secondsRemaining === null || secondsRemaining <= 0) return;

    const timer = setInterval(() => {
      setSecondsRemaining((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [secondsRemaining]);

  const handleOptionSelect = (questionId, optionValue) => {
    if (
      attemptData?.completed_at &&
      attemptData?.started_at &&
      new Date(attemptData.completed_at).getTime() > new Date(attemptData.started_at).getTime()
    ) {
      return; // Prevent modification if submitted/completed
    }
    setResponses((prev) => ({
      ...prev,
      [questionId]: optionValue,
    }));
  };

  const handleSubmitAttempt = async () => {
    try {
      setSubmitting(true);
      setErrorMsg(null);
      await api.post(`/student/assessment-attempts/${attemptId}/submit`, {
        responses: responses,
      });
      onFinishAttempt(attemptId);
    } catch (err) {
      console.error('Failed to submit assessment:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to submit test responses.');
      setSubmitting(false);
    }
  };

  if (loading) {
    return <Loading label="Loading active test session questions..." />;
  }

  if (!attemptData) {
    return (
      <div className="p-6 bg-white rounded-2xl border border-slate-200 text-center space-y-4">
        <p className="text-slate-600 text-sm">Test session data could not be retrieved.</p>
        <Button variant="outline" size="sm" onClick={onBack}>
          Back to Catalog
        </Button>
      </div>
    );
  }

  const assessment = attemptData.assessment || {};
  const questions = attemptData.questions || [];
  const currentQ = questions[currentQIndex];

  const formatTimer = (secs) => {
    if (secs === null) return '--:--';
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const answeredCount = Object.keys(responses).length;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Notifications */}
      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-sm flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0" />
            <span className="font-medium">{errorMsg}</span>
          </div>
        </div>
      )}

      {/* Top Header Bar with Timer & Progress */}
      <div className="bg-white border border-slate-200 rounded-2xl p-4 md:p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            {assessment.title || 'Diagnostic Test Session'}
          </span>
          <h2 className="text-lg font-bold text-slate-900">
            Question {currentQIndex + 1} of {questions.length}
          </h2>
        </div>

        <div className="flex items-center space-x-4">
          {/* Timer Display */}
          <div className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-xl border text-sm font-bold ${
            secondsRemaining !== null && secondsRemaining < 300
              ? 'bg-rose-50 text-rose-700 border-rose-200 animate-pulse'
              : 'bg-slate-50 text-slate-700 border-slate-200'
          }`}>
            <Clock className="w-4 h-4 text-amber-500" />
            <span>{formatTimer(secondsRemaining)}</span>
          </div>

          <span className="text-xs font-semibold text-slate-500 bg-blue-50 px-3 py-1 rounded-xl text-blue-700 border border-blue-100">
            {answeredCount} / {questions.length} Answered
          </span>
        </div>
      </div>

      {/* Question Navigation Numbers */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex items-center space-x-2 flex-wrap gap-y-2">
        {questions.map((q, idx) => {
          const isAnswered = responses[q.id] !== undefined && responses[q.id] !== '';
          const isCurrent = idx === currentQIndex;

          return (
            <button
              key={q.id}
              onClick={() => setCurrentQIndex(idx)}
              className={`w-9 h-9 rounded-lg font-bold text-xs transition-all ${
                isCurrent
                  ? 'bg-blue-600 text-white ring-2 ring-blue-600 ring-offset-2'
                  : isAnswered
                  ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {idx + 1}
            </button>
          );
        })}
      </div>

      {/* Current Question Card */}
      {currentQ && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-3">
              <span className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 font-bold text-sm flex items-center justify-center">
                Q{currentQIndex + 1}
              </span>
              <span className="text-xs font-semibold text-slate-400 uppercase">
                {currentQ.question_type || 'MULTIPLE CHOICE'}
              </span>
            </div>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700">
              {currentQ.points} Point{currentQ.points > 1 ? 's' : ''}
            </span>
          </div>

          <h3 className="text-base font-bold text-slate-900 leading-relaxed">
            {currentQ.question_text}
          </h3>

          {/* Options Selection */}
          <div className="space-y-3 pt-2">
            {Array.isArray(currentQ.options) && currentQ.options.length > 0 ? (
              currentQ.options.map((opt, oIdx) => {
                const optionKey = typeof opt === 'object' ? (opt.id || opt.value || opt.text) : opt;
                const optionLabel = typeof opt === 'object' ? opt.text : opt;
                const isSelected = responses[currentQ.id] === optionKey;

                return (
                  <button
                    key={oIdx}
                    onClick={() => handleOptionSelect(currentQ.id, optionKey)}
                    className={`w-full text-left p-4 rounded-xl border text-sm font-medium transition-all flex items-center justify-between ${
                      isSelected
                        ? 'border-blue-600 bg-blue-50/40 text-blue-900 shadow-sm font-semibold'
                        : 'border-slate-200 bg-white hover:border-slate-300 text-slate-800'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`w-5 h-5 rounded-full border flex items-center justify-center text-xs font-bold ${
                        isSelected ? 'border-blue-600 bg-blue-600 text-white' : 'border-slate-300 text-slate-400'
                      }`}>
                        {String.fromCharCode(65 + oIdx)}
                      </div>
                      <span>{optionLabel}</span>
                    </div>

                    {isSelected && <CheckCircle2 className="w-4 h-4 text-blue-600 flex-shrink-0" />}
                  </button>
                );
              })
            ) : (
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
                <input
                  type="text"
                  placeholder="Type your response here..."
                  value={responses[currentQ.id] || ''}
                  onChange={(e) => handleOptionSelect(currentQ.id, e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                />
              </div>
            )}
          </div>

          {/* Footer Controls */}
          <div className="pt-6 border-t border-slate-100 flex items-center justify-between">
            <Button
              variant="outline"
              size="sm"
              disabled={currentQIndex === 0}
              onClick={() => setCurrentQIndex((prev) => Math.max(0, prev - 1))}
              icon={<ChevronLeft className="w-4 h-4" />}
            >
              Previous
            </Button>

            <div className="flex items-center space-x-3">
              {currentQIndex < questions.length - 1 ? (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentQIndex((prev) => Math.min(questions.length - 1, prev + 1))}
                  icon={<ChevronRight className="w-4 h-4" />}
                >
                  Next Question
                </Button>
              ) : (
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleSubmitAttempt}
                  loading={submitting}
                  icon={<Send className="w-4 h-4" />}
                >
                  Submit Assessment
                </Button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
