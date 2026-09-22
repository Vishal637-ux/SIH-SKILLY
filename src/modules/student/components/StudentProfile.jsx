import React, { useState, useEffect } from 'react';
import { 
  User, 
  Building2, 
  GraduationCap, 
  Target, 
  Save, 
  RotateCcw,
  CheckCircle2, 
  AlertCircle, 
  Loader2, 
  Phone, 
  MapPin, 
  Globe, 
  Linkedin, 
  Github, 
  BookOpen,
  Calendar,
  Sparkles,
  Info,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import api from '../../../lib/api';
import useAuth from '../../../hooks/useAuth';
import Button from '../../../components/Button';
import Loading from '../../../components/Loading';

export default function StudentProfile() {
  const { user, refreshUser } = useAuth();
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [showMissingFields, setShowMissingFields] = useState(false);

  // Lookups data
  const [institutions, setInstitutions] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [careerRoles, setCareerRoles] = useState([]);
  const [loadingDepts, setLoadingDepts] = useState(false);

  // Active tab
  const [activeTab, setActiveTab] = useState('personal'); // 'personal' | 'academic' | 'career'

  // Completion metrics
  const [completion, setCompletion] = useState({
    percentage: 0,
    is_complete: false,
    personal_percentage: 0,
    academic_percentage: 0,
    career_percentage: 0,
    missing_fields: []
  });

  // Initial State for Reset/Cancel
  const [initialFormData, setInitialFormData] = useState(null);

  // Form State
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    bio: '',
    city: '',
    state: '',
    country: 'India',
    linkedin_url: '',
    github_url: '',
    website_url: '',
    institution_id: '',
    department_id: '',
    roll_number: '',
    enrollment_year: new Date().getFullYear() - 1,
    graduation_year: new Date().getFullYear() + 3,
    current_semester: 1,
    cgpa: '',
    target_career_role_id: '',
  });

  // Fetch initial profile & lookups
  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        setErrorMsg(null);

        // Fetch lookups and profile in parallel
        const [profRes, instRes, rolesRes] = await Promise.all([
          api.get('/student/profile'),
          api.get('/student/institutions').catch(() => ({ data: [] })),
          api.get('/student/career-roles').catch(() => ({ data: [] })),
        ]);

        setInstitutions(instRes.data || []);
        setCareerRoles(rolesRes.data || []);

        const prof = profRes.data;
        const u = prof.user;
        const p = u?.profile;
        const a = prof.academic_profile;
        const comp = prof.completion || {
          percentage: prof.is_profile_complete ? 100 : 0,
          is_complete: prof.is_profile_complete,
          personal_percentage: 0,
          academic_percentage: 0,
          career_percentage: 0,
          missing_fields: []
        };
        setCompletion(comp);

        const loadedForm = {
          first_name: p?.first_name || '',
          last_name: p?.last_name || '',
          phone: p?.phone || '',
          bio: p?.bio || '',
          city: p?.city || '',
          state: p?.state || '',
          country: p?.country || 'India',
          linkedin_url: p?.linkedin_url || '',
          github_url: p?.github_url || '',
          website_url: p?.website_url || '',
          institution_id: a?.institution_id || '',
          department_id: a?.department_id || '',
          roll_number: a?.roll_number || '',
          enrollment_year: a?.enrollment_year || new Date().getFullYear() - 1,
          graduation_year: a?.graduation_year || new Date().getFullYear() + 3,
          current_semester: a?.current_semester || 1,
          cgpa: a?.cgpa !== null && a?.cgpa !== undefined ? String(a.cgpa) : '',
          target_career_role_id: a?.target_career_role_id || '',
        };

        setFormData(loadedForm);
        setInitialFormData(loadedForm);

        // If student has an institution, fetch its departments
        if (a?.institution_id) {
          try {
            const deptRes = await api.get(`/student/departments?institution_id=${a.institution_id}`);
            setDepartments(deptRes.data || []);
          } catch (e) {
            console.warn('Failed to load departments:', e);
          }
        }
      } catch (err) {
        console.error('Failed to load student profile:', err);
        setErrorMsg(err.response?.data?.detail || 'Failed to load profile data.');
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  // Handle Institution Change
  const handleInstitutionChange = async (e) => {
    const instId = e.target.value;
    setFormData((prev) => ({
      ...prev,
      institution_id: instId,
      department_id: '', // Reset selected department on institution change
    }));

    if (!instId) {
      setDepartments([]);
      return;
    }

    try {
      setLoadingDepts(true);
      const res = await api.get(`/student/departments?institution_id=${instId}`);
      setDepartments(res.data || []);
    } catch (err) {
      console.warn('Failed to load departments for institution:', err);
      setDepartments([]);
    } finally {
      setLoadingDepts(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // Reset/Cancel Changes
  const handleCancel = () => {
    if (initialFormData) {
      setFormData(initialFormData);
      setErrorMsg(null);
      setSuccessMsg('Changes reverted.');
      setTimeout(() => setSuccessMsg(null), 3000);
    }
  };

  // Check if form is modified
  const isDirty = initialFormData && JSON.stringify(formData) !== JSON.stringify(initialFormData);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSuccessMsg(null);
    setErrorMsg(null);

    // Client-side validations
    if (formData.cgpa !== '' && formData.cgpa !== null) {
      const cgpaVal = parseFloat(formData.cgpa);
      if (isNaN(cgpaVal) || cgpaVal < 0.0 || cgpaVal > 10.0) {
        setErrorMsg('CGPA must be a valid number between 0.00 and 10.00.');
        setSaving(false);
        return;
      }
    }

    if (formData.current_semester) {
      const semVal = parseInt(formData.current_semester, 10);
      if (isNaN(semVal) || semVal < 1 || semVal > 12) {
        setErrorMsg('Current semester must be between 1 and 12.');
        setSaving(false);
        return;
      }
    }

    if (formData.enrollment_year && formData.graduation_year) {
      const enYear = parseInt(formData.enrollment_year, 10);
      const grYear = parseInt(formData.graduation_year, 10);
      if (grYear < enYear) {
        setErrorMsg('Graduation year cannot be earlier than enrollment year.');
        setSaving(false);
        return;
      }
    }

    try {
      // Build clean payload
      const payload = {
        first_name: formData.first_name || null,
        last_name: formData.last_name || null,
        phone: formData.phone || null,
        bio: formData.bio || null,
        city: formData.city || null,
        state: formData.state || null,
        country: formData.country || 'India',
        linkedin_url: formData.linkedin_url || null,
        github_url: formData.github_url || null,
        website_url: formData.website_url || null,
      };

      // Include academic fields if provided
      if (formData.institution_id) {
        payload.institution_id = formData.institution_id;
      }
      if (formData.department_id) {
        payload.department_id = formData.department_id;
      }
      if (formData.roll_number) {
        payload.roll_number = formData.roll_number;
      }
      if (formData.enrollment_year) {
        payload.enrollment_year = parseInt(formData.enrollment_year, 10);
      }
      if (formData.graduation_year) {
        payload.graduation_year = parseInt(formData.graduation_year, 10);
      }
      if (formData.current_semester) {
        payload.current_semester = parseInt(formData.current_semester, 10);
      }
      if (formData.cgpa !== '' && formData.cgpa !== null) {
        payload.cgpa = parseFloat(formData.cgpa);
      }
      if (formData.target_career_role_id) {
        payload.target_career_role_id = formData.target_career_role_id;
      }

      const res = await api.put('/student/profile', payload);
      const updatedProfile = res.data;
      if (updatedProfile?.completion) {
        setCompletion(updatedProfile.completion);
      }
      setInitialFormData(formData);
      setSuccessMsg('Profile updated successfully!');
      if (refreshUser) {
        refreshUser();
      }
    } catch (err) {
      console.error('Profile update failed:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to update profile. Please verify your inputs.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[400px] flex items-center justify-center">
        <Loading message="Loading student profile & academic records..." />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top Header Card */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-soft">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white flex items-center justify-center font-bold text-xl shadow-md shadow-blue-500/20 shrink-0">
              {formData.first_name ? formData.first_name[0].toUpperCase() : 'S'}
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <h1 className="text-2xl font-black text-slate-900">
                  {formData.first_name || 'Student'} {formData.last_name || ''}
                </h1>
                <span className="px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-700 text-xs font-bold">
                  STUDENT
                </span>
                {completion.is_complete ? (
                  <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    Verified Academic Identity
                  </span>
                ) : (
                  <span className="px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800 text-xs font-bold flex items-center gap-1">
                    <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
                    Profile Incomplete
                  </span>
                )}
              </div>
              <p className="text-xs sm:text-sm text-slate-500 mt-0.5">{user?.email}</p>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-wrap w-full md:w-auto">
            <button
              type="button"
              onClick={() => setActiveTab('personal')}
              className={`flex-1 md:flex-initial px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                activeTab === 'personal'
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              <User className="w-3.5 h-3.5" />
              <span>Personal</span>
              <span className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                activeTab === 'personal' ? 'bg-blue-700 text-white' : 'bg-slate-200 text-slate-700'
              }`}>
                {completion.personal_percentage}%
              </span>
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('academic')}
              className={`flex-1 md:flex-initial px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                activeTab === 'academic'
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              <Building2 className="w-3.5 h-3.5" />
              <span>Academic</span>
              <span className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                activeTab === 'academic' ? 'bg-blue-700 text-white' : 'bg-slate-200 text-slate-700'
              }`}>
                {completion.academic_percentage}%
              </span>
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('career')}
              className={`flex-1 md:flex-initial px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                activeTab === 'career'
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              <Target className="w-3.5 h-3.5" />
              <span>Career</span>
              <span className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                activeTab === 'career' ? 'bg-blue-700 text-white' : 'bg-slate-200 text-slate-700'
              }`}>
                {completion.career_percentage}%
              </span>
            </button>
          </div>
        </div>
      </div>

      {/* Profile Completion Progress Card */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white rounded-2xl p-6 shadow-soft relative overflow-hidden">
        <div className="relative z-10 space-y-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-indigo-400" />
              <h2 className="text-base font-bold text-white">Profile & Identity Completion</h2>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-2xl font-black text-indigo-300">
                {completion.percentage}%
              </span>
              <span className="text-xs text-slate-400">Complete</span>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-slate-800 rounded-full h-3 overflow-hidden p-0.5 border border-slate-700">
            <div 
              className={`h-full rounded-full transition-all duration-700 ${
                completion.percentage === 100 
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-400' 
                  : 'bg-gradient-to-r from-blue-500 to-indigo-500'
              }`}
              style={{ width: `${Math.max(5, completion.percentage)}%` }}
            />
          </div>

          {/* Sub-breakdown chips */}
          <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-slate-300 pt-1">
            <div className="flex items-center gap-4">
              <span>Personal: <strong className="text-white">{completion.personal_percentage}%</strong></span>
              <span>•</span>
              <span>Academic: <strong className="text-white">{completion.academic_percentage}%</strong></span>
              <span>•</span>
              <span>Career Goal: <strong className="text-white">{completion.career_percentage}%</strong></span>
            </div>

            {completion.missing_fields && completion.missing_fields.length > 0 && (
              <button
                type="button"
                onClick={() => setShowMissingFields(!showMissingFields)}
                className="text-indigo-300 hover:text-indigo-200 text-xs flex items-center gap-1 font-medium transition-colors"
              >
                <span>{completion.missing_fields.length} Recommended Action{completion.missing_fields.length > 1 ? 's' : ''}</span>
                {showMissingFields ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>
            )}
          </div>

          {/* Missing fields list */}
          {showMissingFields && completion.missing_fields && completion.missing_fields.length > 0 && (
            <div className="mt-3 p-3 bg-slate-800/80 border border-slate-700 rounded-xl text-xs space-y-1.5 animate-fadeIn">
              <div className="text-slate-400 font-medium">Complete these fields to reach 100%:</div>
              <div className="flex flex-wrap gap-2 pt-1">
                {completion.missing_fields.map((field, idx) => (
                  <span key={idx} className="px-2 py-0.5 rounded-md bg-indigo-900/60 border border-indigo-700/50 text-indigo-200 text-[11px]">
                    {field}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Alerts */}
      {successMsg && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center justify-between gap-3 text-xs sm:text-sm text-emerald-800 animate-fadeIn">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
            <span>{successMsg}</span>
          </div>
          <button 
            type="button" 
            onClick={() => setSuccessMsg(null)}
            className="text-emerald-700 hover:text-emerald-900 text-xs font-bold"
          >
            ✕
          </button>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl flex items-center justify-between gap-3 text-xs sm:text-sm text-red-800 animate-fadeIn">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 shrink-0" />
            <span>{errorMsg}</span>
          </div>
          <button 
            type="button" 
            onClick={() => setErrorMsg(null)}
            className="text-red-700 hover:text-red-900 text-xs font-bold"
          >
            ✕
          </button>
        </div>
      )}

      {/* Form Card */}
      <form onSubmit={handleSubmit} className="bg-white rounded-2xl border border-slate-200/80 p-6 sm:p-8 shadow-soft space-y-6">
        
        {/* TAB 1: PERSONAL & CONTACT INFORMATION */}
        {activeTab === 'personal' && (
          <div className="space-y-6">
            <div className="border-b border-slate-100 pb-4">
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <User className="w-5 h-5 text-blue-600" />
                <span>Biographical & Contact Information</span>
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                Your personal details help mentors and placement officers contact you.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  First Name *
                </label>
                <input
                  type="text"
                  name="first_name"
                  required
                  value={formData.first_name}
                  onChange={handleChange}
                  placeholder="e.g. Jordan"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Last Name
                </label>
                <input
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  placeholder="e.g. Lee"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Email Address
                </label>
                <input
                  type="email"
                  disabled
                  value={user?.email || ''}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-500 text-sm cursor-not-allowed"
                />
                <span className="text-[11px] text-slate-400 mt-1 block">Registered email cannot be modified directly.</span>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Phone Number
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                    <Phone className="w-4 h-4" />
                  </div>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    placeholder="+91 9876543210"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  City
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                    <MapPin className="w-4 h-4" />
                  </div>
                  <input
                    type="text"
                    name="city"
                    value={formData.city}
                    onChange={handleChange}
                    placeholder="e.g. Bangalore"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  State
                </label>
                <input
                  type="text"
                  name="state"
                  value={formData.state}
                  onChange={handleChange}
                  placeholder="e.g. Karnataka"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Short Bio / Career Summary
                </label>
                <textarea
                  name="bio"
                  rows={3}
                  value={formData.bio}
                  onChange={handleChange}
                  placeholder="Aspiring software engineer passionate about fullstack development, distributed systems, and machine learning..."
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  LinkedIn URL
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                    <Linkedin className="w-4 h-4" />
                  </div>
                  <input
                    type="url"
                    name="linkedin_url"
                    value={formData.linkedin_url}
                    onChange={handleChange}
                    placeholder="https://linkedin.com/in/username"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  GitHub URL
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                    <Github className="w-4 h-4" />
                  </div>
                  <input
                    type="url"
                    name="github_url"
                    value={formData.github_url}
                    onChange={handleChange}
                    placeholder="https://github.com/username"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="sm:col-span-2">
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Portfolio / Personal Website URL
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                    <Globe className="w-4 h-4" />
                  </div>
                  <input
                    type="url"
                    name="website_url"
                    value={formData.website_url}
                    onChange={handleChange}
                    placeholder="https://myportfolio.dev"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: ACADEMIC AFFILIATION */}
        {activeTab === 'academic' && (
          <div className="space-y-6">
            <div className="border-b border-slate-100 pb-4">
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Building2 className="w-5 h-5 text-blue-600" />
                <span>Academic & Institutional Profile</span>
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                Link your college and department to access campus recruitment, batch skill diagnostics, and accredited coursework.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              {/* Institution Dropdown */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Partner Institution / University
                </label>
                <select
                  name="institution_id"
                  value={formData.institution_id}
                  onChange={handleInstitutionChange}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">-- Select Institution --</option>
                  {institutions.map((inst) => (
                    <option key={inst.id} value={inst.id}>
                      {inst.name} ({inst.code}) - {inst.city}
                    </option>
                  ))}
                </select>
                {institutions.length === 0 && (
                  <span className="text-[11px] text-amber-600 mt-1 block">
                    No partner institutions listed yet.
                  </span>
                )}
              </div>

              {/* Department Dropdown */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Academic Department
                </label>
                <select
                  name="department_id"
                  disabled={!formData.institution_id || loadingDepts}
                  value={formData.department_id}
                  onChange={handleChange}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-slate-50 disabled:text-slate-400"
                >
                  <option value="">
                    {loadingDepts ? 'Loading departments...' : '-- Select Department --'}
                  </option>
                  {departments.map((dept) => (
                    <option key={dept.id} value={dept.id}>
                      {dept.name} ({dept.code})
                    </option>
                  ))}
                </select>
                {!formData.institution_id && (
                  <span className="text-[11px] text-slate-400 mt-1 block">
                    Please select an institution first.
                  </span>
                )}
              </div>

              {/* Roll Number */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  College Roll / Registration Number
                </label>
                <input
                  type="text"
                  name="roll_number"
                  value={formData.roll_number}
                  onChange={handleChange}
                  placeholder="e.g. 2024CS1049"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Current Semester */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Current Semester (1 - 12)
                </label>
                <input
                  type="number"
                  name="current_semester"
                  min={1}
                  max={12}
                  value={formData.current_semester}
                  onChange={handleChange}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Enrollment Year */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Enrollment Year
                </label>
                <input
                  type="number"
                  name="enrollment_year"
                  min={2000}
                  max={2100}
                  value={formData.enrollment_year}
                  onChange={handleChange}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Graduation Year */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Expected Graduation Year
                </label>
                <input
                  type="number"
                  name="graduation_year"
                  min={2000}
                  max={2100}
                  value={formData.graduation_year}
                  onChange={handleChange}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* CGPA */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Current CGPA (0.00 - 10.00)
                </label>
                <input
                  type="number"
                  name="cgpa"
                  step="0.01"
                  min="0.00"
                  max="10.00"
                  value={formData.cgpa}
                  onChange={handleChange}
                  placeholder="e.g. 8.75"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: CAREER GOALS */}
        {activeTab === 'career' && (
          <div className="space-y-6">
            <div className="border-b border-slate-100 pb-4">
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Target className="w-5 h-5 text-blue-600" />
                <span>Target Career Benchmark</span>
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                Setting a target career role allows the SKILLY engine to identify your skill gaps and generate personalized roadmaps.
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Desired Target Career Role
                </label>
                <select
                  name="target_career_role_id"
                  value={formData.target_career_role_id}
                  onChange={handleChange}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">-- Select Target Career Role --</option>
                  {careerRoles.map((cr) => (
                    <option key={cr.id} value={cr.id}>
                      {cr.title} ({cr.industry_domain})
                    </option>
                  ))}
                </select>
              </div>

              {careerRoles.length === 0 && (
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-600">
                  <span>Standard career benchmark catalog will be populated with domain roles (Fullstack Developer, Data Scientist, DevOps Engineer, Cloud Architect, etc.).</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Form Action Controls */}
        <div className="pt-6 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="text-xs text-slate-500 flex items-center gap-2">
            <span>* Required fields</span>
            {isDirty && (
              <span className="text-amber-600 font-medium bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                Unsaved modifications
              </span>
            )}
          </div>
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <button
              type="button"
              onClick={handleCancel}
              disabled={!isDirty || saving}
              className="flex-1 sm:flex-initial px-4 py-2.5 rounded-xl border border-slate-300 text-slate-700 text-xs font-bold hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Cancel</span>
            </button>
            <Button
              type="submit"
              variant="primary"
              size="md"
              disabled={saving || !isDirty}
              className="flex-1 sm:flex-initial shadow-sm"
            >
              {saving ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  <span>Saving Profile...</span>
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  <span>Save Profile Changes</span>
                </>
              )}
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
}
