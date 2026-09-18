import React, { useState, useEffect } from 'react';
import { Video, UploadCloud, Play, AlertTriangle, FileVideo, Cpu, RefreshCw, UserPlus } from 'lucide-react';

export default function NewSession({
  childrenList,
  childrenLoading,
  childrenError,
  onRetryChildren,
  onOpenCreateChild,
  tasksList,
  onCreateSession,
  onUploadRecording,
  onAnalyzeSession,
  onComplete
}) {
  const [step, setStep] = useState(1);
  const [selectedChildId, setSelectedChildId] = useState('');
  const [selectedTaskId, setSelectedTaskId] = useState('');
  const [notes, setNotes] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  
  const [sessionObj, setSessionObj] = useState(null);
  const [recordingObj, setRecordingObj] = useState(null);
  
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');
  const [error, setError] = useState(null);

  // Auto-select initial child if list is non-empty
  useEffect(() => {
    if (childrenList && childrenList.length > 0 && !selectedChildId) {
      setSelectedChildId(childrenList[0].id);
    }
  }, [childrenList, selectedChildId]);

  // Auto-select initial task if list is non-empty
  useEffect(() => {
    if (tasksList && tasksList.length > 0 && !selectedTaskId) {
      setSelectedTaskId(tasksList[0].id);
    }
  }, [tasksList, selectedTaskId]);

  const handleStep1Submit = async (e) => {
    e.preventDefault();
    if (!selectedChildId || !selectedTaskId) {
      setError("Please select both an existing child profile and a standardized task.");
      return;
    }

    setError(null);
    setLoading(true);
    setStatusMsg('Creating behavioral session record in database...');

    try {
      const sess = await onCreateSession({
        child_id: selectedChildId,
        task_id: selectedTaskId,
        notes: notes
      });
      setSessionObj(sess);
      setStep(2); // Proceed to Video Upload
    } catch (err) {
      setError(err.message || "Failed to create session in backend.");
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUploadAndAnalyze = async () => {
    if (!selectedFile || !sessionObj) return;
    setError(null);
    setLoading(true);

    try {
      setStatusMsg('Uploading video file to backend validation gate...');
      const rec = await onUploadRecording(sessionObj.id, selectedTaskId, selectedFile);
      setRecordingObj(rec);

      setStatusMsg('Running Computer Vision (MediaPipe Face & Pose) & Feature Extraction Engine...');
      await onAnalyzeSession(sessionObj.id);

      setStatusMsg('Analysis pipeline execution complete! Loading structured behavioral report...');
      setTimeout(() => {
        onComplete(sessionObj.id);
      }, 1000);
    } catch (err) {
      setError(err.message || "Failed during video upload or analysis execution.");
      setLoading(false);
    }
  };

  const isFormValid = Boolean(selectedChildId && selectedTaskId && !childrenLoading && childrenList.length > 0);

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <h1 className="section-heading" style={{ fontSize: '1.5rem', marginBottom: '1.5rem' }}>
        <Video size={24} style={{ color: 'var(--primary)' }} />
        <span>New Behavioral Task Recording & Analysis</span>
      </h1>

      {error && (
        <div style={{ padding: '1rem', background: 'var(--badge-reassess-bg)', border: '1px solid var(--badge-reassess-border)', borderRadius: '12px', color: 'var(--badge-reassess-text)', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <AlertTriangle size={20} />
          <div>{error}</div>
        </div>
      )}

      {step === 1 && (
        <div className="card">
          <h2 className="section-heading" style={{ fontSize: '1.1rem' }}>Step 1: Session & Task Setup</h2>
          
          <form onSubmit={handleStep1Submit}>
            {/* Child Selection Dropdown */}
            <div className="form-group">
              <label className="form-label">Select Child Profile *</label>
              
              {childrenLoading ? (
                <div style={{ padding: '0.75rem 1rem', background: 'var(--bg-secondary-btn)', borderRadius: '8px', border: '1px solid var(--border-color)', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem' }}>
                  <RefreshCw size={16} className="animate-spin" />
                  <span>Loading child profiles...</span>
                </div>
              ) : childrenError ? (
                <div style={{ padding: '0.75rem 1rem', background: 'var(--badge-reassess-bg)', border: '1px solid var(--badge-reassess-border)', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--badge-reassess-text)', fontSize: '0.9rem' }}>Unable to load child profiles.</span>
                  <button type="button" className="btn-secondary" style={{ padding: '0.3rem 0.75rem', fontSize: '0.82rem' }} onClick={onRetryChildren}>
                    <RefreshCw size={14} />
                    <span>Retry</span>
                  </button>
                </div>
              ) : childrenList.length === 0 ? (
                <div style={{ padding: '1.25rem', background: 'var(--badge-medium-bg)', border: '1px solid var(--badge-medium-border)', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ color: 'var(--badge-medium-text)', fontWeight: 700, fontSize: '0.92rem' }}>No child profiles available.</div>
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '0.2rem' }}>Create a child profile to register a behavioral monitoring subject.</div>
                  </div>
                  <button type="button" className="btn-primary" style={{ padding: '0.45rem 0.9rem', fontSize: '0.85rem' }} onClick={onOpenCreateChild}>
                    <UserPlus size={14} />
                    <span>Create Child Profile</span>
                  </button>
                </div>
              ) : (
                <select 
                  className="form-select"
                  value={selectedChildId}
                  onChange={e => setSelectedChildId(e.target.value)}
                  required
                >
                  {childrenList.map(c => (
                    <option key={c.id} value={c.id}>
                      {c.external_id} ({c.age_months} months, {c.gender})
                    </option>
                  ))}
                </select>
              )}
            </div>

            {/* Task Selection Dropdown */}
            <div className="form-group">
              <label className="form-label">Standardized Task Battery *</label>
              <select 
                className="form-select"
                value={selectedTaskId}
                onChange={e => setSelectedTaskId(e.target.value)}
                required
              >
                {tasksList.map(t => (
                  <option key={t.id} value={t.id}>
                    {t.name} ({t.code.replace('_', ' ').toUpperCase()})
                  </option>
                ))}
              </select>
            </div>

            {/* Session Notes */}
            <div className="form-group">
              <label className="form-label">Session Notes</label>
              <textarea 
                className="form-textarea"
                rows="2"
                placeholder="Optional session environment or trial observations"
                value={notes}
                onChange={e => setNotes(e.target.value)}
              ></textarea>
            </div>

            {/* Submit / Proceed Button */}
            <button 
              type="submit" 
              className="btn-primary" 
              disabled={!isFormValid || loading}
            >
              {loading ? 'Initializing Session...' : 'Create Session & Continue'}
            </button>
          </form>
        </div>
      )}

      {step === 2 && (
        <div className="card">
          <h2 className="section-heading" style={{ fontSize: '1.1rem' }}>
            <FileVideo size={20} style={{ color: 'var(--primary)' }} />
            <span>Step 2: Upload Task Video Recording</span>
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
            Upload a real MP4, MOV, or AVI video recording for Session ID: <code style={{ color: 'var(--primary)', fontFamily: 'var(--font-code)' }}>{sessionObj?.id}</code>. The backend Input Quality Gate will validate blur, resolution, and face/pose visibility.
          </p>

          <label className="upload-dropzone" htmlFor="video-upload-input" style={{ display: 'block' }}>
            <UploadCloud size={48} style={{ color: 'var(--primary)', margin: '0 auto 1rem' }} />
            <div style={{ fontWeight: 700, fontSize: '1.1rem', color: 'var(--text-main)' }}>
              {selectedFile ? selectedFile.name : 'Click or drag video file here to upload'}
            </div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.4rem' }}>
              {selectedFile ? `${(selectedFile.size / (1024*1024)).toFixed(1)} MB` : 'Supported: MP4, MOV, AVI, WEBM (Max 100MB)'}
            </div>
            <input 
              id="video-upload-input" 
              type="file" 
              accept="video/*"
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />
          </label>

          {loading && (
            <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'var(--bg-upload-hover)', borderRadius: '12px', border: '1px solid var(--border-glow)', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <Cpu className="animate-spin" size={24} style={{ color: 'var(--primary)' }} />
              <div style={{ fontWeight: 600, color: 'var(--primary)', fontSize: '0.92rem' }}>
                {statusMsg}
              </div>
            </div>
          )}

          <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
            <button 
              className="btn-primary" 
              disabled={!selectedFile || loading}
              onClick={handleUploadAndAnalyze}
            >
              <Play size={18} />
              <span>{loading ? 'Processing Video Pipeline...' : 'Upload & Execute Pipeline'}</span>
            </button>
            <button 
              className="btn-secondary" 
              disabled={loading}
              onClick={() => setStep(1)}
            >
              Back
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
