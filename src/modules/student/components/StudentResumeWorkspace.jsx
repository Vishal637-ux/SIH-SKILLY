import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Sparkles, 
  Download, 
  Eye, 
  Plus, 
  CheckCircle2, 
  AlertCircle, 
  Layers, 
  Briefcase, 
  Award, 
  Building2, 
  GraduationCap,
  Calendar,
  X
} from 'lucide-react';
import api from '../../../lib/api';
import Button from '../../../components/Button';
import Loading from '../../../components/Loading';

export default function StudentResumeWorkspace() {
  const [resumes, setResumes] = useState([]);
  const [careerRoles, setCareerRoles] = useState([]);
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [selectedResume, setSelectedResume] = useState(null);
  const [isGenerateModalOpen, setIsGenerateModalOpen] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  // Form State for Resume Generation
  const [genTitle, setGenTitle] = useState('Full-Stack Software Engineer Resume');
  const [genTargetRole, setGenTargetRole] = useState('');
  const [genIncludeProjects, setGenIncludeProjects] = useState(true);
  const [genIncludeCerts, setGenIncludeCerts] = useState(true);
  const [genIncludeInternships, setGenIncludeInternships] = useState(true);

  const fetchData = async () => {
    try {
      setLoading(true);
      setErrorMsg(null);
      const [resumesRes, rolesRes, portfolioRes] = await Promise.all([
        api.get('/student/resumes').catch(() => ({ data: [] })),
        api.get('/student/career-roles').catch(() => ({ data: [] })),
        api.get('/student/portfolio').catch(() => ({ data: null })),
      ]);
      setResumes(resumesRes.data || []);
      setCareerRoles(rolesRes.data || []);
      setPortfolio(portfolioRes.data || null);
    } catch (err) {
      console.error('Failed to fetch resume workspace data:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to load resume versions.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleGenerateResume = async (e) => {
    e.preventDefault();
    try {
      setIsGenerating(true);
      setErrorMsg(null);
      const payload = {
        title: genTitle,
        target_role_id: genTargetRole || null,
        include_projects: genIncludeProjects,
        include_certifications: genIncludeCerts,
        include_internships: genIncludeInternships,
      };
      const res = await api.post('/student/resumes/generate', payload);
      setResumes([res.data, ...resumes]);
      setIsGenerateModalOpen(false);
      setSelectedResume(res.data);
    } catch (err) {
      console.error('Failed to generate resume:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to generate tailored resume version.');
    } finally {
      setIsGenerating(false);
    }
  };

  if (loading) {
    return <Loading label="Loading resume versions & portfolio data..." />;
  }

  return (
    <div className="space-y-6">
      {/* Error Alert Banner */}
      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-sm flex items-center justify-between shadow-sm">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0" />
            <span className="font-medium">{errorMsg}</span>
          </div>
          <Button variant="outline" size="sm" onClick={fetchData}>
            Retry
          </Button>
        </div>
      )}

      {/* Workspace Header */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-blue-50 text-blue-600 rounded-2xl border border-blue-100">
              <FileText className="w-7 h-7" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900">Resume Versions & Management</h1>
              <p className="text-sm text-slate-500">
                Generate ATS-friendly, role-targeted resume versions synced directly with your verified skill passport.
              </p>
            </div>
          </div>

          <Button 
            variant="primary" 
            size="sm" 
            icon={<Plus className="w-4 h-4" />}
            onClick={() => setIsGenerateModalOpen(true)}
          >
            Generate New Resume Version
          </Button>
        </div>

        {/* Summary Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-6 mt-6 border-t border-slate-100">
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
            <span className="block text-xs font-semibold text-slate-400 uppercase">Saved Versions</span>
            <span className="text-2xl font-bold text-slate-900">{resumes.length}</span>
          </div>

          <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
            <span className="block text-xs font-semibold text-slate-400 uppercase">Portfolio Score</span>
            <span className="text-2xl font-bold text-emerald-600">
              {portfolio?.portfolio_score !== undefined ? `${portfolio.portfolio_score}%` : 'N/A'}
            </span>
          </div>

          <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
            <span className="block text-xs font-semibold text-slate-400 uppercase">Verified Seals</span>
            <span className="text-2xl font-bold text-blue-600">
              {portfolio?.verified_evidence_count || 0}
            </span>
          </div>
        </div>
      </div>

      {/* Resumes List */}
      {resumes.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-2xl p-10 text-center space-y-4 shadow-sm">
          <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto">
            <FileText className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-slate-900">No Tailored Resumes Generated Yet</h3>
          <p className="text-sm text-slate-500 max-w-md mx-auto">
            Generate your first role-targeted resume version. It will automatically aggregate your verified skills, projects, and academic credentials.
          </p>
          <div className="pt-2">
            <Button 
              variant="primary" 
              size="sm" 
              icon={<Sparkles className="w-4 h-4" />}
              onClick={() => setIsGenerateModalOpen(true)}
            >
              Generate Tailored Resume
            </Button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {resumes.map((res) => (
            <div 
              key={res.id}
              className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs hover:border-blue-300 transition-all flex flex-col justify-between space-y-4"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                    {res.target_role_title || 'General Resume'}
                  </span>
                  <span className="text-xs text-slate-400 flex items-center space-x-1">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>{new Date(res.created_at).toLocaleDateString()}</span>
                  </span>
                </div>

                <h3 className="text-lg font-bold text-slate-900">{res.title}</h3>

                {/* Parsed summary preview */}
                {res.parsed_content && (
                  <div className="bg-slate-50 p-3 rounded-xl border border-slate-100 text-xs text-slate-600 space-y-1.5">
                    <p className="font-medium text-slate-800 line-clamp-2">
                      {res.parsed_content.summary}
                    </p>
                    <div className="flex items-center space-x-3 text-[11px] text-slate-500 pt-1">
                      <span>Skills: <strong>{res.parsed_content.skills?.length || 0}</strong></span>
                      <span>•</span>
                      <span>Projects: <strong>{res.parsed_content.projects?.length || 0}</strong></span>
                      <span>•</span>
                      <span>Certs: <strong>{res.parsed_content.certifications?.length || 0}</strong></span>
                    </div>
                  </div>
                )}
              </div>

              <div className="flex items-center space-x-2 pt-3 border-t border-slate-100">
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="flex-1 justify-center"
                  icon={<Eye className="w-4 h-4" />}
                  onClick={() => setSelectedResume(res)}
                >
                  View Details
                </Button>
                {res.file_url && (
                  <a href={res.file_url} target="_blank" rel="noreferrer" className="flex-1">
                    <Button variant="primary" size="sm" className="w-full justify-center" icon={<Download className="w-4 h-4" />}>
                      Export PDF
                    </Button>
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Generate Resume Modal */}
      {isGenerateModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
          <div className="bg-white rounded-3xl border border-slate-200 max-w-lg w-full p-6 shadow-2xl space-y-5 animate-fadeIn">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-5 h-5 text-blue-600" />
                <h2 className="text-lg font-bold text-slate-900">Generate Structured Resume</h2>
              </div>
              <button 
                onClick={() => setIsGenerateModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleGenerateResume} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Resume Version Title</label>
                <input 
                  type="text"
                  required
                  value={genTitle}
                  onChange={(e) => setGenTitle(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-blue-500"
                  placeholder="e.g. Full-Stack Engineer Resume"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Target Career Goal</label>
                <select
                  value={genTargetRole}
                  onChange={(e) => setGenTargetRole(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-blue-500"
                >
                  <option value="">-- General / Default Target Role --</option>
                  {careerRoles.map((role) => (
                    <option key={role.id} value={role.id}>{role.title} ({role.industry_domain})</option>
                  ))}
                </select>
              </div>

              <div className="space-y-2 pt-2">
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Include Portfolio Sections</label>
                
                <label className="flex items-center space-x-2 text-xs text-slate-700 font-medium">
                  <input 
                    type="checkbox"
                    checked={genIncludeProjects}
                    onChange={(e) => setGenIncludeProjects(e.target.checked)}
                    className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span>Include Portfolio Projects</span>
                </label>

                <label className="flex items-center space-x-2 text-xs text-slate-700 font-medium">
                  <input 
                    type="checkbox"
                    checked={genIncludeCerts}
                    onChange={(e) => setGenIncludeCerts(e.target.checked)}
                    className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span>Include Certifications & Recognitions</span>
                </label>

                <label className="flex items-center space-x-2 text-xs text-slate-700 font-medium">
                  <input 
                    type="checkbox"
                    checked={genIncludeInternships}
                    onChange={(e) => setGenIncludeInternships(e.target.checked)}
                    className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span>Include Internships & Work Experience</span>
                </label>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-end space-x-2">
                <Button 
                  type="button" 
                  variant="outline" 
                  size="sm" 
                  onClick={() => setIsGenerateModalOpen(false)}
                >
                  Cancel
                </Button>
                <Button 
                  type="submit" 
                  variant="primary" 
                  size="sm"
                  disabled={isGenerating}
                  icon={<Sparkles className="w-4 h-4" />}
                >
                  {isGenerating ? 'Generating...' : 'Generate Resume'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Resume Viewer Drawer/Modal */}
      {selectedResume && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs">
          <div className="bg-white rounded-3xl border border-slate-200 max-w-2xl w-full max-h-[85vh] overflow-y-auto p-6 shadow-2xl space-y-6 animate-fadeIn">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <span className="text-xs font-bold text-blue-600 uppercase tracking-wider">Structured JSON Resume</span>
                <h2 className="text-xl font-bold text-slate-900">{selectedResume.title}</h2>
              </div>
              <button 
                onClick={() => setSelectedResume(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {selectedResume.parsed_content && (
              <div className="space-y-6 text-sm">
                {/* Header */}
                <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200/80 space-y-2">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-bold text-slate-900">{selectedResume.parsed_content.header?.name}</h3>
                    <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-800">
                      {selectedResume.parsed_content.header?.target_role || 'General Candidate'}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600">
                    {selectedResume.parsed_content.header?.institution} • {selectedResume.parsed_content.header?.department} • Roll: {selectedResume.parsed_content.header?.roll_number}
                  </p>
                </div>

                {/* Summary */}
                <div className="space-y-1">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Professional Summary</h4>
                  <p className="text-slate-700 leading-relaxed bg-white p-3 rounded-xl border border-slate-100">
                    {selectedResume.parsed_content.summary}
                  </p>
                </div>

                {/* Skills */}
                <div className="space-y-2">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Verified Competency Skills</h4>
                  <div className="flex flex-wrap gap-1.5">
                    {(selectedResume.parsed_content.skills || []).map((s, idx) => (
                      <span key={idx} className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        {s.skill_name} ({s.proficiency_level})
                      </span>
                    ))}
                  </div>
                </div>

                {/* Projects */}
                {selectedResume.parsed_content.projects?.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Portfolio Projects</h4>
                    <div className="space-y-2">
                      {selectedResume.parsed_content.projects.map((p, idx) => (
                        <div key={idx} className="p-3 bg-slate-50 rounded-xl border border-slate-200/60">
                          <h5 className="font-bold text-slate-900">{p.title}</h5>
                          <p className="text-xs text-slate-600">{p.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            <div className="pt-3 border-t border-slate-100 flex items-center justify-end">
              <Button variant="outline" size="sm" onClick={() => setSelectedResume(null)}>
                Close Preview
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
