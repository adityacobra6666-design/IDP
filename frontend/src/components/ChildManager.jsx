import React, { useState } from 'react';
import { Users, UserPlus } from 'lucide-react';

export default function ChildManager({ childrenList, onCreateChild }) {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    external_id: '',
    age_months: 36,
    gender: 'Male',
    notes: ''
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

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
        <table className="data-table">
          <thead>
            <tr>
              <th>Profile ID</th>
              <th>External ID</th>
              <th>Age (Months)</th>
              <th>Gender</th>
              <th>Registered Date</th>
            </tr>
          </thead>
          <tbody>
            {childrenList.map(child => (
              <tr key={child.id}>
                <td style={{ fontFamily: 'var(--font-code)', fontSize: '0.85rem' }}>{child.id.substring(0, 8)}...</td>
                <td style={{ fontWeight: 700, color: 'var(--primary)' }}>{child.external_id}</td>
                <td>{child.age_months} mos ({ (child.age_months / 12).toFixed(1) } yrs)</td>
                <td>{child.gender}</td>
                <td style={{ color: 'var(--text-muted)' }}>{new Date(child.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
