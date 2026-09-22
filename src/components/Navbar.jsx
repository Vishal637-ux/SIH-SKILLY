import React, { useState, useEffect } from 'react';
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom';
import { 
  Menu, 
  X, 
  Search, 
  Moon, 
  Sun, 
  GraduationCap, 
  ChevronRight,
  User,
  LogOut,
  LayoutDashboard
} from 'lucide-react';
import Button from './Button';
import useAuth from '../hooks/useAuth';

const ROLE_PATH_MAP = {
  STUDENT: '/student',
  COLLEGE_ADMIN: '/college',
  TEACHER: '/teacher',
  INDUSTRY: '/industry',
  ALUMNI: '/alumni',
};

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [isScrolled, setIsScrolled] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);

  const { user, isAuthenticated, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    setIsOpen(false);
    setIsSearchOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { name: 'Home', path: '/' },
    { name: 'Features', path: '/features' },
    { name: 'How It Works', path: '/how-it-works' },
    { name: 'For Students', path: '/for-students' },
    { name: 'For Colleges', path: '/for-colleges' },
    { name: 'For Industry', path: '/for-industry' },
  ];

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
    document.documentElement.classList.toggle('dark');
  };

  const handleLogout = async () => {
    await logout();
    navigate('/', { replace: true });
  };

  const userRole = (user?.role || '').toUpperCase();
  const dashboardPath = ROLE_PATH_MAP[userRole] || '/student';
  const displayName = user?.profile?.first_name || user?.username || 'User';

  return (
    <header className={`sticky top-0 z-40 w-full transition-all duration-200 ${
      isScrolled 
        ? 'bg-white/95 backdrop-blur-md border-b border-slate-200/80 shadow-sm' 
        : 'bg-white/90 backdrop-blur-sm border-b border-slate-100'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 sm:h-20">
          
          {/* Brand Logo */}
          <Link to="/" className="flex items-center gap-2.5 group shrink-0">
            <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20 group-hover:bg-blue-700 transition-colors">
              <GraduationCap className="w-6 h-6" />
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-black tracking-tight text-slate-900 group-hover:text-blue-600 transition-colors">
                SKILLY
              </span>
              <span className="text-[10px] uppercase font-bold tracking-widest text-blue-600 -mt-1">
                Bridge to Future
              </span>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden lg:flex items-center gap-1 xl:gap-2">
            {navLinks.map((link) => (
              <NavLink
                key={link.path}
                to={link.path}
                className={({ isActive }) =>
                  `px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'text-blue-600 bg-blue-50/80 font-semibold'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`
                }
              >
                {link.name}
              </NavLink>
            ))}
          </nav>

          {/* Right Action Controls */}
          <div className="hidden md:flex items-center gap-2 lg:gap-3">
            
            {/* Search Button / Trigger */}
            <div className="relative">
              {isSearchOpen ? (
                <div className="flex items-center bg-slate-100 rounded-xl px-3 py-1.5 border border-slate-200">
                  <Search className="w-4 h-4 text-slate-400 mr-2" />
                  <input
                    type="text"
                    placeholder="Search skills, roles, tracks..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="bg-transparent text-xs sm:text-sm text-slate-800 placeholder-slate-400 outline-none w-48"
                    autoFocus
                  />
                  <button 
                    onClick={() => setIsSearchOpen(false)}
                    className="text-slate-400 hover:text-slate-600 p-0.5"
                    aria-label="Close search"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setIsSearchOpen(true)}
                  aria-label="Open search"
                  className="p-2 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-xl transition-colors"
                  title="Search platform"
                >
                  <Search className="w-4 h-4" />
                </button>
              )}
            </div>

            {/* Theme Toggle */}
            <button
              onClick={toggleDarkMode}
              aria-label="Toggle theme"
              className="p-2 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-xl transition-colors"
              title="Toggle theme appearance"
            >
              {isDarkMode ? <Sun className="w-4 h-4 text-amber-500" /> : <Moon className="w-4 h-4" />}
            </button>

            <div className="h-5 w-px bg-slate-200 mx-1"></div>

            {/* Auth Dependent Controls */}
            {isAuthenticated ? (
              <div className="flex items-center gap-2.5">
                <Link
                  to={dashboardPath}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-blue-50 hover:text-blue-600 border border-slate-200 transition-colors text-xs font-semibold text-slate-700"
                  title="Go to role dashboard"
                >
                  <LayoutDashboard className="w-3.5 h-3.5 text-blue-600" />
                  <span>{displayName}</span>
                  <span className="px-1.5 py-0.5 rounded-md bg-blue-600 text-white text-[9px] font-bold tracking-wider">
                    {userRole}
                  </span>
                </Link>

                <button
                  onClick={handleLogout}
                  aria-label="Sign out"
                  className="p-2 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-xl transition-colors"
                  title="Sign out of SKILLY"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Button to="/login" variant="ghost" size="sm" className="text-slate-700 font-medium">
                  Log In
                </Button>
                <Button to="/register" variant="primary" size="sm" className="font-semibold shadow-sm">
                  Sign Up
                </Button>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="flex items-center gap-2 md:hidden">
            <button
              onClick={toggleDarkMode}
              aria-label="Toggle theme"
              className="p-2 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-xl"
            >
              {isDarkMode ? <Sun className="w-5 h-5 text-amber-500" /> : <Moon className="w-5 h-5" />}
            </button>
            <button
              onClick={() => setIsOpen(!isOpen)}
              aria-label="Toggle menu"
              className="p-2 text-slate-700 hover:bg-slate-100 rounded-xl focus:outline-none"
            >
              {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>

        </div>
      </div>

      {/* Mobile Drawer Navigation */}
      {isOpen && (
        <div className="md:hidden border-b border-slate-200 bg-white px-4 pt-3 pb-6 shadow-xl space-y-4 animate-fadeIn">
          {/* Mobile Search */}
          <div className="flex items-center bg-slate-100 rounded-xl px-3 py-2 border border-slate-200">
            <Search className="w-4 h-4 text-slate-400 mr-2" />
            <input
              type="text"
              placeholder="Search skills, roadmaps, colleges..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-transparent text-sm text-slate-800 placeholder-slate-400 outline-none w-full"
            />
          </div>

          <div className="space-y-1">
            {navLinks.map((link) => (
              <NavLink
                key={link.path}
                to={link.path}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3 py-2.5 rounded-xl text-base font-medium ${
                    isActive
                      ? 'text-blue-600 bg-blue-50 font-semibold'
                      : 'text-slate-700 hover:bg-slate-50'
                  }`
                }
              >
                <span>{link.name}</span>
                <ChevronRight className="w-4 h-4 text-slate-400" />
              </NavLink>
            ))}
          </div>

          <div className="pt-3 border-t border-slate-100">
            {isAuthenticated ? (
              <div className="space-y-2">
                <Link
                  to={dashboardPath}
                  className="flex items-center justify-between p-3 rounded-xl bg-blue-50 border border-blue-200 text-blue-700 text-sm font-semibold"
                >
                  <div className="flex items-center gap-2">
                    <User className="w-4 h-4" />
                    <span>{displayName}</span>
                  </div>
                  <span className="px-2 py-0.5 rounded bg-blue-600 text-white text-xs font-bold">
                    {userRole}
                  </span>
                </Link>
                <Button onClick={handleLogout} variant="outline" size="md" className="w-full text-red-600 border-red-200 hover:bg-red-50">
                  <LogOut className="w-4 h-4 mr-2" />
                  Sign Out
                </Button>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-3">
                <Button to="/login" variant="outline" size="md" className="w-full">
                  Log In
                </Button>
                <Button to="/register" variant="primary" size="md" className="w-full">
                  Sign Up
                </Button>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
