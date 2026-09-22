import React, { useState, useEffect } from 'react';
import api from '../../../lib/api';
import Loading from '../../../components/Loading';
import Button from '../../../components/Button';
import { Award, Star, CheckCircle, Calendar, User, FileText, AlertTriangle, X } from 'lucide-react';

export default function IndustryInternshipsWorkspace() {
  const [internships, setInternships] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Evaluation modal
  const [evalModalInt, setEvalModalInt] = useState(null);
  const [evalForm, setEvalForm] = useState({
    technical_rating: 5,
    soft_skills_rating: 5,
    punctuality_rating: 5,
    overall_feedback: '',
  });
  const [submitting, setSubmitting] = useState(false);

  const fetchInternships = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/api/v1/industry/internships');
      setInternships(res.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load corporate internships.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInternships();
  }, []);

  const openEvalModal = (internship) => {
    setEvalModalInt(internship);
    setEvalForm({
      technical_rating: 5,
      soft_skills_rating: 5,
      punctuality_rating: 5,
      overall_feedback: '',
    });
  };

  const handleEvalSubmit = async (e) => {
    e.preventDefault();
    if (!evalModalInt) return;
    setSubmitting(true);
    try {
      await api.post(`/api/v1/industry/internships/${evalModalInt.id}/evaluations`, evalForm);
      setEvalModalInt(null);
      fetchInternships();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to submit internship evaluation.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <Loading label="Loading active corporate internships..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-sm flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-slate-900">Internship Supervision & Rubric Evaluation</h2>
          <p className="text-xs text-slate-500">Monitor ongoing intern contracts, weekly reports, and submit performance evaluations</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0" />
          <p className="text-xs font-semibold">{error}</p>
        </div>
      )}

      {/* Intern Roster */}
      {internships.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200/80 p-12 text-center max-w-md mx-auto space-y-2">
          <Award className="w-10 h-10 text-slate-400 mx-auto" />
          <h3 className="text-base font-bold text-slate-900">No active internships</h3>
          <p className="text-xs text-slate-500">When candidate offers are accepted, active internship contracts will be listed here.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {internships.map((int) => (
            <div key={int.id} className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                    int.status === 'ONGOING' ? 'bg-purple-100 text-purple-800' : 'bg-emerald-100 text-emerald-800'
                  }`}>
                    {int.status}
                  </span>
                  <h3 className="text-base font-bold text-slate-900 mt-1">{int.student_name}</h3>
                  <p className="text-xs text-slate-500">Roll: {int.roll_number}</p>
                </div>
                {int.has_evaluation ? (
                  <span className="inline-flex items-center gap-1 text-emerald-600 text-xs font-bold bg-emerald-50 px-2.5 py-1 rounded-md border border-emerald-200">
                    <CheckCircle className="w-3.5 h-3.5" /> Evaluated
                  </span>
                ) : (
                  <Button variant="primary" size="sm" onClick={() => openEvalModal(int)}>
                    <Star className="w-3.5 h-3.5 mr-1" /> Evaluate Intern
                  </Button>
                )}
              </div>

              <p className="text-xs font-semibold text-slate-700">{int.opportunity_title}</p>

              <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-500 bg-slate-50 p-3 rounded-lg border border-slate-100">
                <div>
                  <span className="font-semibold text-slate-700 block">Supervisor:</span>
                  <span>{int.supervisor_name} ({int.supervisor_email})</span>
                </div>
                <div>
                  <span className="font-semibold text-slate-700 block">Duration:</span>
                  <span>{int.start_date} to {int.end_date}</span>
                </div>
                <div>
                  <span className="font-semibold text-slate-700 block">Stipend:</span>
                  <span>{int.stipend || 'Unpaid'}</span>
                </div>
                <div>
                  <span className="font-semibold text-slate-700 block">Weekly Logs:</span>
                  <span>{int.weekly_reports_count} Reports Submitted</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Rubric Evaluation Modal */}
      {evalModalInt && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <div>
                <span className="text-[10px] font-bold text-blue-600 uppercase tracking-wide">Rubric Performance Scoring</span>
                <h3 className="text-base font-bold text-slate-900">Evaluate {evalModalInt.student_name}</h3>
              </div>
              <button onClick={() => setEvalModalInt(null)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleEvalSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block font-bold text-slate-700 mb-1">Technical Skills Rating (1 to 5 Stars) *</label>
                <select
                  value={evalForm.technical_rating}
                  onChange={(e) => setEvalForm({ ...evalForm, technical_rating: parseInt(e.target.value, 10) })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value={5}>5 - Outstanding Technical Mastery</option>
                  <option value={4}>4 - Strong Technical Capability</option>
                  <option value={3}>3 - Satisfactory Basic Skills</option>
                  <option value={2}>2 - Needs Technical Improvement</option>
                  <option value={1}>1 - Unsatisfactory Performance</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Soft Skills & Team Collaboration (1 to 5 Stars) *</label>
                <select
                  value={evalForm.soft_skills_rating}
                  onChange={(e) => setEvalForm({ ...evalForm, soft_skills_rating: parseInt(e.target.value, 10) })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value={5}>5 - Excellent Communication & Leadership</option>
                  <option value={4}>4 - Good Teamwork & Adaptability</option>
                  <option value={3}>3 - Adequate Collaboration</option>
                  <option value={2}>2 - Needs Soft Skills Training</option>
                  <option value={1}>1 - Poor Team Integration</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Punctuality & Reliability (1 to 5 Stars) *</label>
                <select
                  value={evalForm.punctuality_rating}
                  onChange={(e) => setEvalForm({ ...evalForm, punctuality_rating: parseInt(e.target.value, 10) })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value={5}>5 - Always Punctual & Meets Deadlines</option>
                  <option value={4}>4 - Reliable & Consistent</option>
                  <option value={3}>3 - Minor Delays</option>
                  <option value={2}>2 - Frequent Tardiness</option>
                  <option value={1}>1 - Unreliable</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Overall Performance Feedback & Rationale *</label>
                <textarea
                  rows={4}
                  required
                  placeholder="Provide detailed feedback on project deliverables, strengths, and areas for growth..."
                  value={evalForm.overall_feedback}
                  onChange={(e) => setEvalForm({ ...evalForm, overall_feedback: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-slate-200">
                <Button type="button" variant="outline" size="sm" onClick={() => setEvalModalInt(null)}>
                  Cancel
                </Button>
                <Button type="submit" variant="primary" size="sm" disabled={submitting}>
                  {submitting ? 'Submitting...' : 'Submit Evaluation'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
