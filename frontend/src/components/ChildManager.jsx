import React, { useState } from 'react';
import { Users, UserPlus, Trash2, ClipboardList, AlertTriangle } from 'lucide-react';
import ParentQuestionnaireModal from './ParentQuestionnaireModal';

export default function ChildManager({ childrenList, onCreateChild, onDeleteChild, onRefresh }) {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    external_id: '',
    age_months: 36,
    gender: 'Male',
    notes: ''
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [childToDelete, setChildToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const [activeQuestionnaireChild, setActiveQuestionnaireChild] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await onCreateChild({
        external_id: formData.external_id.trim(),
        age_months: parseInt(formData.age_months),
        gender: formData.gender,
        notes: formData.notes
      });
      setShowForm(false);
      setFormData({ external_id: '', age_months: 36, gender: 'Male', notes: '' });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const confirmDeleteChild = async () => {
    if (!childToDelete) return;
    setDeleting(true);
    try {
      await onDeleteChild(childToDelete.id);
      setChildToDelete(null);
      if (onRefresh) onRefresh();
    } catch (err) {
      alert(err.message || 'Failed to delete child profile.');
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h1 className="section-heading" style={{ fontSize: '1.5rem', margin: 0 }}>
          <Users size={24} style={{ color: 'var(--primary)' }} />
          <span>Child Profiles Directory</span>
        </h1>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          <UserPlus size={18} />
          <span>{showForm ? 'Cancel' : 'Add Child Profile'}</span>
        </button>
      </div>

      {showForm && (
        <div className="card" style={{ marginBottom: '2rem', borderColor: 'var(--primary)' }}>
          <h2 className="section-heading">Register Child Profile</h2>
          {error && (
            <div style={{ padding: '0.75rem 1rem', background: 'var(--badge-reassess-bg)', border: '1px solid var(--badge-reassess-border)', borderRadius: '8px', color: 'var(--badge-reassess-text)', marginBottom: '1rem', fontSize: '0.9rem' }}>
              {error}
            </div>
          )}
          <form onSubmit={handleSubmit}>
            <div className="grid-3">
              <div className="form-group">
                <label className="form-label">External Anonymized ID *</label>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="e.g. C-1042" 
                  required
                  value={formData.external_id}
                  onChange={e => setFormData({ ...formData, external_id: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Age (Months) *</label>
                <input 
                  type="number" 
                  className="form-input" 
                  min="6" 
                  max="180" 
                  required
                  value={formData.age_months}
                  onChange={e => setFormData({ ...formData, age_months: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Gender *</label>
                <select 
                  className="form-select"
                  value={formData.gender}
                  onChange={e => setFormData({ ...formData, gender: e.target.value })}
                >
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Research / Clinical Task Notes</label>
              <textarea 
                className="form-textarea" 
                rows="2"
                placeholder="Optional baseline observations or notes"
                value={formData.notes}
                onChange={e => setFormData({ ...formData, notes: e.target.value })}
              ></textarea>
            </div>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Saving Profile...' : 'Save Child Record'}
            </button>
          </form>
        </div>
      )}

      <div className="card">
        {childrenList.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
            <p style={{ fontWeight: 700, fontSize: '1.1rem', color: 'var(--text-main)', marginBottom: '0.4rem' }}>
              No child profiles registered.
            </p>
            <p style={{ fontSize: '0.9rem' }}>
              Click "Add Child Profile" above to register a subject.
            </p>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>PROFILE #</th>
                <th>EXTERNAL ID</th>
                <th>AGE (MONTHS)</th>
                <th>GENDER</th>
                <th>REGISTERED DATE</th>
                <th>PARENT QUESTIONNAIRE</th>
                <th>ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              {childrenList.map((child, idx) => {
                const profileNumStr = child.profile_number 
                  ? `Profile #${String(child.profile_number).padStart(2, '0')}` 
                  : `Profile #${String(idx + 1).padStart(2, '0')}`;

                return (
                  <tr key={child.id}>
                    <td style={{ fontWeight: 700, color: 'var(--primary)', fontFamily: 'var(--font-code)' }}>
                      {profileNumStr}
                    </td>
                    <td style={{ fontWeight: 600 }}>{child.external_id}</td>
                    <td>{child.age_months} mos ({ (child.age_months / 12).toFixed(1) } yrs)</td>
                    <td>{child.gender}</td>
                    <td style={{ color: 'var(--text-muted)' }}>{new Date(child.created_at).toLocaleDateString()}</td>
                    <td>
                      <button
                        className="btn-secondary"
                        style={{ padding: '0.3rem 0.65rem', fontSize: '0.82rem', gap: '0.35rem' }}
                        onClick={() => setActiveQuestionnaireChild(child)}
                      >
                        <ClipboardList size={14} style={{ color: 'var(--primary)' }} />
                        <span>Parent Questionnaire</span>
                      </button>
                    </td>
                    <td>
                      <button 
                        className="btn-secondary" 
                        style={{ padding: '0.35rem 0.6rem', color: 'var(--status-reassess)', borderColor: 'var(--badge-reassess-border)' }}
                        title="Delete Profile"
                        onClick={() => setChildToDelete(child)}
                      >
                        <Trash2 size={15} />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {childToDelete && (
        <div style={{ position: 'fixed', inset: 0, background: 'var(--bg-modal-backdrop)', backdropFilter: 'blur(8px)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1.5rem' }}>
          <div className="card" style={{ maxWidth: '520px', width: '100%', borderColor: 'var(--badge-reassess-border)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: 'var(--badge-reassess-text)', marginBottom: '1rem' }}>
              <AlertTriangle size={24} />
              <h2 className="section-heading" style={{ margin: 0, color: 'var(--badge-reassess-text)', fontSize: '1.2rem' }}>
                Delete this child profile?
              </h2>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', marginBottom: '1.5rem', lineHeight: '1.5' }}>
              This will permanently delete the child profile <strong style={{ color: 'var(--text-main)' }}>{childToDelete.profile_number ? `Profile #${String(childToDelete.profile_number).padStart(2, '0')}` : childToDelete.external_id}</strong> ({childToDelete.external_id}) and all associated sessions, recordings, assessments, behavioral features and analysis results.
            </p>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button 
                className="btn-secondary" 
                disabled={deleting}
                onClick={() => setChildToDelete(null)}
              >
                Cancel
              </button>
              <button 
                className="btn-primary" 
                style={{ background: 'linear-gradient(135deg, #ef4444 0%, #f43f5e 100%)', color: '#fff' }}
                disabled={deleting}
                onClick={confirmDeleteChild}
              >
                {deleting ? 'Deleting...' : 'Delete Profile'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Parent Questionnaire Modal */}
      {activeQuestionnaireChild && (
        <ParentQuestionnaireModal
          child={activeQuestionnaireChild}
          onClose={() => setActiveQuestionnaireChild(null)}
          onSaved={() => {
            if (onRefresh) onRefresh();
          }}
        />
      )}
    </div>
  );
}
