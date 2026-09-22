import React, { useState, useEffect } from 'react';
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom';
import { 
  Menu, 
  X, 
  Search, 
  Moon, 
  Sun, 
  Network, 
  ChevronRight,
  User,
  LogOut,
  LayoutDashboard
} from 'lucide-react';
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
  const [isDarkMode, setIsDarkMode] = useState(false);

  const { user, isAuthenticated, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    setIsOpen(false);
    setIsSearchOpen(false);
  }, [location.pathname]);

  const navLinks = [
    { name: 'Home', path: '/' },
    { name: 'Features', path: '/features' },
    { name: 'How It Works', path: '/how-it-works' },
    { name: 'For Students', path: '/for-students' },
    { name: 'For Colleges', path: '/for-colleges' },
    { name: 'For Industry', path: '/for-industry' },
    { name: 'Pricing', path: '/pricing' },
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
    <header className="sticky top-3 sm:top-4 z-50 w-full px-3 sm:px-6">
      <div className="max-w-6xl mx-auto bg-white/95 backdrop-blur-md rounded-full border border-slate-200/90 shadow-[0_4px_25px_-5px_rgba(0,0,0,0.06)] px-5 sm:px-7 py-2.5 flex items-center justify-between transition-all">
        
        {/* Brand Logo */}
        <Link to="/" className="flex items-center gap-2 group shrink-0">
          <Network className="w-5 h-5 text-blue-600 group-hover:scale-105 transition-transform" />
          <span className="text-base sm:text-lg font-black tracking-tight text-slate-900 group-hover:text-blue-600 transition-colors">
            SKILLY
          </span>
        </Link>

        {/* Desktop & Tablet Navigation Links */}
        <nav className="hidden md:flex items-center gap-0.5 lg:gap-1 xl:gap-2">
          {navLinks.map((link) => (
            <NavLink
              key={link.path}
              to={link.path}
              className={({ isActive }) =>
                `px-2.5 py-1.5 rounded-full text-[11px] lg:text-xs xl:text-sm font-medium transition-colors whitespace-nowrap ${
                  isActive
                    ? 'text-slate-900 font-semibold bg-slate-100/90'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`
              }
            >
              {link.name}
            </NavLink>
          ))}
        </nav>

        {/* Right Action Controls */}
        <div className="hidden md:flex items-center gap-2.5">
          
          {/* Search Button / Input */}
          <div className="relative">
            {isSearchOpen ? (
              <div className="flex items-center bg-slate-100 rounded-full px-3 py-1 border border-slate-200">
                <Search className="w-3.5 h-3.5 text-slate-400 mr-2" />
                <input
                  type="text"
                  placeholder="Search..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="bg-transparent text-xs text-slate-800 placeholder-slate-400 outline-none w-32"
                  autoFocus
                />
                <button 
                  onClick={() => setIsSearchOpen(false)}
                  className="text-slate-400 hover:text-slate-600 p-0.5"
                  aria-label="Close search"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            ) : (
              <button
                onClick={() => setIsSearchOpen(true)}
                aria-label="Open search"
                className="p-1.5 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-full transition-colors"
                title="Search platform"
              >
                <Search className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Dark Mode Toggle */}
          <button
            onClick={toggleDarkMode}
            aria-label="Toggle theme"
            className="p-1.5 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-full transition-colors"
            title="Toggle theme appearance"
          >
            {isDarkMode ? <Sun className="w-4 h-4 text-amber-500" /> : <Moon className="w-4 h-4" />}
          </button>

          {/* Auth Dependent Controls */}
          {isAuthenticated ? (
            <div className="flex items-center gap-2">
              <Link
                to={dashboardPath}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-100 hover:bg-blue-50 text-slate-800 text-xs font-semibold border border-slate-200 transition-colors"
              >
                <LayoutDashboard className="w-3.5 h-3.5 text-blue-600" />
                <span>{displayName}</span>
              </Link>
              <button
                onClick={handleLogout}
                aria-label="Sign out"
                className="p-1.5 text-slate-400 hover:text-red-600 rounded-full hover:bg-red-50 transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2 ml-1">
              <Link 
                to="/login" 
                className="text-xs sm:text-sm font-semibold text-slate-800 hover:text-slate-900 border border-slate-200/90 hover:bg-slate-50 px-4 py-1.5 rounded-full transition-all"
              >
                Log In
              </Link>
              <Link 
                to="/register" 
                className="text-xs sm:text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 px-5 py-1.5 rounded-full shadow-xs transition-all"
              >
                Sign Up
              </Link>
            </div>
          )}
        </div>

        {/* Mobile Menu Toggle Button */}
        <div className="flex items-center gap-1.5 md:hidden">
          <button
            onClick={toggleDarkMode}
            aria-label="Toggle theme"
            className="p-1.5 text-slate-500 hover:bg-slate-100 rounded-full"
          >
            {isDarkMode ? <Sun className="w-4 h-4 text-amber-500" /> : <Moon className="w-4 h-4" />}
          </button>
          <button
            onClick={() => setIsOpen(!isOpen)}
            aria-label="Toggle menu"
            className="p-1.5 text-slate-700 hover:bg-slate-100 rounded-full focus:outline-none"
          >
            {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

      </div>

      {/* Mobile Drawer Navigation */}
      {isOpen && (
        <div className="md:hidden mt-2 bg-white rounded-3xl border border-slate-200 px-5 pt-4 pb-6 shadow-2xl space-y-4 animate-fadeIn">
          <div className="space-y-1">
            {navLinks.map((link) => (
              <NavLink
                key={link.path}
                to={link.path}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3 py-2 rounded-xl text-sm font-medium ${
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

          <div className="pt-3 border-t border-slate-100 flex gap-2">
            {!isAuthenticated ? (
              <>
                <Link to="/login" className="w-1/2 text-center text-xs font-semibold py-2.5 rounded-full border border-slate-200 text-slate-800">
                  Log In
                </Link>
                <Link to="/register" className="w-1/2 text-center text-xs font-bold py-2.5 rounded-full bg-blue-600 text-white shadow-sm">
                  Sign Up
                </Link>
              </>
            ) : (
              <Link to={dashboardPath} className="w-full text-center text-xs font-bold py-2.5 rounded-full bg-blue-600 text-white">
                Go to Dashboard ({displayName})
              </Link>
            )}
          </div>
        </div>
      )}
    </header>
  );
}


