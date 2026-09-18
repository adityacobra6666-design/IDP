import React, { useState, useEffect } from 'react';
import { fetchSessionResults } from '../api';
import { ArrowLeft, AlertOctagon, Cpu, Activity, Layers } from 'lucide-react';

export default function SessionDetail({ sessionId, onBack }) {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFrame, setSelectedFrame] = useState(null);

  useEffect(() => {
    async function loadResults() {
      try {
        setLoading(true);
        const data = await fetchSessionResults(sessionId);
        setResults(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    if (sessionId) {
      loadResults();
    }
  }, [sessionId]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem 1rem' }}>
        <Cpu className="animate-spin" size={40} style={{ margin: '0 auto 1rem', color: 'var(--primary)' }} />
        <div style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-main)' }}>
          Retrieving Analysis Results from Backend Database...
        </div>
      </div>
    );
  }

  if (error || !results) {
    return (
      <div className="card" style={{ borderColor: 'var(--badge-reassess-border)' }}>
        <h2 className="section-heading" style={{ color: 'var(--badge-reassess-text)' }}>Error Loading Results</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>{error || 'No analysis data found.'}</p>
        <button className="btn-secondary" onClick={onBack}>
          <ArrowLeft size={16} />
          <span>Back to Dashboard</span>
        </button>
      </div>
    );
  }

  const { quality, features, confidence, warnings, joint_attention_summary, imitation_summary, annotated_frame_urls } = results;

  return (
    <div>
      {/* Navigation & Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <button className="btn-secondary" onClick={onBack}>
          <ArrowLeft size={16} />
          <span>Back to Dashboard</span>
        </button>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <span className="form-label" style={{ margin: 0 }}>Evidence Confidence:</span>
          <span className={`badge-level ${
            confidence.level === 'HIGH' ? 'badge-high' :
            confidence.level === 'MEDIUM' ? 'badge-medium' :
            confidence.level === 'LOW' ? 'badge-low' : 'badge-reassess'
          }`}>
            {confidence.level}
          </span>
        </div>
      </div>

      {/* Title & Task Badge */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              {results.task_code.replace('_', ' ').toUpperCase()} TASK ANALYSIS
            </div>
            <h1 className="banner-title" style={{ fontSize: '1.6rem', marginTop: '0.2rem' }}>
              {results.task_name}
            </h1>
            <div style={{ fontSize: '0.88rem', color: 'var(--text-muted)', marginTop: '0.3rem', fontFamily: 'var(--font-code)' }}>
              Session ID: {results.session_id}
            </div>
          </div>
          <div className={`badge-level ${quality.status === 'VALID' ? 'badge-high' : 'badge-reassess'}`}>
            QUALITY GATE: {quality.status}
          </div>
        </div>

        {warnings && warnings.length > 0 && (
          <div style={{ marginTop: '1.25rem', padding: '1rem', background: 'var(--badge-reassess-bg)', border: '1px solid var(--badge-reassess-border)', borderRadius: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--badge-reassess-text)', fontWeight: 700, fontSize: '0.9rem', marginBottom: '0.4rem' }}>
              <AlertOctagon size={18} />
              <span>Input Quality Gate Warnings</span>
            </div>
            <ul style={{ paddingLeft: '1.25rem', color: 'var(--text-muted)', fontSize: '0.88rem' }}>
              {warnings.map((w, i) => (
                <li key={i}>{w}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Grid: Quality Gate vs Calculated Behavioral Metrics */}
      <div className="grid-2" style={{ marginBottom: '1.5rem' }}>
        {/* Quality Gate Metrics Card */}
        <div className="card">
          <h2 className="section-heading">
            <Cpu size={20} style={{ color: 'var(--primary)' }} />
            <span>Input Quality Assessment</span>
          </h2>
          <div className="grid-2" style={{ marginBottom: '1.25rem' }}>
            <div className="metric-card">
              <div className="metric-label">Quality Score</div>
              <div className="metric-value">{quality.overall_score}%</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Blur Score (Laplacian)</div>
              <div className="metric-value" style={{ fontSize: '1.5rem' }}>{quality.blur_score}</div>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.9rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Face Landmark Visibility Ratio:</span>
              <span style={{ fontWeight: 700, color: 'var(--text-main)' }}>{(quality.face_visibility_ratio * 100).toFixed(1)}%</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Pose Landmark Visibility Ratio:</span>
              <span style={{ fontWeight: 700, color: 'var(--text-main)' }}>{(quality.pose_visibility_ratio * 100).toFixed(1)}%</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Resolution Status:</span>
              <span style={{ fontWeight: 700, color: quality.resolution_ok ? 'var(--status-high)' : 'var(--status-low)' }}>
                {quality.resolution_ok ? 'PASS' : 'FAIL'}
              </span>
            </div>
          </div>
        </div>

        {/* Task Specific Behavioral Metrics */}
        <div className="card">
          <h2 className="section-heading">
            <Activity size={20} style={{ color: 'var(--primary)' }} />
            <span>Computed Behavioral Features</span>
          </h2>

          {joint_attention_summary && (
            <div className="grid-2" style={{ gap: '1rem' }}>
              <div className="metric-card">
                <div className="metric-label">Target Orientation</div>
                <div className="metric-value">{(joint_attention_summary.target_orientation_ratio * 100).toFixed(1)}<span className="metric-unit">%</span></div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Orientation Latency</div>
                <div className="metric-value">{joint_attention_summary.orientation_latency_sec}<span className="metric-unit">s</span></div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Max Fixation Duration</div>
                <div className="metric-value">{joint_attention_summary.fixation_duration_sec}<span className="metric-unit">s</span></div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Gaze Shifts</div>
                <div className="metric-value">{joint_attention_summary.gaze_shift_count}</div>
              </div>
            </div>
          )}

          {imitation_summary && (
            <div className="grid-2" style={{ gap: '1rem' }}>
              <div className="metric-card">
                <div className="metric-label">Pose Similarity</div>
                <div className="metric-value">{(imitation_summary.pose_similarity * 100).toFixed(1)}<span className="metric-unit">%</span></div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Movement Consistency</div>
                <div className="metric-value">{(imitation_summary.movement_consistency * 100).toFixed(1)}<span className="metric-unit">%</span></div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Movement Completion</div>
                <div className="metric-value">{(imitation_summary.movement_completion_proxy * 100).toFixed(1)}<span className="metric-unit">%</span></div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Response Latency</div>
                <div className="metric-value">{imitation_summary.response_latency_sec}<span className="metric-unit">s</span></div>
              </div>
            </div>
          )}

          {!joint_attention_summary && !imitation_summary && (
            <div style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              No task-specific summary generated for this recording trial.
            </div>
          )}
        </div>
      </div>

      {/* Complete Extracted Feature Dictionary Table */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h2 className="section-heading">Extracted Feature Dictionary</h2>
        
        {(!features || features.length === 0) ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            No behavioral features computed for this trial (Quality Gate flagged insufficient evidence).
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Feature Name</th>
                <th>Computed Value</th>
                <th>Unit</th>
                <th>CV Source</th>
                <th>Validity</th>
                <th>Confidence</th>
              </tr>
            </thead>
            <tbody>
              {features.map((feat, idx) => (
                <tr key={idx}>
                  <td style={{ fontWeight: 600, fontFamily: 'var(--font-code)', color: 'var(--primary)' }}>{feat.feature_name}</td>
                  <td style={{ fontWeight: 700 }}>
                    {feat.valid ? feat.value : <span style={{ color: 'var(--text-dim)', fontStyle: 'italic' }}>Not Available</span>}
                  </td>
                  <td style={{ color: 'var(--text-muted)' }}>{feat.unit}</td>
                  <td>{feat.source}</td>
                  <td>
                    <span style={{ color: feat.valid ? 'var(--status-high)' : 'var(--status-low)', fontWeight: 600 }}>
                      {feat.valid ? 'VALID' : 'INSUFFICIENT_EVIDENCE'}
                    </span>
                  </td>
                  <td>{(feat.confidence * 100).toFixed(0)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Representative Annotated Frames Gallery */}
      {annotated_frame_urls && annotated_frame_urls.length > 0 && (
        <div className="card">
          <h2 className="section-heading">
            <Layers size={20} style={{ color: 'var(--primary)' }} />
            <span>Annotated Computer Vision Evidence Snapshots</span>
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginBottom: '1rem' }}>
            Sampled video frames showing real-time MediaPipe Face Mesh & Body Pose skeleton landmark tracking generated by OpenCV.
          </p>

          <div className="frames-gallery">
            {annotated_frame_urls.map((url, i) => (
              <img 
                key={i} 
                src={url} 
                alt={`Annotated frame ${i+1}`}
                className="frame-thumbnail"
                onClick={() => setSelectedFrame(url)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Frame Fullscreen Modal */}
      {selectedFrame && (
        <div 
          style={{ position: 'fixed', inset: 0, background: 'var(--bg-modal-backdrop)', backdropFilter: 'blur(8px)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem' }}
          onClick={() => setSelectedFrame(null)}
        >
          <div style={{ maxWidth: '900px', width: '100%', position: 'relative' }}>
            <img src={selectedFrame} alt="Annotated frame zoom" style={{ width: '100%', borderRadius: '12px', border: '2px solid var(--primary)' }} />
            <div style={{ textAlign: 'center', marginTop: '1rem', color: 'var(--text-main)', fontSize: '0.9rem' }}>
              Click anywhere to close
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
