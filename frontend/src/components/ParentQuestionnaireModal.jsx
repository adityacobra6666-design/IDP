import React, { useState, useEffect } from 'react';
import { ClipboardList, Save, X, Edit3, CheckCircle, HelpCircle } from 'lucide-react';
import { fetchParentQuestionnaire, saveParentQuestionnaire } from '../api';

const SENSORY_OPTIONS = [
  'Loud sounds',
  'Bright lights',
  'Crowded environments',
  'Certain textures',
  'Unexpected changes',
  'None known',
  'Not sure'
];

export default function ParentQuestionnaireModal({ child, onClose, onSaved }) {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(true);
  const [isNew, setIsNew] = useState(true);

  const [formData, setFormData] = useState({
    developmental_context: {
      school_setting: '',
      primary_communication: '',
      home_languages: ''
    },
    communication: {
      communicate_needs: '',
      communication_mode: ''
    },
    social_interaction: {
      initiate_interaction: '',
      respond_name: ''
    },
    attention_engagement: {
      engagement_ability: '',
      shift_attention: ''
    },
    imitation_play: {
      imitate_actions: '',
      play_style: ''
    },
    sensory_context: [],
    parent_observations: '',
    session_context: ''
  });

  useEffect(() => {
    async function loadData() {
      if (!child) return;
      try {
        setLoading(true);
        const data = await fetchParentQuestionnaire(child.id);
        if (data) {
          setIsNew(false);
          setIsEditing(false); // Default to viewing if already completed
          setFormData({
            developmental_context: data.developmental_context || { school_setting: '', primary_communication: '', home_languages: '' },
            communication: data.communication || { communicate_needs: '', communication_mode: '' },
            social_interaction: data.social_interaction || { initiate_interaction: '', respond_name: '' },
            attention_engagement: data.attention_engagement || { engagement_ability: '', shift_attention: '' },
            imitation_play: data.imitation_play || { imitate_actions: '', play_style: '' },
            sensory_context: data.sensory_context || [],
            parent_observations: data.parent_observations || '',
            session_context: data.session_context || ''
          });
        } else {
          setIsNew(true);
          setIsEditing(true);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [child]);

  const handleSensoryToggle = (option) => {
    if (!isEditing) return;
    setFormData(prev => {
      const current = prev.sensory_context || [];
      if (current.includes(option)) {
        return { ...prev, sensory_context: current.filter(o => o !== option) };
      } else {
        return { ...prev, sensory_context: [...current, option] };
      }
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSaving(true);
    try {
      await saveParentQuestionnaire(child.id, formData);
      setIsEditing(false);
      setIsNew(false);
      if (onSaved) onSaved();
    } catch (err) {
      setError(err.message || 'Failed to save questionnaire.');
    } finally {
      setSaving(false);
    }
  };

  const profileLabel = child.profile_number 
    ? `Profile #${String(child.profile_number).padStart(2, '0')}` 
    : `Child (${child.external_id})`;

  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'var(--bg-modal-backdrop)', 
      backdropFilter: 'blur(8px)', zIndex: 1000, display: 'flex', 
      alignItems: 'center', justifyContent: 'center', padding: '1.5rem',
      overflowY: 'auto'
    }}>
      <div className="card" style={{ 
        maxWidth: '850px', width: '100%', maxHeight: '90vh', overflowY: 'auto',
        borderColor: 'var(--primary)', position: 'relative' 
      }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', paddingBottom: '0.75rem', borderBottom: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <ClipboardList size={24} style={{ color: 'var(--primary)' }} />
            <div>
              <h2 className="section-heading" style={{ margin: 0, fontSize: '1.3rem' }}>
                Parent Questionnaire
              </h2>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                Structured Contextual Information for <span style={{ color: 'var(--primary)', fontWeight: 700 }}>{profileLabel}</span> ({child.external_id})
              </div>
            </div>
          </div>
          <button className="btn-secondary" style={{ padding: '0.35rem 0.6rem' }} onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        {error && (
          <div style={{ padding: '0.75rem 1rem', background: 'var(--badge-reassess-bg)', border: '1px solid var(--badge-reassess-border)', borderRadius: '8px', color: 'var(--badge-reassess-text)', marginBottom: '1rem', fontSize: '0.9rem' }}>
            {error}
          </div>
        )}

        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
            Loading questionnaire data...
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            {/* Context Note Notice */}
            <div style={{ 
              padding: '0.75rem 1rem', background: 'var(--bg-metric-card)', 
              border: '1px solid var(--border-color)', borderRadius: '8px', 
              color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '1.5rem',
              display: 'flex', alignItems: 'flex-start', gap: '0.6rem'
            }}>
              <HelpCircle size={18} style={{ color: 'var(--primary)', flexShrink: 0, marginTop: '2px' }} />
              <div>
                <strong>Contextual Record:</strong> This questionnaire collects parent-observed developmental and environmental context to assist researchers/clinicians. It is non-diagnostic and does not produce automated medical scores.
              </div>
            </div>

            {/* SECTION A: BASIC DEVELOPMENTAL CONTEXT */}
            <div style={{ marginBottom: '1.75rem' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--primary)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <span>A. Basic Developmental Context</span>
              </h3>
              <div className="grid-3">
                <div className="form-group">
                  <label className="form-label">Current School / Learning Setting</label>
                  <input 
                    type="text"
                    className="form-input"
                    placeholder="e.g. Daycare, Pre-K, Home"
                    disabled={!isEditing}
                    value={formData.developmental_context.school_setting}
                    onChange={e => setFormData({
                      ...formData,
                      developmental_context: { ...formData.developmental_context, school_setting: e.target.value }
                    })}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Primary Communication Mode</label>
                  <select 
                    className="form-select"
                    disabled={!isEditing}
                    value={formData.developmental_context.primary_communication}
                    onChange={e => setFormData({
                      ...formData,
                      developmental_context: { ...formData.developmental_context, primary_communication: e.target.value }
                    })}
                  >
                    <option value="">Select option...</option>
                    <option value="Verbal">Verbal</option>
                    <option value="Limited verbal">Limited verbal</option>
                    <option value="Non-verbal">Non-verbal</option>
                    <option value="Alternative/AAC">Alternative/AAC</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Languages Used at Home</label>
                  <input 
                    type="text"
                    className="form-input"
                    placeholder="e.g. English, Spanish"
                    disabled={!isEditing}
                    value={formData.developmental_context.home_languages}
                    onChange={e => setFormData({
                      ...formData,
                      developmental_context: { ...formData.developmental_context, home_languages: e.target.value }
                    })}
                  />
                </div>
              </div>
            </div>

            {/* SECTION B: COMMUNICATION */}
            <div style={{ marginBottom: '1.75rem' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--primary)', marginBottom: '0.75rem' }}>
                B. Communication
              </h3>
              <div className="grid-2">
                <div className="form-group">
                  <label className="form-label">Can the child communicate basic needs?</label>
                  <select 
                    className="form-select"
                    disabled={!isEditing}
                    value={formData.communication.communicate_needs}
                    onChange={e => setFormData({
                      ...formData,
                      communication: { ...formData.communication, communicate_needs: e.target.value }
                    })}
                  >
                    <option value="">Select option...</option>
                    <option value="Always">Always</option>
                    <option value="Often">Often</option>
                    <option value="Sometimes">Sometimes</option>
                    <option value="Rarely">Rarely</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">How does the child usually communicate?</label>
                  <select 
                    className="form-select"
                    disabled={!isEditing}
                    value={formData.communication.communication_mode}
                    onChange={e => setFormData({
                      ...formData,
                      communication: { ...formData.communication, communication_mode: e.target.value }
                    })}
                  >
                    <option value="">Select option...</option>
                    <option value="Speech">Speech</option>
                    <option value="Gestures">Gestures</option>
                    <option value="Pointing">Pointing</option>
                    <option value="AAC/device">AAC / Device</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
              </div>
            </div>

            {/* SECTION C: SOCIAL INTERACTION */}
            <div style={{ marginBottom: '1.75rem' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--primary)', marginBottom: '0.75rem' }}>
                C. Social Interaction
              </h3>
              <div className="grid-2">
                <div className="form-group">
                  <label className="form-label">How frequently does the child initiate interaction?</label>
                  <select 
                    className="form-select"
                    disabled={!isEditing}
                    value={formData.social_interaction.initiate_interaction}
                    onChange={e => setFormData({
                      ...formData,
                      social_interaction: { ...formData.social_interaction, initiate_interaction: e.target.value }
                    })}
                  >
                    <option value="">Select option...</option>
                    <option value="Frequently">Frequently</option>
                    <option value="Sometimes">Sometimes</option>
                    <option value="Rarely">Rarely</option>
                    <option value="Not sure">Not sure</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Response when someone calls their name?</label>
                  <select 
                    className="form-select"
                    disabled={!isEditing}
                    value={formData.social_interaction.respond_name}
                    onChange={e => setFormData({
                      ...formData,
                      social_interaction: { ...formData.social_interaction, respond_name: e.target.value }
                    })}
                  >
                    <option value="">Select option...</option>
                    <option value="Consistently">Consistently</option>
                    <option value="Often">Often</option>
                    <option value="Sometimes">Sometimes</option>
                    <option value="Rarely">Rarely</option>
                    <option value="Not sure">Not sure</option>
                  </select>
                </div>
              </div>
            </div>

            {/* SECTION D: ATTENTION / ENGAGEMENT */}
            <div style={{ marginBottom: '1.75rem' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--primary)', marginBottom: '0.75rem' }}>
                D. Attention & Engagement
              </h3>
              <div className="grid-2">
                <div className="form-group">
                  <label className="form-label">Typical ability to stay engaged with an activity:</label>
                  <select 
                    className="form-select"
                    disabled={!isEditing}
                    value={formData.attention_engagement.engagement_ability}
                    onChange={e => setFormData({
                      ...formData,
                      attention_engagement: { ...formData.attention_engagement, engagement_ability: e.target.value }
                    })}
                  >
                    <option value="">Select option...</option>
                    <option value="Short">Short</option>
                    <option value="Moderate">Moderate</option>
                    <option value="Long">Long</option>
                    <option value="Variable">Variable</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Does the child shift attention between people/objects?</label>
                  <select 
                    className="form-select"
                    disabled={!isEditing}
                    value={formData.attention_engagement.shift_attention}
                    onChange={e => setFormData({
                      ...formData,
                      attention_engagement: { ...formData.attention_engagement, shift_attention: e.target.value }
                    })}
                  >
                    <option value="">Select option...</option>
                    <option value="Frequently">Frequently</option>
                    <option value="Sometimes">Sometimes</option>
                    <option value="Rarely">Rarely</option>
                    <option value="Not sure">Not sure</option>
                  </select>
                </div>
              </div>
            </div>

            {/* SECTION E: IMITATION / PLAY */}
            <div style={{ marginBottom: '1.75rem' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--primary)', marginBottom: '0.75rem' }}>
                E. Imitation & Play
              </h3>
              <div className="grid-2">
                <div className="form-group">
                  <label className="form-label">Does the child imitate simple actions?</label>
                  <select 
                    className="form-select"
                    disabled={!isEditing}
                    value={formData.imitation_play.imitate_actions}
                    onChange={e => setFormData({
                      ...formData,
                      imitation_play: { ...formData.imitation_play, imitate_actions: e.target.value }
                    })}
                  >
                    <option value="">Select option...</option>
                    <option value="Frequently">Frequently</option>
                    <option value="Sometimes">Sometimes</option>
                    <option value="Rarely">Rarely</option>
                    <option value="Not sure">Not sure</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Preferred play style:</label>
                  <select 
                    className="form-select"
                    disabled={!isEditing}
                    value={formData.imitation_play.play_style}
                    onChange={e => setFormData({
                      ...formData,
                      imitation_play: { ...formData.imitation_play, play_style: e.target.value }
                    })}
                  >
                    <option value="">Select option...</option>
                    <option value="Social">Social</option>
                    <option value="Solitary">Solitary</option>
                    <option value="Parallel">Parallel</option>
                    <option value="Mixed">Mixed</option>
                    <option value="Not sure">Not sure</option>
                  </select>
                </div>
              </div>
            </div>

            {/* SECTION F: SENSORY / BEHAVIORAL CONTEXT */}
            <div style={{ marginBottom: '1.75rem' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--primary)', marginBottom: '0.75rem' }}>
                F. Sensory / Environmental Context
              </h3>
              <label className="form-label" style={{ marginBottom: '0.5rem' }}>
                Are there situations where the child becomes uncomfortable? (Select all that apply)
              </label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.6rem' }}>
                {SENSORY_OPTIONS.map(opt => {
                  const isSelected = (formData.sensory_context || []).includes(opt);
                  return (
                    <button
                      key={opt}
                      type="button"
                      disabled={!isEditing}
                      onClick={() => handleSensoryToggle(opt)}
                      style={{
                        padding: '0.4rem 0.85rem',
                        borderRadius: '20px',
                        fontSize: '0.85rem',
                        fontWeight: 600,
                        border: isSelected ? '1px solid var(--primary)' : '1px solid var(--border-color)',
                        background: isSelected ? 'rgba(59, 130, 246, 0.15)' : 'var(--bg-metric-card)',
                        color: isSelected ? 'var(--primary)' : 'var(--text-main)',
                        cursor: isEditing ? 'pointer' : 'default',
                        transition: 'all 0.2s ease'
                      }}
                    >
                      {isSelected ? '✓ ' : ''}{opt}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* SECTION G: PARENT OBSERVATIONS */}
            <div style={{ marginBottom: '1.75rem' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--primary)', marginBottom: '0.75rem' }}>
                G. Parent Observations
              </h3>
              <div className="form-group">
                <label className="form-label">
                  Anything else you would like the assessment team to know about the child's typical behavior?
                </label>
                <textarea
                  className="form-textarea"
                  rows="3"
                  placeholder="Optional parent notes or typical behavioral routines"
                  disabled={!isEditing}
                  value={formData.parent_observations}
                  onChange={e => setFormData({ ...formData, parent_observations: e.target.value })}
                ></textarea>
              </div>
            </div>

            {/* SECTION H: SESSION CONTEXT */}
            <div style={{ marginBottom: '1.75rem' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--primary)', marginBottom: '0.75rem' }}>
                H. Assessment Session Context
              </h3>
              <div className="form-group">
                <label className="form-label">Parent-reported state for assessment sessions:</label>
                <select 
                  className="form-select"
                  disabled={!isEditing}
                  value={formData.session_context}
                  onChange={e => setFormData({ ...formData, session_context: e.target.value })}
                >
                  <option value="">Select option...</option>
                  <option value="Typical day">Typical day</option>
                  <option value="Tired">Tired</option>
                  <option value="Excited">Excited</option>
                  <option value="Unwell">Unwell</option>
                  <option value="Unusual environment">Unusual environment</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>

            {/* Actions */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
              <button 
                type="button"
                className="btn-secondary"
                disabled={saving}
                onClick={onClose}
              >
                Cancel
              </button>

              {!isEditing ? (
                <button 
                  type="button"
                  className="btn-primary"
                  onClick={() => setIsEditing(true)}
                >
                  <Edit3 size={16} />
                  <span>Edit Questionnaire</span>
                </button>
              ) : (
                <button 
                  type="submit"
                  className="btn-primary"
                  disabled={saving}
                >
                  <Save size={16} />
                  <span>{saving ? 'Saving Questionnaire...' : 'Save Questionnaire'}</span>
                </button>
              )}
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
