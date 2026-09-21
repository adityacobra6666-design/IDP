import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import ChildManager from './components/ChildManager';
import NewSession from './components/NewSession';
import SessionDetail from './components/SessionDetail';
import { ThemeProvider } from './context/ThemeContext';
import { checkHealth, fetchChildren, fetchTasks, fetchSessions, createChild, deleteChild, createSession, deleteSession, uploadRecording, analyzeSession } from './api';

function AppContent() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [healthStatus, setHealthStatus] = useState(null);
  const [childrenList, setChildrenList] = useState([]);
  const [childrenLoading, setChildrenLoading] = useState(true);
  const [childrenError, setChildrenError] = useState(null);

  const [tasksList, setTasksList] = useState([]);
  const [sessionsList, setSessionsList] = useState([]);
  const [selectedSessionId, setSelectedSessionId] = useState(null);

  const loadChildrenData = async () => {
    try {
      setChildrenLoading(true);
      setChildrenError(null);
      const c = await fetchChildren();
      setChildrenList(c);
    } catch (err) {
      console.error("Error fetching children:", err);
      setChildrenError(err.message || "Failed to load children");
    } finally {
      setChildrenLoading(false);
    }
  };

  const refreshData = async () => {
    loadChildrenData();
    try {
      const [h, t, s] = await Promise.all([
        checkHealth().catch(() => null),
        fetchTasks().catch(() => []),
        fetchSessions().catch(() => [])
      ]);
      setHealthStatus(h);
      setTasksList(t);
      setSessionsList(s);
    } catch (err) {
      console.error("Data refresh error:", err);
    }
  };

  useEffect(() => {
    refreshData();
  }, []);

  const handleSelectSession = (sessionId) => {
    setSelectedSessionId(sessionId);
    setActiveTab('session-detail');
  };

  const handleCreateChild = async (data) => {
    const newChild = await createChild(data);
    await refreshData();
    return newChild;
  };

  const handleDeleteChild = async (childId) => {
    await deleteChild(childId);
    await refreshData();
  };

  const handleDeleteSession = async (sessionId) => {
    await deleteSession(sessionId);
    await refreshData();
  };

  return (
    <div className="app-container">
      <Header 
        activeTab={activeTab} 
        setActiveTab={(tab) => {
          setSelectedSessionId(null);
          setActiveTab(tab);
        }} 
        healthStatus={healthStatus}
      />

      <main className="main-content">
        {activeTab === 'dashboard' && (
          <Dashboard 
            childrenList={childrenList}
            sessionsList={sessionsList}
            onSelectSession={handleSelectSession}
            onNewSession={() => setActiveTab('new-session')}
            onDeleteSession={handleDeleteSession}
          />
        )}

        {activeTab === 'children' && (
          <ChildManager 
            childrenList={childrenList}
            onCreateChild={handleCreateChild}
            onDeleteChild={handleDeleteChild}
            onRefresh={refreshData}
          />
        )}

        {activeTab === 'new-session' && (
          <NewSession 
            childrenList={childrenList}
            childrenLoading={childrenLoading}
            childrenError={childrenError}
            onRetryChildren={loadChildrenData}
            onOpenCreateChild={() => setActiveTab('children')}
            tasksList={tasksList}
            onCreateSession={createSession}
            onUploadRecording={uploadRecording}
            onAnalyzeSession={analyzeSession}
            onComplete={async (sessionId) => {
              await refreshData();
              handleSelectSession(sessionId);
            }}
          />
        )}

        {activeTab === 'session-detail' && selectedSessionId && (
          <SessionDetail 
            sessionId={selectedSessionId}
            onBack={() => setActiveTab('dashboard')}
          />
        )}
      </main>

      <footer className="app-footer">
        <div>
          <strong>NeuroTrack AI</strong> — Behavioral Monitoring & Assessment Platform
        </div>
        <div style={{ fontSize: '0.78rem', marginTop: '0.2rem', color: 'var(--text-dim)' }}>
          © {new Date().getFullYear()} NeuroTrack AI. All rights reserved.
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}
