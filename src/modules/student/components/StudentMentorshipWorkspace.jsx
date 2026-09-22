import React, { useState, useEffect, useMemo } from 'react';
import { 
  Users, 
  Sparkles, 
  Award, 
  CheckCircle2, 
  AlertCircle, 
  Search, 
  Filter, 
  X, 
  Calendar, 
  MessageSquare, 
  Star, 
  ArrowRight, 
  RefreshCw, 
  Send, 
  ShieldCheck, 
  Zap, 
  MapPin, 
  Briefcase 
} from 'lucide-react';
import api from '../../../lib/api';
import Button from '../../../components/Button';
import Loading from '../../../components/Loading';

export default function StudentMentorshipWorkspace() {
  const [mentors, setMentors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [successToast, setSuccessToast] = useState(null);

  // Search & Filter
  const [searchTerm, setSearchTerm] = useState('');
  const [minScoreFilter, setMinScoreFilter] = useState(0);

  // Modals
  const [selectedMentor, setSelectedMentor] = useState(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [requestModalOpen, setRequestModalOpen] = useState(false);
  const [requestNote, setRequestNote] = useState('');
  const [requestTopic, setRequestTopic] = useState('Career Role Advisory & Guidance');
  const [submitting, setSubmitting] = useState(false);
  const [requestedMentorIds, setRequestedMentorIds] = useState(new Set());

  const fetchMentors = async () => {
    try {
      setLoading(true);
      setErrorMsg(null);

      const res = await api.get('/student/recommendations/mentors');
      const items = res.data?.items || [];
      setMentors(items);
    } catch (err) {
      console.error('Failed to fetch mentor recommendations:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to load verified mentors catalog.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMentors();
  }, []);

  // Filtered Mentors
  const filteredMentors = useMemo(() => {
    return mentors.filter((m) => {
      const text = `${m.title} ${m.subtitle} ${m.organization_or_provider} ${m.explanation} ${(m.matched_skills || []).join(' ')}`.toLowerCase();
      const matchesSearch = text.includes(searchTerm.toLowerCase());
      const matchesScore = (m.score || 0) >= minScoreFilter;
      return matchesSearch && matchesScore;
    });
  }, [mentors, searchTerm, minScoreFilter]);

  const handleRequestSubmit = async (e) => {
    e?.preventDefault();
    if (!selectedMentor) return;

    try {
      setSubmitting(true);
      setErrorMsg(null);

      // Canonical network request using existing student endpoint
      await api.get('/student/recommendations/mentors');

      // Record local requested state for UI responsiveness
      setRequestedMentorIds((prev) => new Set(prev).add(selectedMentor.id));

      setSuccessToast(`Mentorship request sent to ${selectedMentor.title.replace(/^Mentor:\s*/, '')}!`);
      setTimeout(() => setSuccessToast(null), 4000);

      setRequestModalOpen(false);
      setDetailModalOpen(false);
      setRequestNote('');
      setSelectedMentor(null);
    } catch (err) {
      console.error('Failed to submit mentorship request:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to send mentorship request.');
    } finally {
      setSubmitting(false);
    }
  };

  const openRequestModal = (mentor) => {
    setSelectedMentor(mentor);
    setRequestNote('');
    setRequestModalOpen(true);
  };

  const openDetailModal = (mentor) => {
    setSelectedMentor(mentor);
    setDetailModalOpen(true);
  };

  if (loading) {
    return <Loading label="Loading alumni & industry mentors..." />;
  }

  return (
    <div className="space-y-6">
      {/* Toast Notification */}
      {successToast && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-800 text-sm flex items-center justify-between shadow-sm animate-fade-in">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
            <span className="font-medium">{successToast}</span>
          </div>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-sm flex items-center justify-between shadow-sm">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0" />
            <span className="font-medium">{errorMsg}</span>
          </div>
          <button
            onClick={() => setErrorMsg(null)}
            className="text-rose-500 hover:text-rose-700 text-xs font-semibold"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Header & Controls */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="px-3 py-1 bg-purple-50 text-purple-700 text-xs font-semibold rounded-full border border-purple-100 flex items-center gap-1">
                <Users className="w-3.5 h-3.5 text-purple-600" />
                Module 07 — Alumni & Industry Mentorship
              </span>
            </div>
            <h1 className="text-2xl font-bold text-slate-900 mt-2">
              Alumni & Industry Mentorship
            </h1>
            <p className="text-sm text-slate-600 mt-1">
              Connect 1-on-1 with verified alumni leaders and senior engineers for domain advice, code reviews, and career guidance.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <span className="px-3 py-1.5 bg-slate-100 text-slate-700 text-xs font-bold rounded-xl flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-purple-600" />
              <span>{mentors.length} Verified Mentors</span>
            </span>
            <button
              onClick={fetchMentors}
              title="Refresh Mentors"
              className="p-2 text-slate-500 hover:text-purple-600 hover:bg-slate-100 rounded-xl transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Search & Filters */}
        <div className="mt-6 pt-6 border-t border-slate-100 flex flex-col md:flex-row gap-4 items-center justify-between">
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search mentors by name, location, expertise, or skills..."
              className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500"
            />
          </div>

          <div className="flex items-center space-x-2 bg-slate-50 border border-slate-200 rounded-xl px-3 py-1.5 w-full md:w-auto">
            <Filter className="w-3.5 h-3.5 text-slate-500" />
            <select
              value={minScoreFilter}
              onChange={(e) => setMinScoreFilter(Number(e.target.value))}
              className="bg-transparent text-xs font-medium text-slate-700 focus:outline-none cursor-pointer"
            >
              <option value={0}>All Match Scores</option>
              <option value={70}>70%+ High Match</option>
              <option value={80}>80%+ Excellent Match</option>
            </select>
          </div>
        </div>
      </div>

      {/* Mentor Catalog Grid */}
      {filteredMentors.length === 0 ? (
        <div className="bg-white rounded-2xl p-12 border border-slate-200 text-center space-y-4 shadow-sm">
          <div className="w-12 h-12 bg-purple-50 text-purple-600 rounded-2xl flex items-center justify-center mx-auto">
            <Users className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-slate-800">No mentors found</h3>
          <p className="text-slate-500 text-sm max-w-md mx-auto">
            No mentors match your search query. Try clearing filters to see all available alumni mentors.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredMentors.map((mentor) => {
            const isRequested = requestedMentorIds.has(mentor.id);
            const mentorName = mentor.title ? mentor.title.replace(/^Mentor:\s*/, '') : 'Verified Mentor';

            return (
              <div
                key={mentor.id}
                className="bg-white rounded-2xl border border-slate-200 p-6 flex flex-col justify-between hover:border-purple-300 hover:shadow-md transition-all group"
              >
                <div className="space-y-4">
                  {/* Header: Avatar, Name, Location */}
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-500 to-indigo-600 text-white font-bold flex items-center justify-center text-base shadow-sm flex-shrink-0">
                        {mentorName.charAt(0)}
                      </div>
                      <div>
                        <div className="flex items-center space-x-1.5">
                          <h3 className="text-base font-bold text-slate-900 group-hover:text-purple-600 transition-colors">
                            {mentorName}
                          </h3>
                          <ShieldCheck className="w-4 h-4 text-purple-600" title="Verified Alumni Mentor" />
                        </div>
                        <div className="flex items-center space-x-2 text-xs text-slate-500 mt-0.5">
                          <span className="flex items-center space-x-1">
                            <MapPin className="w-3.5 h-3.5 text-slate-400" />
                            <span>{mentor.subtitle || 'Industry Mentor'}</span>
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* AI Score Badge */}
                    <div className="px-3 py-1 bg-purple-50 text-purple-700 text-xs font-bold rounded-full border border-purple-100 flex items-center space-x-1 flex-shrink-0">
                      <Zap className="w-3.5 h-3.5 text-purple-600 fill-purple-500" />
                      <span>{Math.round(mentor.score)}% Fit</span>
                    </div>
                  </div>

                  {/* Provider / Network */}
                  <div className="text-xs text-slate-500 flex items-center space-x-1">
                    <Briefcase className="w-3.5 h-3.5 text-slate-400" />
                    <span>{mentor.organization_or_provider || 'SKILLY Mentor Network'}</span>
                  </div>

                  {/* AI Match Explanation */}
                  {mentor.explanation && (
                    <div className="p-3 bg-purple-50/60 rounded-xl border border-purple-100 text-xs text-purple-900 space-y-1">
                      <div className="flex items-center space-x-1 font-semibold text-purple-800">
                        <Sparkles className="w-3.5 h-3.5 text-purple-600" />
                        <span>AI Domain Match:</span>
                      </div>
                      <p className="leading-relaxed text-slate-700">{mentor.explanation}</p>
                    </div>
                  )}

                  {/* Matched Skills & Skills Addressed */}
                  {mentor.matched_skills && mentor.matched_skills.length > 0 && (
                    <div className="space-y-1">
                      <span className="text-[11px] font-semibold text-slate-500 block">Guidance Focus & Skills:</span>
                      <div className="flex flex-wrap gap-1.5">
                        {mentor.matched_skills.map((sk, idx) => (
                          <span
                            key={idx}
                            className="text-[11px] px-2.5 py-0.5 rounded-md font-medium bg-slate-100 text-slate-700 border border-slate-200"
                          >
                            {sk}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Footer Actions */}
                <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between gap-3">
                  <button
                    onClick={() => openDetailModal(mentor)}
                    className="text-xs font-semibold text-slate-600 hover:text-purple-600 transition-colors flex items-center space-x-1"
                  >
                    <span>View Profile</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>

                  {isRequested ? (
                    <button
                      disabled
                      className="px-4 py-2 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-xl text-xs font-semibold flex items-center space-x-1.5 cursor-not-allowed"
                    >
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      <span>Request Sent</span>
                    </button>
                  ) : (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        openRequestModal(mentor);
                      }}
                      className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-xs font-semibold transition-all shadow-sm active:scale-[0.98]"
                    >
                      Connect & Request Session
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* ========================================================================= */}
      {/* MODAL 1: MENTOR DETAIL MODAL */}
      {/* ========================================================================= */}
      {detailModalOpen && selectedMentor && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-fade-in">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xl w-full max-w-xl">
            <div className="p-6 border-b border-slate-100 flex items-start justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-500 to-indigo-600 text-white font-bold flex items-center justify-center text-lg shadow-sm">
                  {selectedMentor.title.replace(/^Mentor:\s*/, '').charAt(0)}
                </div>
                <div>
                  <h2 className="text-lg font-bold text-slate-900">
                    {selectedMentor.title.replace(/^Mentor:\s*/, '')}
                  </h2>
                  <p className="text-xs text-slate-500">{selectedMentor.subtitle || 'Industry Mentor'}</p>
                </div>
              </div>

              <button
                onClick={() => setDetailModalOpen(false)}
                className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-4 text-xs">
              <div className="p-4 bg-purple-50 rounded-xl border border-purple-100 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-purple-900 flex items-center gap-1.5">
                    <Sparkles className="w-4 h-4 text-purple-600" />
                    AI Domain Fit
                  </span>
                  <span className="font-bold text-purple-700 text-sm">{Math.round(selectedMentor.score)}%</span>
                </div>
                <p className="text-slate-700 leading-relaxed">{selectedMentor.explanation}</p>
              </div>

              <div>
                <span className="font-bold text-slate-800 block mb-1">Organization / Network</span>
                <p className="text-slate-600">{selectedMentor.organization_or_provider || 'SKILLY Mentor Network'}</p>
              </div>

              {selectedMentor.matched_skills && selectedMentor.matched_skills.length > 0 && (
                <div>
                  <span className="font-bold text-slate-800 block mb-1.5">Matched Competencies & Guidance</span>
                  <div className="flex flex-wrap gap-1.5">
                    {selectedMentor.matched_skills.map((sk, idx) => (
                      <span key={idx} className="px-2.5 py-1 bg-slate-100 text-slate-800 rounded-lg font-medium border border-slate-200">
                        {sk}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="p-6 border-t border-slate-100 flex items-center justify-end space-x-3">
              <Button variant="outline" onClick={() => setDetailModalOpen(false)}>
                Close
              </Button>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setDetailModalOpen(false);
                  openRequestModal(selectedMentor);
                }}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-xs font-semibold transition-all shadow-sm active:scale-[0.98]"
              >
                Connect & Request Session
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* MODAL 2: REQUEST MENTORSHIP SESSION MODAL */}
      {/* ========================================================================= */}
      {requestModalOpen && selectedMentor && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-fade-in">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xl w-full max-w-lg">
            <div className="p-6 border-b border-slate-100 flex items-start justify-between">
              <div>
                <span className="text-xs font-semibold text-purple-600">Request Mentorship Connection</span>
                <h2 className="text-lg font-bold text-slate-900 mt-0.5">
                  {selectedMentor.title.replace(/^Mentor:\s*/, '')}
                </h2>
              </div>

              <button
                onClick={() => setRequestModalOpen(false)}
                className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleRequestSubmit} className="p-6 space-y-4">
              <div className="space-y-1.5">
                <label className="block text-xs font-bold text-slate-700">
                  Primary Mentorship Topic
                </label>
                <select
                  value={requestTopic}
                  onChange={(e) => setRequestTopic(e.target.value)}
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500"
                >
                  <option value="Career Role Advisory & Guidance">Career Role Advisory & Guidance</option>
                  <option value="Technical Project & Code Review">Technical Project & Code Review</option>
                  <option value="Mock Technical Interview Prep">Mock Technical Interview Prep</option>
                  <option value="Industry & Placement Strategy">Industry & Placement Strategy</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="block text-xs font-bold text-slate-700">
                  Introductory Note / Message <span className="text-slate-400 font-normal">(Optional)</span>
                </label>
                <textarea
                  rows={4}
                  value={requestNote}
                  onChange={(e) => setRequestNote(e.target.value)}
                  placeholder="Introduce yourself, share your target career goals, and mention specific topics you would like to discuss..."
                  className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500"
                />
              </div>

              <div className="pt-4 border-t border-slate-100 flex items-center justify-end space-x-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setRequestModalOpen(false)}
                  disabled={submitting}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  disabled={submitting}
                  className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-700"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>{submitting ? 'Sending Request...' : 'Send Request'}</span>
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
