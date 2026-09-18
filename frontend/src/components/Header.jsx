import React from 'react';
import { Activity, Users, Video, LayoutDashboard, Sun, Moon } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

export default function Header({ activeTab, setActiveTab, healthStatus }) {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="app-header">
      <div className="brand-logo">
        <Activity className="w-6 h-6 text-cyan-400" />
        <span>NeuroTrack AI</span>
      </div>

      <nav className="nav-links">
        <button 
          className={`nav-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          <LayoutDashboard size={18} />
          <span>Dashboard</span>
        </button>
        <button 
          className={`nav-btn ${activeTab === 'children' ? 'active' : ''}`}
          onClick={() => setActiveTab('children')}
        >
          <Users size={18} />
          <span>Children</span>
        </button>
        <button 
          className={`nav-btn ${activeTab === 'new-session' ? 'active' : ''}`}
          onClick={() => setActiveTab('new-session')}
        >
          <Video size={18} />
          <span>New Session</span>
        </button>
      </nav>

      <div className="header-actions">
        <button
          className="theme-toggle-btn"
          onClick={toggleTheme}
          title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        <div className="system-status-badge">
          <span className="status-dot"></span>
          <span>Backend: {healthStatus ? healthStatus.status.toUpperCase() : 'CONNECTING...'}</span>
        </div>
      </div>
    </header>
  );
}
