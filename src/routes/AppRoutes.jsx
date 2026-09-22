import React, { useEffect } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';

// Public Pages
import Home from '../pages/Home';
import About from '../pages/About';
import Features from '../pages/Features';
import HowItWorks from '../pages/HowItWorks';
import ForStudents from '../pages/ForStudents';
import ForColleges from '../pages/ForColleges';
import ForIndustry from '../pages/ForIndustry';
import Contact from '../pages/Contact';
import Pricing from '../pages/Pricing';

// Auth Pages
import Login from '../pages/Login';
import Register from '../pages/Register';

// Route Guards
import ProtectedRoute from './ProtectedRoute';
import RoleRoute from './RoleRoute';

// Role Dashboard / Workspace Pages
import Student from '../pages/Student';
import College from '../pages/College';
import Teacher from '../pages/Teacher';
import Industry from '../pages/Industry';
import Alumni from '../pages/Alumni';

// Platform Module Pages
import Skills from '../pages/Skills';
import Training from '../pages/Training';
import Internships from '../pages/Internships';
import Placements from '../pages/Placements';
import Portfolio from '../pages/Portfolio';
import Mentorship from '../pages/Mentorship';
import Community from '../pages/Community';
import Competitions from '../pages/Competitions';
import Notifications from '../pages/Notifications';
import AI from '../pages/AI';

// Helper component to auto-scroll to top on route navigation
function ScrollToTop() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
}

export default function AppRoutes() {
  return (
    <>
      <ScrollToTop />
      <Routes>
        {/* ========================================= */}
        {/* Public Website Routes (No Auth Required)  */}
        {/* ========================================= */}
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/features" element={<Features />} />
        <Route path="/how-it-works" element={<HowItWorks />} />
        <Route path="/for-students" element={<ForStudents />} />
        <Route path="/for-colleges" element={<ForColleges />} />
        <Route path="/for-industry" element={<ForIndustry />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/pricing" element={<Pricing />} />

        {/* Authentication Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* ========================================= */}
        {/* Protected Role-Based Application Routes   */}
        {/* ========================================= */}
        <Route element={<ProtectedRoute />}>
          {/* Student Portal (STUDENT only) */}
          <Route
            path="/student/*"
            element={
              <RoleRoute allowedRoles={['STUDENT']}>
                <Student />
              </RoleRoute>
            }
          />

          {/* College / TPO Portal (COLLEGE_ADMIN only) */}
          <Route
            path="/college/*"
            element={
              <RoleRoute allowedRoles={['COLLEGE_ADMIN']}>
                <College />
              </RoleRoute>
            }
          />

          {/* Teacher / Trainer Portal (TEACHER only) */}
          <Route
            path="/teacher/*"
            element={
              <RoleRoute allowedRoles={['TEACHER']}>
                <Teacher />
              </RoleRoute>
            }
          />

          {/* Industry / Recruiter Portal (INDUSTRY only) */}
          <Route
            path="/industry/*"
            element={
              <RoleRoute allowedRoles={['INDUSTRY']}>
                <Industry />
              </RoleRoute>
            }
          />

          {/* Alumni / Mentor Portal (ALUMNI only) */}
          <Route
            path="/alumni/*"
            element={
              <RoleRoute allowedRoles={['ALUMNI']}>
                <Alumni />
              </RoleRoute>
            }
          />

          {/* General Platform Modules (Protected for any authenticated role) */}
          <Route path="/skills" element={<Skills />} />
          <Route path="/training" element={<Training />} />
          <Route path="/internships" element={<Internships />} />
          <Route path="/placements" element={<Placements />} />
          <Route path="/portfolio" element={<Portfolio />} />
          <Route path="/mentorship" element={<Mentorship />} />
          <Route path="/community" element={<Community />} />
          <Route path="/competitions" element={<Competitions />} />
          <Route path="/notifications" element={<Notifications />} />
          <Route path="/ai" element={<AI />} />
        </Route>

        {/* Fallback Route */}
        <Route path="*" element={<Home />} />
      </Routes>
    </>
  );
}
