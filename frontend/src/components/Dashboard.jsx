import React, { useState } from 'react';
import { Users, Video, ArrowRight, Activity, Trash2, AlertTriangle } from 'lucide-react';

export default function Dashboard({ childrenList, sessionsList, onSelectSession, onNewSession, onDeleteSession }) {
  const [sessionToDelete, setSessionToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const [toastMsg, setToastMsg] = useState(null);

  const completedSessions = sessionsList.filter(s => s.status === 'COMPLETED');
  const reassessSessions = sessionsList.filter(s => s.status === 'REASSESSMENT_REQUIRED');

  const confirmDelete = async () => {
    if (!sessionToDelete) return;
    setDeleting(true);
    try {
      await onDeleteSession(sessionToDelete.id);
      setToastMsg('Session deleted successfully.');
      setTimeout(() => setToastMsg(null), 3000);
      setSessionToDelete(null);
    } catch (err) {
      alert(err.message || 'Unable to delete session. Please try again.');
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div>
      {/* Toast notification */}
      {toastMsg && (
        <div style={{ position: 'fixed', top: '80px', right: '20px', background: 'rgba(16,185,129,0.9)', color: '#fff', padding: '0.75rem 1.25rem', borderRadius: '8px', zIndex: 1000, fontWeight: 600, boxShadow: '0 4px 12px rgba(0,0,0,0.3)' }}>
          {toastMsg}
        </div>
      )}

      {/* Hero Banner */}
      <div className="research-banner">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem', color: 'var(--primary)' }}>
          <Activity size={20} />
          <span style={{ fontWeight: 700, fontSize: '0.95rem', letterSpacing: '0.05em' }}>BEHAVIORAL MONITORING & ASSESSMENT PLATFORM</span>
        </div>
        <h1 className="banner-title">NeuroTrack AI: Confidence-Aware Multimodal Behavioral Monitoring</h1>
        <p className="banner-desc">
          Automated analysis platform for personal behavioral monitoring and intervention-response assessment. 
          Quantifies observable traits (joint attention, gaze orientation, motor imitation) from standardized task recordings using computer vision.
        </p>
      </div>

      {/* Metrics Row */}
      <div className="grid-4" style={{ marginBottom: '2rem' }}>
        <div className="metric-card">
          <div className="metric-label">Registered Children</div>
          <div className="metric-value">{childrenList.length}</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Total Sessions</div>
          <div className="metric-value">{sessionsList.length}</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Completed Analyses</div>
          <div className="metric-value" style={{ color: 'var(--status-high)' }}>{completedSessions.length}</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Quality Reassessments</div>
          <div className="metric-value" style={{ color: 'var(--status-reassess)' }}>{reassessSessions.length}</div>
        </div>
      </div>

      {/* Recent Sessions Table */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <h2 className="section-heading" style={{ margin: 0 }}>
            <Activity size={20} style={{ color: 'var(--primary)' }} />
            <span>Recent Behavioral Sessions</span>
          </h2>
          <button className="btn-primary" onClick={onNewSession}>
            <Video size={16} />
            <span>Start New Session</span>
          </button>
        </div>

        {sessionsList.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3.5rem 1rem' }}>
            <p style={{ fontWeight: 700, fontSize: '1.15rem', color: 'var(--text-main)', marginBottom: '0.4rem' }}>
              No behavioral sessions yet.
            </p>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
              Create a session and upload a recording to begin analysis.
            </p>
            <button className="btn-primary" onClick={onNewSession}>
              <Video size={16} />
              <span>Start New Session</span>
            </button>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Session ID</th>
                <th>Child</th>
                <th>Task</th>
                <th>Status</th>
                <th>Date</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {sessionsList.map(session => {
                const childProfile = session.child || childrenList.find(c => c.id === session.child_id);
                const childIdLabel = childProfile 
                  ? (childProfile.profile_number 
                      ? `Profile #${String(childProfile.profile_number).padStart(2, '0')} (${childProfile.external_id})` 
                      : childProfile.external_id) 
                  : 'Subject Profile';
                return (
                  <tr key={session.id}>
                    <td style={{ fontFamily: 'var(--font-code)', fontSize: '0.85rem' }}>
                      Session #{session.id.substring(0, 6)}
                    </td>
                    <td style={{ fontWeight: 600, color: 'var(--primary)' }}>
                      {childIdLabel}
                    </td>
                    <td>{session.recordings && session.recordings.length > 0 ? (session.recordings[0].task_id?.includes('imitation') ? 'Imitation' : 'Joint Attention') : 'Behavioral Task'}</td>
                    <td>
                      <span className={`badge-level ${
                        session.status === 'COMPLETED' ? 'badge-high' :
                        session.status === 'REASSESSMENT_REQUIRED' ? 'badge-reassess' : 'badge-medium'
                      }`}>
                        {session.status}
                      </span>
                    </td>
                    <td style={{ color: 'var(--text-muted)' }}>
                      {new Date(session.created_at).toLocaleDateString()}
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                        <button 
                          className="btn-secondary" 
                          style={{ padding: '0.35rem 0.75rem', fontSize: '0.82rem' }}
                          onClick={() => onSelectSession(session.id)}
                        >
                          <span>View Results</span>
                          <ArrowRight size={14} />
                        </button>
                        <button 
                          className="btn-secondary" 
                          style={{ padding: '0.35rem 0.6rem', color: 'var(--status-reassess)', borderColor: 'var(--badge-reassess-border)' }}
                          title="Delete Session"
                          onClick={() => setSessionToDelete(session)}
                        >
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {sessionToDelete && (
        <div style={{ position: 'fixed', inset: 0, background: 'var(--bg-modal-backdrop)', backdropFilter: 'blur(8px)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1.5rem' }}>
          <div className="card" style={{ maxWidth: '500px', width: '100%', borderColor: 'var(--badge-reassess-border)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: 'var(--badge-reassess-text)', marginBottom: '1rem' }}>
              <AlertTriangle size={24} />
              <h2 className="section-heading" style={{ margin: 0, color: 'var(--badge-reassess-text)', fontSize: '1.2rem' }}>
                Delete Behavioral Session?
              </h2>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', marginBottom: '1.5rem', lineHeight: '1.5' }}>
              This will permanently delete session <code style={{ color: 'var(--primary)', fontFamily: 'var(--font-code)' }}>{sessionToDelete.id}</code>, analysis results, behavioral features, quality assessment and associated uploaded/processed recordings. <strong>This action cannot be undone.</strong>
            </p>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button 
                className="btn-secondary" 
                disabled={deleting}
                onClick={() => setSessionToDelete(null)}
              >
                Cancel
              </button>
              <button 
                className="btn-primary" 
                style={{ background: 'linear-gradient(135deg, #ef4444 0%, #f43f5e 100%)', color: '#fff' }}
                disabled={deleting}
                onClick={confirmDelete}
              >
                {deleting ? 'Deleting...' : 'Delete Session'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
