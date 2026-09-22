import React, { useState, useEffect } from 'react';
import { 
  Layers, 
  Search, 
  CheckCircle2, 
  Award, 
  TrendingUp, 
  AlertCircle, 
  Sparkles, 
  ExternalLink,
  BookOpen,
  ArrowRight
} from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../../../lib/api';
import Button from '../../../components/Button';
import Loading from '../../../components/Loading';

export default function StudentSkillsWorkspace() {
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');

  const fetchStudentSkills = async () => {
    try {
      setLoading(true);
      setErrorMsg(null);
      const res = await api.get('/student/skills');
      setSkills(res.data || []);
    } catch (err) {
      console.error('Failed to fetch student skills:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to load verified skill profile.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudentSkills();
  }, []);

  if (loading) {
    return <Loading label="Loading verified skill profile..." />;
  }

  // Derive unique categories
  const categories = ['ALL', ...Array.from(new Set(skills.map(s => s.skill_category).filter(Boolean)))];

  // Filter skills by search query and selected category
  const filteredSkills = skills.filter((item) => {
    const matchesSearch = 
      (item.skill_name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (item.skill_category || '').toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'ALL' || item.skill_category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  // Calculate metrics
  const verifiedCount = skills.filter(s => s.verification_status === 'VERIFIED').length;
  const scores = skills.map(s => Number(s.score)).filter(score => !isNaN(score) && score > 0);
  const avgScore = scores.length > 0 ? (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1) : 0;

  const getProficiencyColor = (level) => {
    switch ((level || '').toUpperCase()) {
      case 'EXPERT':
        return 'bg-purple-50 text-purple-700 border-purple-200';
      case 'ADVANCED':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'INTERMEDIATE':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'BEGINNER':
      default:
        return 'bg-amber-50 text-amber-700 border-amber-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Error Alert Banner */}
      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-sm flex items-center justify-between shadow-sm">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0" />
            <span className="font-medium">{errorMsg}</span>
          </div>
          <Button variant="outline" size="sm" onClick={fetchStudentSkills}>
            Retry
          </Button>
        </div>
      )}

      {/* Workspace Header */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-blue-50 text-blue-600 rounded-2xl border border-blue-100">
              <Layers className="w-7 h-7" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900">Verified Skill Passport</h1>
              <p className="text-sm text-slate-500">
                Authoritative breakdown of your verified competencies, proficiency scores, and digital evidence artifacts.
              </p>
            </div>
          </div>

          <Link to="/student/assessments">
            <Button variant="primary" size="sm" icon={<Sparkles className="w-4 h-4" />}>
              Take Skill Assessment
            </Button>
          </Link>
        </div>

        {/* Summary Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-6 mt-6 border-t border-slate-100">
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
            <span className="block text-xs font-semibold text-slate-400 uppercase">Assessed Skills</span>
            <span className="text-2xl font-bold text-slate-900">{skills.length}</span>
          </div>

          <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
            <span className="block text-xs font-semibold text-slate-400 uppercase">Verified Seals</span>
            <span className="text-2xl font-bold text-emerald-600">{verifiedCount}</span>
          </div>

          <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
            <span className="block text-xs font-semibold text-slate-400 uppercase">Avg Competency Score</span>
            <span className="text-2xl font-bold text-blue-600">{avgScore > 0 ? `${avgScore}%` : 'N/A'}</span>
          </div>
        </div>
      </div>

      {/* Filter & Search Toolbar */}
      <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Search Bar */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search skills by name or category..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
          />
        </div>

        {/* Category Pills */}
        <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 md:pb-0 scrollbar-none">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                selectedCategory === cat
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Skills Grid */}
      {filteredSkills.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-2xl p-10 text-center space-y-4 shadow-sm">
          <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto">
            <Award className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-slate-900">
            {skills.length === 0 ? 'No Verified Skills Assessed Yet' : 'No Matching Skills Found'}
          </h3>
          <p className="text-sm text-slate-500 max-w-md mx-auto">
            {skills.length === 0
              ? 'Complete a diagnostic skill assessment to benchmark your competencies, earn verified digital seals, and populate your skill passport.'
              : 'No skills match your current search query or category filter.'}
          </p>
          <div className="pt-2">
            <Link to="/student/assessments">
              <Button variant="primary" size="sm" icon={<ArrowRight className="w-4 h-4" />}>
                Browse Diagnostic Assessments
              </Button>
            </Link>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredSkills.map((sk) => {
            const scoreVal = sk.score !== null ? Number(sk.score) : 0;
            const isVerified = sk.verification_status === 'VERIFIED';

            return (
              <div
                key={sk.id}
                className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs hover:shadow-md hover:border-blue-300 transition-all flex flex-col justify-between space-y-4"
              >
                <div className="space-y-3">
                  {/* Category & Verification Badges */}
                  <div className="flex items-center justify-between">
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200">
                      {sk.skill_category || 'General'}
                    </span>

                    {isVerified && (
                      <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                        <span>Verified</span>
                      </span>
                    )}
                  </div>

                  {/* Skill Name */}
                  <h3 className="text-lg font-bold text-slate-900">{sk.skill_name}</h3>

                  {/* Proficiency Badge */}
                  <div className="flex items-center space-x-2">
                    <span className={`px-2.5 py-1 rounded-lg text-xs font-bold border ${getProficiencyColor(sk.proficiency_level)}`}>
                      {sk.proficiency_level || 'ASSESSED'}
                    </span>
                    {sk.last_assessed_at && (
                      <span className="text-xs text-slate-400">
                        Assessed {new Date(sk.last_assessed_at).toLocaleDateString()}
                      </span>
                    )}
                  </div>

                  {/* Score Progress Bar */}
                  {sk.score !== null && (
                    <div className="space-y-1.5 pt-1">
                      <div className="flex items-center justify-between text-xs font-semibold">
                        <span className="text-slate-500">Benchmark Score</span>
                        <span className="text-slate-900 font-bold">{scoreVal}%</span>
                      </div>
                      <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-600 rounded-full transition-all duration-500"
                          style={{ width: `${Math.min(100, Math.max(0, scoreVal))}%` }}
                        />
                      </div>
                    </div>
                  )}

                  {/* Evidence Attachments */}
                  {Array.isArray(sk.evidence) && sk.evidence.length > 0 && (
                    <div className="space-y-2 pt-3 border-t border-slate-100">
                      <span className="block text-xs font-semibold text-slate-400 uppercase">
                        Evidence ({sk.evidence.length})
                      </span>
                      <div className="space-y-1.5">
                        {sk.evidence.map((ev) => (
                          <div
                            key={ev.id}
                            className="p-2 bg-slate-50 rounded-lg border border-slate-100 flex items-center justify-between text-xs"
                          >
                            <span className="font-medium text-slate-700 truncate pr-2">
                              {ev.title || ev.evidence_type}
                            </span>
                            {ev.url ? (
                              <a
                                href={ev.url}
                                target="_blank"
                                rel="noreferrer"
                                className="text-blue-600 hover:text-blue-800 font-semibold flex items-center space-x-1 flex-shrink-0"
                              >
                                <span>Link</span>
                                <ExternalLink className="w-3 h-3" />
                              </a>
                            ) : (
                              <span className="text-[10px] font-semibold text-slate-400 uppercase bg-slate-200/60 px-1.5 py-0.5 rounded">
                                {ev.evidence_type}
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Footer Action */}
                <div className="pt-3 border-t border-slate-100">
                  <Link to="/student/assessments" className="block">
                    <Button variant="outline" size="sm" className="w-full">
                      Upgrade & Retake Assessment
                    </Button>
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
