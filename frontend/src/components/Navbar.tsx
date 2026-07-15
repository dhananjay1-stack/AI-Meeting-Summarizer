import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../lib/auth';
import { LogOut, Settings, Moon, Sun, Sparkles } from 'lucide-react';
import { useEffect, useState } from 'react';
import './Navbar.css';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'dark';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar glass-card">
      <Link to="/" className="navbar-brand">
        <Sparkles size={22} />
        <span className="navbar-brand-text gradient-text">MeetingAI</span>
      </Link>

      <div className="navbar-actions">
        <button className="btn-ghost" onClick={toggleTheme} title="Toggle theme">
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        <Link to="/settings" className="btn-ghost" title="Settings">
          <Settings size={18} />
        </Link>
        <div className="navbar-user">
          <span className="navbar-username">{user?.username}</span>
        </div>
        <button className="btn-ghost" onClick={handleLogout} title="Logout">
          <LogOut size={18} />
        </button>
      </div>
    </nav>
  );
}
