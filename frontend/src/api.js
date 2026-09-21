const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

export async function checkHealth() {
  const res = await fetch('/health');
  if (!res.ok) throw new Error('Backend health check failed');
  return res.json();
}

export async function fetchChildren() {
  const res = await fetch(`${API_BASE}/children`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to fetch children profiles');
  }
  return res.json();
}

export async function createChild(data) {
  const res = await fetch(`${API_BASE}/children`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to create child profile');
  }
  return res.json();
}

export async function deleteChild(childId) {
  const res = await fetch(`${API_BASE}/children/${childId}`, {
    method: 'DELETE'
  });
  if (!res.ok && res.status !== 204) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Unable to delete child profile.');
  }
  return true;
}

export async function fetchParentQuestionnaire(childId) {
  const res = await fetch(`${API_BASE}/children/${childId}/questionnaire`);
  if (res.status === 404) {
    return null; // Parent questionnaire not completed
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to fetch parent questionnaire');
  }
  return res.json();
}

export async function saveParentQuestionnaire(childId, questionnaireData) {
  const res = await fetch(`${API_BASE}/children/${childId}/questionnaire`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(questionnaireData)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to save parent questionnaire');
  }
  return res.json();
}

export async function fetchTasks() {
  const res = await fetch(`${API_BASE}/tasks`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to fetch task catalog');
  }
  return res.json();
}

export async function fetchSessions() {
  const res = await fetch(`${API_BASE}/sessions`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to fetch sessions');
  }
  return res.json();
}

export async function fetchSession(sessionId) {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to fetch session details');
  }
  return res.json();
}

export async function createSession(data) {
  const res = await fetch(`${API_BASE}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to create session');
  }
  return res.json();
}

export async function deleteSession(sessionId) {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}`, {
    method: 'DELETE'
  });
  if (!res.ok && res.status !== 204) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Unable to delete session. Please try again.');
  }
  return true;
}

export async function uploadRecording(sessionId, taskId, file) {
  const formData = new FormData();
  formData.append('task_id', taskId);
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/sessions/${sessionId}/recording`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to upload video recording');
  }
  return res.json();
}

export async function analyzeSession(sessionId) {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/analyze`, {
    method: 'POST'
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to process video analysis');
  }
  return res.json();
}

export async function fetchSessionResults(sessionId) {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/results`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to fetch session analysis results');
  }
  return res.json();
}
