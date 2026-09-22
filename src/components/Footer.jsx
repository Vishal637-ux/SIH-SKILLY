import React from 'react';
import { Link } from 'react-router-dom';
import { GraduationCap, ArrowUpRight } from 'lucide-react';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-slate-900 text-slate-400 border-t border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10 lg:gap-8 pb-12 border-b border-slate-800">
          
          {/* Platform Identity */}
          <div className="lg:col-span-2 space-y-4">
            <Link to="/" className="flex items-center gap-2.5">
              <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/30">
                <GraduationCap className="w-6 h-6" />
              </div>
              <span className="text-2xl font-black tracking-tight text-white">
                SKILLY
              </span>
            </Link>
            <p className="text-sm text-slate-400 leading-relaxed max-w-sm">
              An Academia–Industry collaboration platform connecting Students, Colleges, Trainers, Industry, and Alumni into one continuous skill development and career growth ecosystem.
            </p>
            <div className="pt-2 text-xs text-slate-500">
              <span>Skill Development • Evidence • Experience • Placement</span>
            </div>
          </div>

          {/* Public Navigation */}
          <div>
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider mb-4">
              Platform
            </h3>
            <ul className="space-y-2.5 text-sm">
              <li>
                <Link to="/" className="hover:text-white transition-colors">
                  Home
                </Link>
              </li>
              <li>
                <Link to="/about" className="hover:text-white transition-colors">
                  About SKILLY
                </Link>
              </li>
              <li>
                <Link to="/features" className="hover:text-white transition-colors">
                  Features
                </Link>
              </li>
              <li>
                <Link to="/how-it-works" className="hover:text-white transition-colors">
                  How It Works
                </Link>
              </li>
              <li>
                <Link to="/contact" className="hover:text-white transition-colors">
                  Contact Us
                </Link>
              </li>
            </ul>
          </div>

          {/* Stakeholder Journeys */}
          <div>
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider mb-4">
              Stakeholders
            </h3>
            <ul className="space-y-2.5 text-sm">
              <li>
                <Link to="/for-students" className="hover:text-white transition-colors">
                  For Students
                </Link>
              </li>
              <li>
                <Link to="/for-colleges" className="hover:text-white transition-colors">
                  For Colleges & TPOs
                </Link>
              </li>
              <li>
                <Link to="/for-industry" className="hover:text-white transition-colors">
                  For Industry & Recruiters
                </Link>
              </li>
              <li>
                <Link to="/teacher" className="hover:text-white transition-colors">
                  For Teachers & Trainers
                </Link>
              </li>
              <li>
                <Link to="/alumni" className="hover:text-white transition-colors">
                  For Alumni & Mentors
                </Link>
              </li>
            </ul>
          </div>

          {/* Platform Modules & Access */}
          <div>
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider mb-4">
              Modules
            </h3>
            <ul className="space-y-2.5 text-sm">
              <li>
                <Link to="/skills" className="hover:text-white transition-colors">
                  Skill Assessment
                </Link>
              </li>
              <li>
                <Link to="/training" className="hover:text-white transition-colors">
                  Training & Workshops
                </Link>
              </li>
              <li>
                <Link to="/internships" className="hover:text-white transition-colors">
                  Internships & Projects
                </Link>
              </li>
              <li>
                <Link to="/placements" className="hover:text-white transition-colors">
                  Placement Drives
                </Link>
              </li>
              <li>
                <Link to="/competitions" className="hover:text-white transition-colors">
                  Competitions & Hackathons
                </Link>
              </li>
              <li>
                <Link to="/mentorship" className="hover:text-white transition-colors">
                  Mentorship Network
                </Link>
              </li>
              <li>
                <Link to="/portfolio" className="hover:text-white transition-colors">
                  Skill Passport
                </Link>
              </li>
            </ul>
          </div>

        </div>

        {/* Bottom bar */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
          <p>© {currentYear} SKILLY Platform. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <span className="text-slate-400">Academia–Industry Collaboration Ecosystem</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
