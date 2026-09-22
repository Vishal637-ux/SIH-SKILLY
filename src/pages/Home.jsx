import React, { useState } from 'react';
import { Link } from 'react-router-dom';
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
  Network, 
  Palette, 
  Rocket, 
  ShieldCheck, 
  Sparkles, 
  Target, 
  Users, 
  Building2, 
  ArrowRight,
  TrendingUp,
  MapPin,
  Clock,
  DollarSign,
  Calendar,
  CheckCircle,
  Search,
  Zap,
  Star,
  ExternalLink
} from 'lucide-react';
import Button from '../components/Button';

export default function Home() {
  const [activePreviewTab, setActivePreviewTab] = useState('skills'); // 'skills' | 'internships' | 'placements'
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  // Sample live data previews
  const topSkillsData = [
    {
      id: 1,
      title: 'Full-Stack React & Node Architecture',
      category: 'WEB',
      level: 'Advanced',
      learners: '3.4k enrolled',
      demand: 'High Demand',
      tags: ['React 18', 'Node.js', 'PostgreSQL', 'REST API'],
      icon: Code2,
      bg: 'bg-blue-50 text-blue-600 border-blue-200',
    },
    {
      id: 2,
      title: 'Machine Learning & Predictive Analytics',
      category: 'AI',
      level: 'Intermediate',
      learners: '2.8k enrolled',
      demand: 'Trending',
      tags: ['Python', 'Scikit-Learn', 'Pandas', 'BigQuery'],
      icon: LineChart,
      bg: 'bg-indigo-50 text-indigo-600 border-indigo-200',
    },
    {
      id: 3,
      title: 'Cloud DevOps & Container Orchestration',
      category: 'CLOUD',
      level: 'Advanced',
      learners: '1.9k enrolled',
      demand: 'High Demand',
      tags: ['Docker', 'Kubernetes', 'CI/CD', 'AWS'],
      icon: Layers,
      bg: 'bg-sky-50 text-sky-600 border-sky-200',
    },
    {
      id: 4,
      title: 'IoT & Embedded Systems Programming',
      category: 'CORE',
      level: 'Intermediate',
      learners: '1.5k enrolled',
      demand: 'Industry Standard',
      tags: ['Embedded C', 'ESP32', 'Robotics', 'MQTT'],
      icon: Cpu,
      bg: 'bg-emerald-50 text-emerald-600 border-emerald-200',
    },
    {
      id: 5,
      title: 'UI/UX Design Systems & Prototyping',
      category: 'DESIGN',
      level: 'Beginner - Inter',
      learners: '2.2k enrolled',
      demand: 'High Demand',
      tags: ['Figma', 'User Research', 'Design Tokens', 'Wireframes'],
      icon: Palette,
      bg: 'bg-purple-50 text-purple-600 border-purple-200',
    },
    {
      id: 6,
      title: 'Cybersecurity Audit & Threat Analysis',
      category: 'SECURITY',
      level: 'Advanced',
      learners: '1.2k enrolled',
      demand: 'Critical Demand',
      tags: ['Network Audit', 'OWASP', 'Cryptography', 'Linux'],
      icon: ShieldCheck,
      bg: 'bg-rose-50 text-rose-600 border-rose-200',
    },
  ];

  const activeInternshipsData = [
    {
      id: 1,
      title: 'Frontend Engineering Intern',
      company: 'Apex Tech Solutions',
      location: 'Remote / Bangalore',
      duration: '3 Months',
      stipend: '₹25,000 / month',
      type: 'Paid Internship',
      skills: ['React', 'TypeScript', 'TailwindCSS'],
      posted: '2 days ago',
      verifiedLogo: '⚡',
    },
    {
      id: 2,
      title: 'AI Data Analyst Apprentice',
      company: 'Cognitive Dynamics Lab',
      location: 'Hybrid / Hyderabad',
      duration: '6 Months',
      stipend: '₹30,000 / month',
      type: 'PPO Opportunity',
      skills: ['Python', 'SQL', 'Data Analytics'],
      posted: '1 day ago',
      verifiedLogo: '🧠',
    },
    {
      id: 3,
      title: 'Cloud Systems & DevOps Intern',
      company: 'ScaleGrid Infrastructure',
      location: 'Remote / Pune',
      duration: '4 Months',
      stipend: '₹22,000 / month',
      type: 'Paid Internship',
      skills: ['Docker', 'Linux', 'AWS Cloud'],
      posted: '3 days ago',
      verifiedLogo: '☁️',
    },
    {
      id: 4,
      title: 'Embedded Firmware Developer Trainee',
      company: 'RoboCore Automations',
      location: 'Onsite / Chennai',
      duration: '6 Months',
      stipend: '₹20,000 / month',
      type: 'Project Based',
      skills: ['C++', 'Microcontrollers', 'IoT Protocols'],
      posted: 'Just now',
      verifiedLogo: '🤖',
    }
  ];

  const placementDrivesData = [
    {
      id: 1,
      company: 'Global Cloud Systems Inc.',
      role: 'Associate Software Engineer',
      ctc: '₹8.5 LPA - ₹12 LPA',
      eligibility: 'B.Tech CSE/IT/ECE (Batch 2025/2026)',
      date: 'Oct 15, 2026',
      rounds: 'Aptitude -> Coding -> Technical -> HR',
      status: 'Registration Open',
      badgeColor: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    },
    {
      id: 2,
      company: 'FinTech Innovations Ltd.',
      role: 'Data Engineer & Analyst',
      ctc: '₹9.0 LPA - ₹14 LPA',
      eligibility: 'All Engineering & MCA Streams',
      date: 'Oct 22, 2026',
      rounds: 'SQL Assessment -> System Design -> HR',
      status: 'Registration Open',
      badgeColor: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    },
    {
      id: 3,
      company: 'NextGen Cybersec Ops',
      role: 'Security Analyst Trainee',
      ctc: '₹7.5 LPA - ₹10 LPA',
      eligibility: 'B.Tech/B.Sc IT (Min 7.0 CGPA)',
      date: 'Nov 02, 2026',
      rounds: 'Security Audit Challenge -> Technical Interview',
      status: 'Upcoming Drive',
      badgeColor: 'bg-blue-50 text-blue-700 border-blue-200',
    }
  ];

  const filteredSkills = topSkillsData.filter(skill => {
    const matchesCategory = selectedCategory === 'ALL' || skill.category === selectedCategory;
    const matchesSearch = skill.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          skill.tags.some(t => t.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesCategory && matchesSearch;
  });

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
    <div className="space-y-20 sm:space-y-28 pb-20">
      
      {/* 1. HERO SECTION */}
      <section className="relative pt-12 sm:pt-20 pb-16 hero-gradient overflow-hidden border-b border-slate-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
            
            {/* Hero Left Content */}
            <div className="lg:col-span-7 space-y-6 text-center lg:text-left">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-50 border border-blue-200/80 text-blue-700 text-xs font-semibold shadow-2xs">
                <Sparkles className="w-3.5 h-3.5 text-blue-600 animate-pulse" />
                <span>Academia–Industry Collaboration Platform</span>
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-slate-900 tracking-tight leading-[1.15]">
                Turn Every Skill Into <span className="text-blue-600">Proof</span>.<br className="hidden sm:inline" />
                Every Internship Into <span className="text-blue-600">Experience</span>.
              </h1>

              <p className="text-lg sm:text-xl text-slate-600 leading-relaxed max-w-2xl mx-auto lg:mx-0">
                SKILLY connects skills, learning, internships, industry exposure, and placement into one continuous career journey for students, colleges, and hiring partners.
              </p>

              <div className="pt-2 flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4">
                <Button to="/register" size="lg" variant="primary" className="w-full sm:w-auto shadow-md font-semibold">
                  <span>Build My Skill Profile</span>
                  <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
                <Button to="/how-it-works" size="lg" variant="outline" className="w-full sm:w-auto">
                  See How It Works
                </Button>
              </div>

              {/* Stakeholder Highlights */}
              <div className="pt-6 border-t border-slate-200/80 grid grid-cols-3 gap-4 text-left">
                <div>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">For Students</p>
                  <p className="text-sm font-bold text-slate-800 mt-0.5">Verified Evidence</p>
                </div>
                <div>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">For Colleges</p>
                  <p className="text-sm font-bold text-slate-800 mt-0.5">Skill Transparency</p>
                </div>
                <div>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">For Industry</p>
                  <p className="text-sm font-bold text-slate-800 mt-0.5">Direct Matching</p>
                </div>
              </div>
            </div>

            {/* Hero Right Ecosystem Visual Card Composition */}
            <div className="lg:col-span-5">
              <div className="relative mx-auto max-w-md lg:max-w-none">
                
                {/* Background glow decoration */}
                <div className="absolute -inset-2 bg-gradient-to-tr from-blue-100 to-indigo-100 rounded-3xl blur-lg opacity-70"></div>
                
                {/* Main Card Container */}
                <div className="relative bg-white rounded-2xl border border-slate-200/80 shadow-soft-lg p-6 sm:p-7 space-y-5">
                  <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-blue-600 animate-ping"></div>
                      <span className="text-xs font-bold uppercase tracking-wider text-slate-700">SKILLY Ecosystem</span>
                    </div>
                    <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-0.5 rounded-md border border-blue-100">
                      Unified Lifecycle
                    </span>
                  </div>

                  {/* Flow items */}
                  <div className="space-y-3">
                    
                    {/* Node 1: Skills & Assessment */}
                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/60 flex items-center justify-between hover:bg-blue-50/50 hover:border-blue-200 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-xs">
                          <Target className="w-4 h-4" />
                        </div>
                        <div>
                          <p className="text-xs font-bold text-slate-900">Skills & Assessment</p>
                          <p className="text-[11px] text-slate-500">Benchmark capability & gap map</p>
                        </div>
                      </div>
                      <span className="text-[10px] font-semibold bg-white border border-slate-200 px-2 py-0.5 rounded text-slate-600">Evidence</span>
                    </div>

                    {/* Down arrow indicator */}
                    <div className="flex justify-center -my-1 text-slate-300">
                      <div className="w-0.5 h-3 bg-slate-200"></div>
                    </div>

                    {/* Node 2: College & Training */}
                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/60 flex items-center justify-between hover:bg-blue-50/50 hover:border-blue-200 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-xs">
                          <GraduationCap className="w-4 h-4" />
                        </div>
                        <div>
                          <p className="text-xs font-bold text-slate-900">College & Learning</p>
                          <p className="text-[11px] text-slate-500">Structured roadmaps & trainer sync</p>
                        </div>
                      </div>
                      <span className="text-[10px] font-semibold bg-white border border-slate-200 px-2 py-0.5 rounded text-slate-600">Roadmap</span>
                    </div>

                    {/* Down arrow indicator */}
                    <div className="flex justify-center -my-1 text-slate-300">
                      <div className="w-0.5 h-3 bg-slate-200"></div>
                    </div>

                    {/* Node 3: Internship & Industry */}
                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/60 flex items-center justify-between hover:bg-blue-50/50 hover:border-blue-200 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-xs">
                          <Briefcase className="w-4 h-4" />
                        </div>
                        <div>
                          <p className="text-xs font-bold text-slate-900">Internships & Industry</p>
                          <p className="text-[11px] text-slate-500">Verified project work & mentorship</p>
                        </div>
                      </div>
                      <span className="text-[10px] font-semibold bg-white border border-slate-200 px-2 py-0.5 rounded text-slate-600">Experience</span>
                    </div>

                    {/* Down arrow indicator */}
                    <div className="flex justify-center -my-1 text-slate-300">
                      <div className="w-0.5 h-3 bg-slate-200"></div>
                    </div>

                    {/* Node 4: Placement & Career */}
                    <div className="p-3 rounded-xl bg-blue-600 text-white flex items-center justify-between shadow-sm">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-white/20 text-white flex items-center justify-center font-bold text-xs">
                          <Award className="w-4 h-4" />
                        </div>
                        <div>
                          <p className="text-xs font-bold text-white">Placement & Career Growth</p>
                          <p className="text-[11px] text-blue-100">Proof-based hiring & advancement</p>
                        </div>
                      </div>
                      <span className="text-[10px] font-semibold bg-white/20 px-2 py-0.5 rounded text-white">Placement</span>
                    </div>

                  </div>

                  {/* Summary Footer */}
                  <div className="pt-2 text-center">
                    <p className="text-xs text-slate-500 font-medium">
                      Skills → Evidence → Experience → Opportunities → Career
                    </p>
                  </div>

                </div>

              </div>
            </div>

          </div>
        </div>
      </section>

      {/* LIVE ECOSYSTEM COUNTER METRICS */}
      <section className="section-container">
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
      <section className="section-container">
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
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredSkills.map((skill) => {
                  const Icon = skill.icon;
                  return (
                    <div key={skill.id} className="bg-slate-50/70 rounded-2xl border border-slate-200/80 p-5 flex flex-col justify-between hover:border-blue-300 hover:bg-white transition-all shadow-xs group">
                      <div>
                        <div className="flex items-center justify-between mb-3">
                          <div className={`w-10 h-10 rounded-xl flex items-center justify-center border ${skill.bg}`}>
                            <Icon className="w-5 h-5" />
                          </div>
                          <span className="text-[11px] font-bold px-2 py-0.5 rounded-md bg-amber-50 text-amber-700 border border-amber-200">
                            {skill.demand}
                          </span>
                        </div>
                        <h3 className="text-base font-bold text-slate-900 mb-1 group-hover:text-blue-600 transition-colors">
                          {skill.title}
                        </h3>
                        <div className="flex items-center gap-3 text-xs text-slate-500 mb-4">
                          <span>Level: <strong className="text-slate-700 font-semibold">{skill.level}</strong></span>
                          <span>•</span>
                          <span>{skill.learners}</span>
                        </div>
                      </div>

                      <div>
                        <div className="flex flex-wrap gap-1.5 mb-4">
                          {skill.tags.map((t, i) => (
                            <span key={i} className="text-[10px] font-medium bg-white text-slate-600 border border-slate-200 px-2 py-0.5 rounded">
                              {t}
                            </span>
                          ))}
                        </div>
                        <Link to="/register" className="inline-flex items-center text-xs font-bold text-blue-600 hover:text-blue-700">
                          <span>Start Assessment</span>
                          <ArrowRight className="w-3.5 h-3.5 ml-1" />
                        </Link>
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="pt-2 text-center">
                <Link to="/skills" className="inline-flex items-center text-sm font-bold text-blue-600 hover:underline">
                  <span>View all 120+ verified skill modules</span>
                  <ChevronRight className="w-4 h-4 ml-0.5" />
                </Link>
              </div>
            </div>
          )}

          {/* TAB 2: ACTIVE INTERNSHIPS PREVIEW */}
          {activePreviewTab === 'internships' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {activeInternshipsData.map((item) => (
                  <div key={item.id} className="bg-slate-50/70 rounded-2xl border border-slate-200/80 p-6 flex flex-col justify-between hover:border-blue-300 hover:bg-white transition-all shadow-xs">
                    <div>
                      <div className="flex items-start justify-between gap-3 mb-3">
                        <div className="flex items-center gap-2.5">
                          <div className="w-10 h-10 rounded-xl bg-blue-100 text-slate-800 flex items-center justify-center font-bold text-lg shrink-0">
                            {item.verifiedLogo}
                          </div>
                          <div>
                            <h3 className="text-base font-bold text-slate-900">{item.title}</h3>
                            <p className="text-xs text-slate-600 font-medium">{item.company}</p>
                          </div>
                        </div>
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                          {item.type}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 gap-2 text-xs text-slate-600 my-4 bg-white p-3 rounded-xl border border-slate-200/60">
                        <div className="flex items-center gap-1.5">
                          <MapPin className="w-3.5 h-3.5 text-slate-400" />
                          <span>{item.location}</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <Clock className="w-3.5 h-3.5 text-slate-400" />
                          <span>{item.duration}</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <DollarSign className="w-3.5 h-3.5 text-emerald-600" />
                          <span className="font-bold text-slate-800">{item.stipend}</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <Zap className="w-3.5 h-3.5 text-amber-500" />
                          <span>{item.posted}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-2 border-t border-slate-200/60">
                      <div className="flex items-center gap-1">
                        {item.skills.map((s, i) => (
                          <span key={i} className="text-[10px] bg-slate-200/70 text-slate-700 font-medium px-2 py-0.5 rounded">
                            {s}
                          </span>
                        ))}
                      </div>
                      <Link to="/register" className="inline-flex items-center text-xs font-bold text-blue-600 hover:text-blue-700">
                        <span>Apply Now</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </Link>
                    </div>
                  </div>
                ))}
              </div>

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
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {placementDrivesData.map((drive) => (
                  <div key={drive.id} className="bg-slate-50/70 rounded-2xl border border-slate-200/80 p-6 flex flex-col justify-between hover:border-blue-300 hover:bg-white transition-all shadow-xs">
                    <div>
                      <div className="flex items-center justify-between mb-3">
                        <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${drive.badgeColor}`}>
                          {drive.status}
                        </span>
                        <span className="text-[11px] text-slate-500 flex items-center gap-1">
                          <Calendar className="w-3.5 h-3.5" />
                          {drive.date}
                        </span>
                      </div>

                      <h3 className="text-base font-bold text-slate-900 mb-0.5">{drive.role}</h3>
                      <p className="text-xs text-blue-600 font-bold mb-3">{drive.company}</p>

                      <div className="space-y-2 bg-white p-3.5 rounded-xl border border-slate-200/70 text-xs mb-4">
                        <div>
                          <span className="text-slate-400 font-medium">Package (CTC):</span>
                          <p className="font-extrabold text-slate-900 text-sm">{drive.ctc}</p>
                        </div>
                        <div>
                          <span className="text-slate-400 font-medium">Eligibility:</span>
                          <p className="text-slate-700 text-xs font-semibold">{drive.eligibility}</p>
                        </div>
                        <div>
                          <span className="text-slate-400 font-medium">Rounds:</span>
                          <p className="text-slate-600 text-[11px]">{drive.rounds}</p>
                        </div>
                      </div>
                    </div>

                    <Button to="/register" variant="primary" size="sm" className="w-full justify-center">
                      Register for Drive
                    </Button>
                  </div>
                ))}
              </div>

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
        <div className="section-container">
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
      <section className="section-container">
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

      {/* 5. STAKEHOLDER SECTIONS (Students, Colleges, Industry) */}
      <section className="bg-slate-50 py-16 border-y border-slate-200/80">
        <div className="section-container space-y-16">
          
          {/* Section: For Students */}
          <div className="bg-white rounded-2xl border border-slate-200/80 p-8 sm:p-10 shadow-sm">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
              <div className="lg:col-span-7 space-y-4">
                <span className="badge-blue">For Students</span>
                <h3 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
                  Build Proof of Skills & Secure Opportunities
                </h3>
                <p className="text-sm sm:text-base text-slate-600 leading-relaxed">
                  Bridge the gap between theoretical campus learning and high-impact industry careers. Discover where you stand, learn through actionable roadmaps, and build verified proof of what you can do.
                </p>
                <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-2 text-sm text-slate-700">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                    <span>Skill awareness & gap identification</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                    <span>Structured milestone roadmaps</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                    <span>Verified project & internship evidence</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                    <span>Placement and mentorship access</span>
                  </li>
                </ul>
                <div className="pt-3">
                  <Button to="/for-students" variant="primary" size="md">
                    Explore Student Journey
                  </Button>
                </div>
              </div>
              <div className="lg:col-span-5 bg-blue-50/60 rounded-xl p-6 border border-blue-100">
                <div className="space-y-3">
                  <div className="p-3 bg-white rounded-lg border border-slate-200 shadow-2xs">
                    <p className="text-xs font-bold text-slate-800">1. Assess Capability</p>
                    <p className="text-[11px] text-slate-500">Benchmark your technical & problem-solving abilities.</p>
                  </div>
                  <div className="p-3 bg-white rounded-lg border border-slate-200 shadow-2xs">
                    <p className="text-xs font-bold text-slate-800">2. Complete Milestones</p>
                    <p className="text-[11px] text-slate-500">Work on assignments reviewed by trainers and mentors.</p>
                  </div>
                  <div className="p-3 bg-white rounded-lg border border-slate-200 shadow-2xs">
                    <p className="text-xs font-bold text-slate-800">3. Apply with Proof</p>
                    <p className="text-[11px] text-slate-500">Stand out to recruiters with verified skill evidence.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Section: For Colleges */}
          <div className="bg-white rounded-2xl border border-slate-200/80 p-8 sm:p-10 shadow-sm">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
              <div className="lg:col-span-5 order-2 lg:order-1 bg-indigo-50/50 rounded-xl p-6 border border-indigo-100">
                <div className="space-y-3">
                  <div className="p-3 bg-white rounded-lg border border-slate-200 shadow-2xs">
                    <p className="text-xs font-bold text-slate-800">Real-Time Cohort Analytics</p>
                    <p className="text-[11px] text-slate-500">Track skill gaps across batches and departments.</p>
                  </div>
                  <div className="p-3 bg-white rounded-lg border border-slate-200 shadow-2xs">
                    <p className="text-xs font-bold text-slate-800">TPO Placement Dashboard</p>
                    <p className="text-[11px] text-slate-500">Match eligible students with incoming corporate drives.</p>
                  </div>
                  <div className="p-3 bg-white rounded-lg border border-slate-200 shadow-2xs">
                    <p className="text-xs font-bold text-slate-800">Industry Collaboration</p>
                    <p className="text-[11px] text-slate-500">Coordinate joint workshops and live project sponsorships.</p>
                  </div>
                </div>
              </div>
              <div className="lg:col-span-7 order-1 lg:order-2 space-y-4">
                <span className="badge-blue">For Colleges & TPOs</span>
                <h3 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
                  Institutional Transparency & Enhanced Placement
                </h3>
                <p className="text-sm sm:text-base text-slate-600 leading-relaxed">
                  Equip Training and Placement Officers (TPOs) and academic departments with complete visibility into student readiness, training tracking, and industry partner connections.
                </p>
                <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-2 text-sm text-slate-700">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                    <span>Student skill visibility across batches</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                    <span>Training and curriculum sync</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                    <span>Internship and placement coordination</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                    <span>Outcome analytics and reporting</span>
                  </li>
                </ul>
                <div className="pt-3">
                  <Button to="/for-colleges" variant="primary" size="md">
                    Explore for Colleges
                  </Button>
                </div>
              </div>
            </div>
          </div>

          {/* Section: For Industry */}
          <div className="bg-white rounded-2xl border border-slate-200/80 p-8 sm:p-10 shadow-sm">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
              <div className="lg:col-span-7 space-y-4">
                <span className="badge-blue">For Industry & Companies</span>
                <h3 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
                  Direct Access to Verified Talent
                </h3>
                <p className="text-sm sm:text-base text-slate-600 leading-relaxed">
                  Reduce recruitment overhead and hire with confidence. Post specific skill requirements, sponsor real-world projects, and discover pre-vetted candidates with proven capabilities.
                </p>
                <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-2 text-sm text-slate-700">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                    <span>Precise skill-based candidate matching</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                    <span>Internship and direct job posting</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                    <span>Industry project sponsorship</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                    <span>Direct academia collaboration</span>
                  </li>
                </ul>
                <div className="pt-3">
                  <Button to="/for-industry" variant="primary" size="md">
                    Explore for Industry
                  </Button>
                </div>
              </div>
              <div className="lg:col-span-5 bg-slate-900 text-white rounded-xl p-6 border border-slate-800">
                <div className="space-y-3">
                  <div className="p-3 bg-slate-800/80 rounded-lg border border-slate-700">
                    <p className="text-xs font-bold text-white">Post Skill Requirements</p>
                    <p className="text-[11px] text-slate-400">Specify exact tech stacks and required proficiency levels.</p>
                  </div>
                  <div className="p-3 bg-slate-800/80 rounded-lg border border-slate-700">
                    <p className="text-xs font-bold text-white">Review Verified Portfolios</p>
                    <p className="text-[11px] text-slate-400">Assess real project evidence and peer reviews before interviewing.</p>
                  </div>
                  <div className="p-3 bg-slate-800/80 rounded-lg border border-slate-700">
                    <p className="text-xs font-bold text-white">Direct Campus Drives</p>
                    <p className="text-[11px] text-slate-400">Coordinate seamlessly with affiliated college placement cells.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* 6. CAREER JOURNEY / IMPACT SECTION */}
      <section className="section-container">
        <div className="text-center max-w-3xl mx-auto space-y-3 mb-16">
          <span className="badge-blue">The SKILLY Continuum</span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
            From First Step to Career Impact
          </h2>
          <p className="text-base sm:text-lg text-slate-600">
            A cohesive framework uniting every stage of professional development.
          </p>
        </div>

        {/* Visual Timeline / Process Ribbon */}
        <div className="relative">
          <div className="hidden lg:block absolute top-1/2 left-0 right-0 h-0.5 bg-blue-100 -translate-y-1/2 z-0"></div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 relative z-10">
            <div className="bg-white rounded-2xl border border-slate-200 p-6 text-center card-hover">
              <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto mb-4 border border-blue-200">
                <Target className="w-6 h-6" />
              </div>
              <h4 className="font-bold text-slate-900 mb-1">1. Assessment & Gap</h4>
              <p className="text-xs text-slate-600">Diagnostic testing and competency analysis to establish baseline.</p>
            </div>

            <div className="bg-white rounded-2xl border border-slate-200 p-6 text-center card-hover">
              <div className="w-12 h-12 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto mb-4 border border-indigo-200">
                <BookOpen className="w-6 h-6" />
              </div>
              <h4 className="font-bold text-slate-900 mb-1">2. Roadmap & Learning</h4>
              <p className="text-xs text-slate-600">Milestone courses, trainer assistance, and structured mastery.</p>
            </div>

            <div className="bg-white rounded-2xl border border-slate-200 p-6 text-center card-hover">
              <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto mb-4 border border-emerald-200">
                <Briefcase className="w-6 h-6" />
              </div>
              <h4 className="font-bold text-slate-900 mb-1">3. Projects & Mentorship</h4>
              <p className="text-xs text-slate-600">Hands-on internships and guidance from senior practitioners.</p>
            </div>

            <div className="bg-white rounded-2xl border border-slate-200 p-6 text-center card-hover">
              <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center mx-auto mb-4 border border-amber-200">
                <Award className="w-6 h-6" />
              </div>
              <h4 className="font-bold text-slate-900 mb-1">4. Placement & Growth</h4>
              <p className="text-xs text-slate-600">Verified placement matching and long-term career alumni support.</p>
            </div>
          </div>
        </div>
      </section>

      {/* 7. FINAL CTA SECTION */}
      <section className="section-container">
        <div className="bg-gradient-to-r from-blue-700 via-blue-600 to-indigo-700 rounded-3xl p-8 sm:p-14 text-white text-center shadow-soft-lg relative overflow-hidden">
          
          {/* Subtle decorative circles */}
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

