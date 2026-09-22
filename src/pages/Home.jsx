import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../lib/api';
import { 
  Award, 
  BookOpen, 
  Briefcase, 
  CheckCircle2, 
  ChevronRight, 
  Code2, 
  Compass, 
  Cpu, 
  FileCheck, 
  GraduationCap, 
  Layers, 
  LineChart, 
  Palette, 
  Rocket, 
  ShieldCheck, 
  Sparkles, 
  Target, 
  Users, 
  Building2, 
  ArrowRight,
  MapPin,
  Clock,
  DollarSign,
  Calendar,
  Search,
  Zap,
  Play,
  Database
} from 'lucide-react';
import Button from '../components/Button';
import studentHeroImg from '../assets/student_hero.jpg';
import industryHeroImg from '../assets/industry_hero.jpg';

export default function Home() {
  const [activePreviewTab, setActivePreviewTab] = useState('skills');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [skillsList, setSkillsList] = useState([]);
  const [opportunitiesList, setOpportunitiesList] = useState([]);
  const [isLoadingData, setIsLoadingData] = useState(true);

  useEffect(() => {
    let isMounted = true;
    const fetchMarketplaceData = async () => {
      try {
        const [skillsRes, oppsRes] = await Promise.all([
          api.get('/skills').catch(() => ({ data: [] })),
          api.get('/student/opportunities').catch(() => ({ data: [] }))
        ]);
        if (isMounted) {
          setSkillsList(Array.isArray(skillsRes.data) ? skillsRes.data : []);
          setOpportunitiesList(Array.isArray(oppsRes.data) ? oppsRes.data : []);
          setIsLoadingData(false);
        }
      } catch (err) {
        if (isMounted) setIsLoadingData(false);
      }
    };
    fetchMarketplaceData();
    return () => { isMounted = false; };
  }, []);

  const filteredSkills = skillsList.filter(skill => {
    const matchesCategory = selectedCategory === 'ALL' || (skill.category || '').toUpperCase() === selectedCategory;
    const matchesSearch = !searchQuery ||
      (skill.name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (skill.code || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (skill.category || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (skill.description || '').toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const internshipOpportunities = opportunitiesList.filter(o => 
    !o.role_type || o.role_type.toUpperCase().includes('INTERN')
  );

  const placementOpportunities = opportunitiesList.filter(o => 
    o.role_type && (o.role_type.toUpperCase().includes('FULL') || o.role_type.toUpperCase().includes('PLACEMENT') || o.role_type.toUpperCase().includes('JOB'))
  ).length > 0 ? opportunitiesList.filter(o => 
    o.role_type && (o.role_type.toUpperCase().includes('FULL') || o.role_type.toUpperCase().includes('PLACEMENT') || o.role_type.toUpperCase().includes('JOB'))
  ) : opportunitiesList;

  const journeySteps = [
    { num: '01', title: 'Student Onboarding', desc: 'Profile creation, role interest & goal definition' },
    { num: '02', title: 'Skill Assessment', desc: 'Evaluation of foundational & core competencies' },
    { num: '03', title: 'Skill Gap Analysis', desc: 'Identification of missing industry required skills' },
    { num: '04', title: 'Career Roadmap', desc: 'Tailored sequential milestone learning path' },
    { num: '05', title: 'Guided Learning', desc: 'Targeted coursework, coding labs & assignments' },
    { num: '06', title: 'Internship & Projects', desc: 'Real-world problem solving & verified evidence' },
    { num: '07', title: 'Mentorship', desc: 'Guidance from alumni and industry professionals' },
    { num: '08', title: 'Placement Match', desc: 'Direct corporate drive matching & interview prep' },
    { num: '09', title: 'Career Growth', desc: 'Lifelong continuous professional elevation' },
  ];

  const features = [
    {
      title: 'Skill Assessment',
      desc: 'Evaluate current capabilities and benchmark proficiency levels through structured diagnostic modules.',
      icon: Target,
      tag: 'Assessment',
    },
    {
      title: 'Skill Mapping',
      desc: 'Dynamically link individual skill competencies with verified industry job roles and marketplace standards.',
      icon: Compass,
      tag: 'Mapping',
    },
    {
      title: 'Career Roadmap',
      desc: 'Follow clear, milestone-driven roadmaps designed to guide students from basics to job readiness.',
      icon: Rocket,
      tag: 'Roadmap',
    },
    {
      title: 'Internship & Projects',
      desc: 'Discover vetted practical assignments and industry internship opportunities tailored to verified skills.',
      icon: Briefcase,
      tag: 'Experience',
    },
    {
      title: 'Skill Passport & Portfolio',
      desc: 'Maintain a tamper-proof digital record of verified projects, assessments, and verifiable evidence.',
      icon: FileCheck,
      tag: 'Evidence',
    },
    {
      title: 'Mentorship Network',
      desc: 'Engage with experienced alumni, teachers, and industry professionals for feedback and advice.',
      icon: Users,
      tag: 'Mentorship',
    },
    {
      title: 'Placement Support',
      desc: 'Connect colleges and students with recruiting companies through seamless recruitment coordination.',
      icon: Award,
      tag: 'Placement',
    },
    {
      title: 'AI Recommendations',
      desc: 'Receive automated, AI-assisted guidance for next skill steps, learning resources, and role matching.',
      icon: Sparkles,
      tag: 'Intelligence',
    },
  ];

  return (
    <div className="space-y-16 sm:space-y-24 pb-20 overflow-x-hidden">
      
      {/* 1. HERO PERSPECTIVE SHOWCASE SECTION */}
      <section className="relative pt-6 sm:pt-10 pb-12 bg-gradient-to-b from-blue-50/60 via-slate-50 to-white overflow-hidden">
        
        {/* Subtle background ambient glow */}
        <div className="absolute top-12 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-blue-200/30 rounded-full blur-3xl pointer-events-none"></div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          
          {/* PERSPECTIVE CAROUSEL CARD DECK CONTAINER */}
          <div className="flex items-center justify-center gap-6 xl:-mx-12 overflow-x-auto xl:overflow-visible pt-4 pb-8 scrollbar-none">
            
            {/* LEFT CARD: SKILLY FOR COLLEGES */}
            <div className="hidden 2xl:flex flex-col justify-between w-[340px] shrink-0 bg-white/90 backdrop-blur-md rounded-3xl border border-slate-200/80 p-6 shadow-xl opacity-80 transform -rotate-2 hover:rotate-0 hover:opacity-100 transition-all duration-300">
              <div className="space-y-4">
                <span className="text-[10px] font-bold tracking-widest text-slate-400 uppercase">
                  SKILLY FOR COLLEGES
                </span>
                <h3 className="text-xl font-extrabold text-slate-900 leading-tight">
                  One Dashboard. Every Department. Every Outcome.
                </h3>
                <p className="text-xs text-slate-500 leading-relaxed">
                  See placement readiness before NAAC asks — not after.
                </p>

                <div className="space-y-3 pt-2">
                  <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                    <p className="text-xs font-bold text-slate-800">NAAC/AICTE-Ready Reports</p>
                    <p className="text-[11px] text-slate-500">Exportable audit trail, one click</p>
                  </div>
                  <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                    <p className="text-xs font-bold text-slate-800">Department-Wise Insight</p>
                    <p className="text-[11px] text-slate-500">Every HOD sees their own numbers, live</p>
                  </div>
                </div>
              </div>

              <div className="pt-6">
                <Link to="/for-colleges" className="w-full inline-flex items-center justify-center py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-full shadow-sm">
                  See College Dashboard →
                </Link>
                <div className="flex items-center justify-between text-[10px] font-semibold text-slate-400 mt-3 px-1">
                  <span>38 Depts Onboarded</span>
                  <span>100% Audit Trail</span>
                </div>
              </div>
            </div>

            {/* CENTER MAIN HERO CARD */}
            <div className="w-full max-w-4xl shrink-0 bg-white rounded-3xl sm:rounded-[36px] border border-slate-200/90 shadow-2xl p-6 sm:p-9 relative z-20 transition-all">
              

              {/* Two Column Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
                
                {/* Left Content */}
                <div className="lg:col-span-7 space-y-5">
                  <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-50 border border-blue-200/80 text-blue-600 text-xs font-bold">
                    <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                    <span>Your Skills. Your Evidence. Your Career.</span>
                  </div>

                  <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 tracking-tight leading-[1.15]">
                    Turn Every Skill Into <span className="text-blue-600">Proof</span>.<br className="hidden sm:inline" />
                    Every Internship Into <span className="text-blue-600">Evidence</span>.
                  </h1>

                  <p className="text-sm sm:text-base text-slate-600 leading-relaxed">
                    See your exact skill gap for the role you want, follow a personalized roadmap, and walk into placement season with a verified Skill Passport — not just a resume.
                  </p>

                  <div className="pt-2 flex flex-col sm:flex-row items-center gap-3">
                    <Link 
                      to="/register" 
                      className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm px-6 py-3 rounded-full shadow-md shadow-blue-500/20 transition-all"
                    >
                      <span>Build My Skill Profile</span>
                      <ArrowRight className="w-4 h-4" />
                    </Link>
                    <Link 
                      to="/how-it-works" 
                      className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-white hover:bg-slate-50 border border-slate-200 text-slate-800 font-semibold text-sm px-6 py-3 rounded-full shadow-2xs transition-all"
                    >
                      <span>See How It Works</span>
                      <Play className="w-3.5 h-3.5 fill-slate-800 text-slate-800 ml-0.5" />
                    </Link>
                  </div>
                </div>

                {/* Right Image Container */}
                <div className="lg:col-span-5 relative">
                  <div className="relative rounded-2xl overflow-hidden shadow-lg border border-slate-200/80 group">
                    <img 
                      src={studentHeroImg} 
                      alt="Student working on laptop" 
                      className="w-full h-64 sm:h-72 object-cover transform group-hover:scale-105 transition-transform duration-500"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-slate-900/40 via-transparent to-transparent"></div>
                    <div className="absolute bottom-3 left-3 right-3 bg-white/90 backdrop-blur-md p-3 rounded-xl border border-white/40 flex items-center justify-between text-xs">
                      <div>
                        <p className="font-bold text-slate-900">Verified Skill Passport</p>
                        <p className="text-[10px] text-slate-500">Live Project Evidence Attached</p>
                      </div>
                      <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
                    </div>
                  </div>
                </div>

              </div>

              {/* POPULAR SKILL TRACKS SECTION INSIDE MAIN CARD */}
              <div className="mt-8 pt-6 border-t border-slate-100">
                <div className="text-[11px] font-bold tracking-widest text-slate-400 uppercase mb-3.5">
                  POPULAR SKILL TRACKS
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <Link to="/skills" className="p-3 bg-slate-50 hover:bg-blue-50/60 rounded-2xl border border-slate-200/70 hover:border-blue-200 transition-all group">
                    <div className="flex items-center gap-2 mb-1">
                      <div className="w-7 h-7 rounded-lg bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-xs">
                        <Code2 className="w-3.5 h-3.5" />
                      </div>
                      <p className="text-xs font-bold text-slate-900 group-hover:text-blue-600 transition-colors">Web Dev</p>
                    </div>
                    <p className="text-[10px] text-slate-400 font-medium">1200+ active</p>
                  </Link>

                  <Link to="/skills" className="p-3 bg-slate-50 hover:bg-indigo-50/60 rounded-2xl border border-slate-200/70 hover:border-indigo-200 transition-all group">
                    <div className="flex items-center gap-2 mb-1">
                      <div className="w-7 h-7 rounded-lg bg-indigo-100 text-indigo-600 flex items-center justify-center font-bold text-xs">
                        <Database className="w-3.5 h-3.5" />
                      </div>
                      <p className="text-xs font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">Data Science</p>
                    </div>
                    <p className="text-[10px] text-slate-400 font-medium">850+ active</p>
                  </Link>

                  <Link to="/skills" className="p-3 bg-slate-50 hover:bg-emerald-50/60 rounded-2xl border border-slate-200/70 hover:border-emerald-200 transition-all group">
                    <div className="flex items-center gap-2 mb-1">
                      <div className="w-7 h-7 rounded-lg bg-emerald-100 text-emerald-600 flex items-center justify-center font-bold text-xs">
                        <Cpu className="w-3.5 h-3.5" />
                      </div>
                      <p className="text-xs font-bold text-slate-900 group-hover:text-emerald-600 transition-colors">Core Eng.</p>
                    </div>
                    <p className="text-[10px] text-slate-400 font-medium">950+ active</p>
                  </Link>

                  <Link to="/skills" className="p-3 bg-slate-50 hover:bg-purple-50/60 rounded-2xl border border-slate-200/70 hover:border-purple-200 transition-all group">
                    <div className="flex items-center gap-2 mb-1">
                      <div className="w-7 h-7 rounded-lg bg-purple-100 text-purple-600 flex items-center justify-center font-bold text-xs">
                        <Palette className="w-3.5 h-3.5" />
                      </div>
                      <p className="text-xs font-bold text-slate-900 group-hover:text-purple-600 transition-colors">UI/UX Design</p>
                    </div>
                    <p className="text-[10px] text-slate-400 font-medium">600+ active</p>
                  </Link>
                </div>
              </div>

            </div>

            {/* RIGHT CARD: SKILLY FOR INDUSTRY */}
            <div className="hidden 2xl:flex flex-col justify-between w-[340px] shrink-0 bg-slate-900 text-white rounded-3xl border border-slate-800 p-6 shadow-xl opacity-90 transform rotate-2 hover:rotate-0 hover:opacity-100 transition-all duration-300 relative overflow-hidden">
              <div>
                <div className="relative rounded-2xl overflow-hidden mb-4 border border-slate-800">
                  <img src={industryHeroImg} alt="Industry recruiters" className="w-full h-36 object-cover opacity-80" />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent"></div>
                  <span className="absolute bottom-2 left-2 text-[10px] font-bold px-2 py-0.5 rounded bg-blue-600 text-white">
                    2K+ Hiring Partners
                  </span>
                </div>

                <h3 className="text-lg font-extrabold text-white mb-1.5 leading-tight">
                  Hire On Evidence. Not Adjectives.
                </h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-4">
                  Every candidate's skills are backed by verified internship evaluations — not self-reported claims.
                </p>
              </div>

              <div>
                <Link to="/for-industry" className="w-full inline-flex items-center justify-center py-2.5 px-4 bg-white text-slate-900 hover:bg-slate-100 font-bold text-xs rounded-full shadow-sm">
                  Post an Opportunity →
                </Link>
              </div>
            </div>

          </div>

        </div>
      </section>

      {/* LIVE ECOSYSTEM COUNTER METRICS */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6">
          <div className="bg-white rounded-2xl border border-slate-200/80 p-5 sm:p-6 text-center card-hover shadow-2xs">
            <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto mb-3">
              <Target className="w-5 h-5" />
            </div>
            <p className="text-2xl sm:text-3xl font-black text-slate-900">12,400+</p>
            <p className="text-xs text-slate-500 font-medium mt-1">Verified Skill Assessments</p>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200/80 p-5 sm:p-6 text-center card-hover shadow-2xs">
            <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto mb-3">
              <Building2 className="w-5 h-5" />
            </div>
            <p className="text-2xl sm:text-3xl font-black text-slate-900">150+</p>
            <p className="text-xs text-slate-500 font-medium mt-1">Partner Colleges & TPOs</p>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200/80 p-5 sm:p-6 text-center card-hover shadow-2xs">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto mb-3">
              <Briefcase className="w-5 h-5" />
            </div>
            <p className="text-2xl sm:text-3xl font-black text-slate-900">320+</p>
            <p className="text-xs text-slate-500 font-medium mt-1">Active Industry Hiring Drives</p>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200/80 p-5 sm:p-6 text-center card-hover shadow-2xs">
            <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center mx-auto mb-3">
              <Award className="w-5 h-5" />
            </div>
            <p className="text-2xl sm:text-3xl font-black text-slate-900">94.8%</p>
            <p className="text-xs text-slate-500 font-medium mt-1">Placement Match Rate</p>
          </div>
        </div>
      </section>

      {/* 2. DYNAMIC LIVE PREVIEWS SECTION (Top Skills, Internships & Placement Drives) */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-3xl border border-slate-200/90 shadow-soft-lg p-6 sm:p-10 space-y-8">
          
          {/* Section Header */}
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-slate-100">
            <div>
              <span className="badge-blue mb-2">Live Marketplace Catalog</span>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                Explore Skills, Internships & Placement Drives
              </h2>
              <p className="text-sm sm:text-base text-slate-600 mt-1">
                Real-time previews of verified competency tracks, corporate internships, and campus placement drives.
              </p>
            </div>

            {/* Tab Switcher Controls */}
            <div className="flex items-center gap-1.5 p-1 bg-slate-100 rounded-xl shrink-0 self-start md:self-auto">
              <button
                onClick={() => setActivePreviewTab('skills')}
                className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                  activePreviewTab === 'skills'
                    ? 'bg-white text-blue-600 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Top Skills
              </button>
              <button
                onClick={() => setActivePreviewTab('internships')}
                className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                  activePreviewTab === 'internships'
                    ? 'bg-white text-blue-600 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Active Internships
              </button>
              <button
                onClick={() => setActivePreviewTab('placements')}
                className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                  activePreviewTab === 'placements'
                    ? 'bg-white text-blue-600 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Placement Drives
              </button>
            </div>
          </div>

          {/* TAB 1: TOP SKILLS PREVIEW */}
          {activePreviewTab === 'skills' && (
            <div className="space-y-6">
              
              {/* Category Pills & Search Bar */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
                  {['ALL', 'WEB', 'AI', 'CLOUD', 'CORE', 'DESIGN', 'SECURITY'].map((cat) => (
                    <button
                      key={cat}
                      onClick={() => setSelectedCategory(cat)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors shrink-0 ${
                        selectedCategory === cat
                          ? 'bg-blue-600 text-white shadow-xs'
                          : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                      }`}
                    >
                      {cat}
                    </button>
                  ))}
                </div>

                <div className="relative">
                  <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    placeholder="Search skills or tags..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9 pr-4 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 outline-none focus:border-blue-500 w-full sm:w-64"
                  />
                </div>
              </div>

              {/* Skill Cards Grid */}
              {isLoadingData ? (
                <div className="py-12 text-center text-xs font-semibold text-slate-400">Loading live skills catalog from database...</div>
              ) : filteredSkills.length === 0 ? (
                <div className="py-12 text-center text-xs font-semibold text-slate-500">No matching skills found in catalog.</div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {filteredSkills.slice(0, 9).map((skill) => (
                    <div key={skill.id} className="bg-slate-50/70 rounded-2xl border border-slate-200/80 p-5 flex flex-col justify-between hover:border-blue-300 hover:bg-white transition-all shadow-xs group">
                      <div>
                        <div className="flex items-center justify-between mb-3">
                          <div className="w-10 h-10 rounded-xl flex items-center justify-center border bg-blue-50 text-blue-600 border-blue-200 font-bold text-xs">
                            <Code2 className="w-5 h-5" />
                          </div>
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200">
                            {skill.code || 'MASTER'}
                          </span>
                        </div>
                        <h3 className="text-base font-bold text-slate-900 mb-1 group-hover:text-blue-600 transition-colors">
                          {skill.name}
                        </h3>
                        <p className="text-xs text-slate-500 line-clamp-2 mb-3">
                          {skill.description || 'Master competency skill module.'}
                        </p>
                      </div>

                      <div>
                        <div className="flex flex-wrap gap-1.5 mb-4">
                          <span className="text-[10px] font-medium bg-white text-slate-600 border border-slate-200 px-2 py-0.5 rounded">
                            Category: {skill.category || 'GENERAL'}
                          </span>
                        </div>
                        <Link to="/register" className="inline-flex items-center text-xs font-bold text-blue-600 hover:text-blue-700">
                          <span>Start Assessment</span>
                          <ArrowRight className="w-3.5 h-3.5 ml-1" />
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="pt-2 text-center">
                <Link to="/skills" className="inline-flex items-center text-sm font-bold text-blue-600 hover:underline">
                  <span>View all {skillsList.length} verified skill modules</span>
                  <ChevronRight className="w-4 h-4 ml-0.5" />
                </Link>
              </div>
            </div>
          )}

          {/* TAB 2: ACTIVE INTERNSHIPS PREVIEW */}
          {activePreviewTab === 'internships' && (
            <div className="space-y-6">
              {isLoadingData ? (
                <div className="py-12 text-center text-xs font-semibold text-slate-400">Loading active opportunities from database...</div>
              ) : internshipOpportunities.length === 0 ? (
                <div className="py-12 text-center text-xs font-semibold text-slate-500">No active internship opportunities currently listed.</div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {internshipOpportunities.slice(0, 6).map((item) => (
                    <div key={item.id} className="bg-slate-50/70 rounded-2xl border border-slate-200/80 p-6 flex flex-col justify-between hover:border-blue-300 hover:bg-white transition-all shadow-xs">
                      <div>
                        <div className="flex items-start justify-between gap-3 mb-3">
                          <div className="flex items-center gap-2.5">
                            <div className="w-10 h-10 rounded-xl bg-blue-100 text-slate-800 flex items-center justify-center font-bold text-sm shrink-0">
                              {item.company_name ? item.company_name[0].toUpperCase() : 'C'}
                            </div>
                            <div>
                              <h3 className="text-base font-bold text-slate-900">{item.title}</h3>
                              <p className="text-xs text-slate-600 font-medium">{item.company_name || 'Verified Company'}</p>
                            </div>
                          </div>
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                            {item.role_type || 'INTERNSHIP'}
                          </span>
                        </div>

                        <div className="grid grid-cols-2 gap-2 text-xs text-slate-600 my-4 bg-white p-3 rounded-xl border border-slate-200/60">
                          <div className="flex items-center gap-1.5">
                            <MapPin className="w-3.5 h-3.5 text-slate-400" />
                            <span>{item.is_remote ? 'Remote' : (item.location || 'Not Specified')}</span>
                          </div>
                          <div className="flex items-center gap-1.5">
                            <Clock className="w-3.5 h-3.5 text-slate-400" />
                            <span>{item.duration_months ? `${item.duration_months} Months` : 'N/A'}</span>
                          </div>
                          <div className="flex items-center gap-1.5">
                            <DollarSign className="w-3.5 h-3.5 text-emerald-600" />
                            <span className="font-bold text-slate-800">{item.stipend_salary ? `₹${item.stipend_salary}` : 'Disclosed on selection'}</span>
                          </div>
                          <div className="flex items-center gap-1.5">
                            <Zap className="w-3.5 h-3.5 text-amber-500" />
                            <span>{item.status || 'Active'}</span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center justify-between pt-2 border-t border-slate-200/60">
                        <div className="flex items-center gap-1 overflow-x-auto">
                          {(item.required_skills || []).slice(0, 3).map((s, i) => (
                            <span key={i} className="text-[10px] bg-slate-200/70 text-slate-700 font-medium px-2 py-0.5 rounded whitespace-nowrap">
                              {s.skill_name}
                            </span>
                          ))}
                        </div>
                        <Link to="/register" className="inline-flex items-center text-xs font-bold text-blue-600 hover:text-blue-700 shrink-0">
                          <span>Apply Now</span>
                          <ChevronRight className="w-3.5 h-3.5" />
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="pt-2 text-center">
                <Link to="/internships" className="inline-flex items-center text-sm font-bold text-blue-600 hover:underline">
                  <span>Browse all active industry internship listings</span>
                  <ChevronRight className="w-4 h-4 ml-0.5" />
                </Link>
              </div>
            </div>
          )}

          {/* TAB 3: PLACEMENT DRIVES PREVIEW */}
          {activePreviewTab === 'placements' && (
            <div className="space-y-6">
              {isLoadingData ? (
                <div className="py-12 text-center text-xs font-semibold text-slate-400">Loading placement drives from database...</div>
              ) : placementOpportunities.length === 0 ? (
                <div className="py-12 text-center text-xs font-semibold text-slate-500">No active placement drives currently listed.</div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {placementOpportunities.slice(0, 6).map((drive) => (
                    <div key={drive.id} className="bg-slate-50/70 rounded-2xl border border-slate-200/80 p-6 flex flex-col justify-between hover:border-blue-300 hover:bg-white transition-all shadow-xs">
                      <div>
                        <div className="flex items-center justify-between mb-3">
                          <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full border bg-emerald-50 text-emerald-700 border-emerald-200">
                            {drive.status || 'OPEN'}
                          </span>
                          <span className="text-[11px] text-slate-500 flex items-center gap-1">
                            <Calendar className="w-3.5 h-3.5" />
                            {drive.application_deadline ? new Date(drive.application_deadline).toLocaleDateString() : 'Open Drive'}
                          </span>
                        </div>

                        <h3 className="text-base font-bold text-slate-900 mb-0.5">{drive.title}</h3>
                        <p className="text-xs text-blue-600 font-bold mb-3">{drive.company_name || 'Partner Company'}</p>

                        <div className="space-y-2 bg-white p-3.5 rounded-xl border border-slate-200/70 text-xs mb-4">
                          <div>
                            <span className="text-slate-400 font-medium">Package / Stipend:</span>
                            <p className="font-extrabold text-slate-900 text-sm">{drive.stipend_salary ? `₹${drive.stipend_salary}` : 'As per Industry Standards'}</p>
                          </div>
                          <div>
                            <span className="text-slate-400 font-medium">Location:</span>
                            <p className="text-slate-700 text-xs font-semibold">{drive.is_remote ? 'Remote' : (drive.location || 'Onsite')}</p>
                          </div>
                        </div>
                      </div>

                      <Button to="/register" variant="primary" size="sm" className="w-full justify-center">
                        Register for Drive
                      </Button>
                    </div>
                  ))}
                </div>
              )}

              <div className="pt-2 text-center">
                <Link to="/placements" className="inline-flex items-center text-sm font-bold text-blue-600 hover:underline">
                  <span>View full campus placement calendar</span>
                  <ChevronRight className="w-4 h-4 ml-0.5" />
                </Link>
              </div>
            </div>
          )}

        </div>
      </section>

      {/* 3. HOW SKILLY WORKS SECTION */}
      <section className="bg-slate-100/70 py-20 border-y border-slate-200/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto space-y-3 mb-16">
            <span className="badge-blue">End-to-End Progression</span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
              How SKILLY Works
            </h2>
            <p className="text-base sm:text-lg text-slate-600">
              A continuous, step-by-step career acceleration model connecting learning to tangible professional outcomes.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {journeySteps.map((step, idx) => (
              <div 
                key={idx} 
                className="bg-white rounded-2xl border border-slate-200/80 p-6 card-hover relative overflow-hidden"
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-2xl font-black text-blue-600/80">
                    {step.num}
                  </span>
                  <div className="w-2 h-2 rounded-full bg-blue-600"></div>
                </div>
                <h3 className="text-lg font-bold text-slate-900 mb-1.5">
                  {step.title}
                </h3>
                <p className="text-sm text-slate-600">
                  {step.desc}
                </p>
              </div>
            ))}
          </div>

          <div className="mt-12 text-center">
            <Button to="/how-it-works" variant="primary" size="md">
              <span>Read the Full Process Guide</span>
              <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
        </div>
      </section>

      {/* 4. PLATFORM FEATURES SECTION */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto space-y-3 mb-16">
          <span className="badge-blue">Comprehensive Toolkit</span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
            Designed for Practical Excellence
          </h2>
          <p className="text-base sm:text-lg text-slate-600">
            Every feature on SKILLY serves a distinct purpose in elevating student readiness and institutional collaboration.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, idx) => {
            const Icon = feature.icon;
            return (
              <div 
                key={idx} 
                className="bg-white rounded-2xl border border-slate-200/80 p-6 card-hover flex flex-col justify-between"
              >
                <div>
                  <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mb-4 border border-blue-100">
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="text-[11px] font-bold uppercase tracking-wider text-blue-600 mb-1">
                    {feature.tag}
                  </div>
                  <h3 className="text-base font-bold text-slate-900 mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    {feature.desc}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-10 text-center">
          <Link to="/features" className="text-sm font-bold text-blue-600 hover:text-blue-700 inline-flex items-center gap-1">
            <span>Explore all feature specifications</span>
            <ChevronRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      {/* 5. FINAL CTA SECTION */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-gradient-to-r from-blue-700 via-blue-600 to-indigo-700 rounded-3xl p-8 sm:p-14 text-white text-center shadow-soft-lg relative overflow-hidden">
          
          <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 rounded-full bg-white/10 blur-xl pointer-events-none"></div>
          <div className="absolute bottom-0 left-0 -ml-16 -mb-16 w-64 h-64 rounded-full bg-indigo-900/30 blur-xl pointer-events-none"></div>

          <div className="relative max-w-3xl mx-auto space-y-6">
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight text-white">
              Build Skills. Gain Experience. Grow Your Career.
            </h2>
            <p className="text-base sm:text-lg text-blue-100 leading-relaxed max-w-2xl mx-auto">
              Start your SKILLY journey today. Connect with top mentors, streamline campus placements, and unlock high-impact opportunities.
            </p>
            <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button to="/register" size="lg" variant="white" className="w-full sm:w-auto font-bold">
                Get Started
              </Button>
              <Button to="/login" size="lg" variant="dark" className="w-full sm:w-auto bg-slate-900/80 hover:bg-slate-900">
                Log In
              </Button>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
}


