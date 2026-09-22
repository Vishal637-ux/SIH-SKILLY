import React, { useState, useEffect } from 'react';
import { 
  Layers, 
  Sparkles, 
  CheckCircle2, 
  Award, 
  Briefcase, 
  Building2, 
  ExternalLink, 
  Plus, 
  Trash2, 
  AlertCircle,
  FileCheck,
  ShieldCheck,
  Link2,
  X
} from 'lucide-react';
import api from '../../../lib/api';
import Button from '../../../components/Button';
import Loading from '../../../components/Loading';

export default function StudentPortfolioWorkspace() {
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [isAddProjectModalOpen, setIsAddProjectModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // New Project form fields
  const [projTitle, setProjTitle] = useState('');
  const [projDesc, setProjDesc] = useState('');
  const [projRepoUrl, setProjRepoUrl] = useState('');
  const [projLiveUrl, setProjLiveUrl] = useState('');
  const [projRole, setProjRole] = useState('Lead Developer');

  const fetchPortfolio = async () => {
    try {
      setLoading(true);
      setErrorMsg(null);
      const res = await api.get('/student/portfolio');
      setPortfolio(res.data || null);
    } catch (err) {
      console.error('Failed to fetch digital portfolio:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to load verified digital portfolio.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPortfolio();
  }, []);

  const handleAddProject = async (e) => {
    e.preventDefault();
    try {
      setIsSubmitting(true);
      setErrorMsg(null);
      const payload = {
        item_type: 'PROJECT',
        title: projTitle,
        description: projDesc,
        repository_url: projRepoUrl || null,
        live_url: projLiveUrl || null,
        role_in_project: projRole,
      };
      await api.post('/student/portfolio/projects', payload);
      setIsAddProjectModalOpen(false);
      setProjTitle('');
      setProjDesc('');
      setProjRepoUrl('');
      setProjLiveUrl('');
      await fetchPortfolio();
    } catch (err) {
      console.error('Failed to add project:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to add portfolio project.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteProject = async (projectId) => {
    if (!window.confirm('Are you sure you want to delete this portfolio project?')) return;
    try {
      setErrorMsg(null);
      await api.delete(`/student/portfolio/projects/${projectId}`);
      await fetchPortfolio();
    } catch (err) {
      console.error('Failed to delete project:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to delete portfolio project.');
    }
  };

  if (loading) {
    return <Loading label="Loading verified digital portfolio..." />;
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
          <Button variant="outline" size="sm" onClick={fetchPortfolio}>
            Retry
          </Button>
        </div>
      )}

      {/* Workspace Header */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-indigo-50 text-indigo-600 rounded-2xl border border-indigo-100">
              <Layers className="w-7 h-7" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900">Verified Digital Portfolio & Passport</h1>
              <p className="text-sm text-slate-500">
                Authoritative record of your verified projects, certifications, competency seals, and placement evidence.
              </p>
            </div>
          </div>

          <Button 
            variant="primary" 
            size="sm" 
            icon={<Plus className="w-4 h-4" />}
            onClick={() => setIsAddProjectModalOpen(true)}
          >
            Add Portfolio Project
          </Button>
        </div>

        {/* Metric Overview */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 pt-6 mt-6 border-t border-slate-100">
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
            <span className="block text-xs font-semibold text-slate-400 uppercase">Portfolio Score</span>
            <span className="text-2xl font-bold text-emerald-600">{portfolio?.portfolio_score || 0}%</span>
          </div>

          <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
            <span className="block text-xs font-semibold text-slate-400 uppercase">Verified Seals</span>
            <span className="text-2xl font-bold text-blue-600">{portfolio?.verified_evidence_count || 0}</span>
          </div>

          <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
            <span className="block text-xs font-semibold text-slate-400 uppercase">Projects</span>
            <span className="text-2xl font-bold text-slate-900">{portfolio?.projects?.length || 0}</span>
          </div>

          <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
            <span className="block text-xs font-semibold text-slate-400 uppercase">Certifications</span>
            <span className="text-2xl font-bold text-indigo-600">{portfolio?.certifications?.length || 0}</span>
          </div>
        </div>
      </div>

      {/* Projects Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
            <FileCheck className="w-5 h-5 text-blue-600" />
            <span>Technical Projects & Deliverables</span>
          </h2>
          <button 
            onClick={() => setIsAddProjectModalOpen(true)}
            className="text-xs font-bold text-blue-600 hover:text-blue-700 flex items-center space-x-1"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Project</span>
          </button>
        </div>

        {portfolio?.projects?.length === 0 ? (
          <div className="bg-white border border-slate-200 rounded-2xl p-8 text-center space-y-3">
            <p className="text-sm text-slate-500">No portfolio projects added yet.</p>
            <Button variant="outline" size="sm" onClick={() => setIsAddProjectModalOpen(true)}>
              Add Your First Project
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {portfolio?.projects?.map((p) => (
              <div key={p.id} className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs flex flex-col justify-between space-y-3">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                      {p.role_in_project || 'Project'}
                    </span>
                    <button 
                      onClick={() => handleDeleteProject(p.id)}
                      className="p-1 text-slate-400 hover:text-rose-600 transition-colors"
                      title="Delete project"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <h3 className="text-base font-bold text-slate-900">{p.title}</h3>
                  <p className="text-xs text-slate-600 line-clamp-3">{p.description}</p>
                </div>

                <div className="flex items-center space-x-3 pt-3 border-t border-slate-100 text-xs">
                  {p.repository_url && (
                    <a href={p.repository_url} target="_blank" rel="noreferrer" className="text-blue-600 font-semibold hover:underline flex items-center space-x-1">
                      <span>GitHub Repository</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                  {p.live_url && (
                    <a href={p.live_url} target="_blank" rel="noreferrer" className="text-emerald-600 font-semibold hover:underline flex items-center space-x-1">
                      <span>Live Demo</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add Project Modal */}
      {isAddProjectModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
          <div className="bg-white rounded-3xl border border-slate-200 max-w-lg w-full p-6 shadow-2xl space-y-5 animate-fadeIn">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h2 className="text-lg font-bold text-slate-900">Add Portfolio Project</h2>
              <button onClick={() => setIsAddProjectModalOpen(false)} className="p-1 text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddProject} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Project Title</label>
                <input 
                  type="text"
                  required
                  value={projTitle}
                  onChange={(e) => setProjTitle(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-blue-500"
                  placeholder="e.g. Distributed E-Commerce Microservices Platform"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Role in Project</label>
                <input 
                  type="text"
                  value={projRole}
                  onChange={(e) => setProjRole(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-blue-500"
                  placeholder="e.g. Lead Backend Engineer"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Description</label>
                <textarea 
                  required
                  rows={3}
                  value={projDesc}
                  onChange={(e) => setProjDesc(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-blue-500"
                  placeholder="Describe your architecture, tech stack, and key technical achievements..."
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Repository URL</label>
                  <input 
                    type="url"
                    value={projRepoUrl}
                    onChange={(e) => setProjRepoUrl(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-blue-500"
                    placeholder="https://github.com/username/repo"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Live Demo URL</label>
                  <input 
                    type="url"
                    value={projLiveUrl}
                    onChange={(e) => setProjLiveUrl(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-blue-500"
                    placeholder="https://myproject.vercel.app"
                  />
                </div>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-end space-x-2">
                <Button type="button" variant="outline" size="sm" onClick={() => setIsAddProjectModalOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" variant="primary" size="sm" disabled={isSubmitting}>
                  {isSubmitting ? 'Saving...' : 'Add Project'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
