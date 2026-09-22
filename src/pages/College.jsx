import React, { useState } from 'react';
import { Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import PageContainer from '../components/PageContainer';
import { Building2, LayoutDashboard, Building, Users, Briefcase } from 'lucide-react';

import CollegeDashboardWorkspace from '../modules/college/components/CollegeDashboardWorkspace';
import CollegeDepartmentWorkspace from '../modules/college/components/CollegeDepartmentWorkspace';
import CollegeStudentRosterWorkspace from '../modules/college/components/CollegeStudentRosterWorkspace';
import CollegePlacementDriveWorkspace from '../modules/college/components/CollegePlacementDriveWorkspace';

export default function College() {
  const location = useLocation();

  // Navigation tabs definition
  const tabs = [
    {
      id: 'dashboard',
      label: 'Institutional Analytics',
      path: '/college/dashboard',
      icon: LayoutDashboard
    },
    {
      id: 'departments',
      label: 'Departments & Faculty',
      path: '/college/departments',
      icon: Building
    },
    {
      id: 'students',
      label: 'Student Roster',
      path: '/college/students',
      icon: Users
    },
    {
      id: 'drives',
      label: 'Placement Drives',
      path: '/college/drives',
      icon: Briefcase
    }
  ];

  // Determine active tab
  const activePath = location.pathname.endsWith('/college') 
    ? '/college/dashboard' 
    : location.pathname;

  return (
    <PageContainer
      badge="Institutional Operations"
      title="College & TPO Portal"
      subtitle="Institutional batch analytics, department management, skill aggregations, eligibility filtering, and placement logging."
    >
      <div className="space-y-6">
        {/* Navigation Tabs Header */}
        <div className="bg-white rounded-xl p-1.5 shadow-sm border border-slate-200/80 flex flex-wrap gap-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activePath.startsWith(tab.path);
            return (
              <Link
                key={tab.id}
                to={tab.path}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-semibold transition ${
                  isActive
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </Link>
            );
          })}
        </div>

        {/* Tab Route Content */}
        <Routes>
          <Route path="/" element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<CollegeDashboardWorkspace />} />
          <Route path="departments" element={<CollegeDepartmentWorkspace />} />
          <Route path="students" element={<CollegeStudentRosterWorkspace />} />
          <Route path="drives" element={<CollegePlacementDriveWorkspace />} />
        </Routes>
      </div>
    </PageContainer>
  );
}
