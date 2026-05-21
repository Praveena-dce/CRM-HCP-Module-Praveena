import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { sendChatMessage, createInteraction, updateInteraction, setCurrentInteraction, clearChatHistory } from '../store/interactionSlice';

const styles = {
  container: {
    display: 'flex',
    height: '100vh',
    fontFamily: "'Inter', sans-serif",
    backgroundColor: '#f5f7fa',
  },
  // Left panel now contains the form (swapped)
  leftPanel: {
    flex: 1,
    overflowY: 'auto',
    padding: '24px',
  },
  // Right panel now contains the chat (swapped)
  rightPanel: {
    width: '35%',
    display: 'flex',
    flexDirection: 'column',
    backgroundColor: '#fff',
    borderLeft: '1px solid #e0e4ea',
  },
  chatHeader: {
    padding: '20px',
    borderBottom: '1px solid #e0e4ea',
    backgroundColor: '#f8f9fa',
  },
  chatTitle: {
    margin: 0,
    fontSize: '18px',
    fontWeight: 600,
    color: '#1a202c',
  },
  chatSubtitle: {
    margin: '5px 0 0 0',
    fontSize: '13px',
    color: '#718096',
  },
  chatMessages: {
    flex: 1,
    overflowY: 'auto',
    padding: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  emptyChat: {
    textAlign: 'center',
    color: '#a0aec0',
    padding: '40px 20px',
    fontSize: '14px',
    lineHeight: '1.6',
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#2b6cb0',
    color: '#fff',
    padding: '12px 16px',
    borderRadius: '18px 18px 4px 18px',
    maxWidth: '85%',
    fontSize: '14px',
    lineHeight: '1.5',
  },
  aiMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#edf2f7',
    color: '#2d3748',
    padding: '12px 16px',
    borderRadius: '18px 18px 18px 4px',
    maxWidth: '85%',
    fontSize: '14px',
    lineHeight: '1.5',
  },
  chatInputContainer: {
    padding: '16px',
    borderTop: '1px solid #e0e4ea',
    display: 'flex',
    gap: '10px',
  },
  chatInput: {
    flex: 1,
    padding: '10px 14px',
    border: '1px solid #cbd5e0',
    borderRadius: '8px',
    fontSize: '14px',
    outline: 'none',
    transition: 'border-color 0.2s',
  },
  chatSendBtn: {
    padding: '10px 20px',
    backgroundColor: '#2b6cb0',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: 500,
    cursor: 'pointer',
    transition: 'background-color 0.2s',
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  formHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
  },
  formTitle: {
    margin: 0,
    fontSize: '22px',
    fontWeight: 600,
    color: '#1a202c',
  },
  buttonGroupHeader: {
    display: 'flex',
    gap: '10px',
  },
  refreshBtn: {
    padding: '8px 16px',
    backgroundColor: '#edf2f7',
    color: '#4a5568',
    border: 'none',
    borderRadius: '6px',
    fontSize: '13px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    transition: 'background-color 0.2s',
  },
  resetBtn: {
    padding: '8px 16px',
    backgroundColor: '#e2e8f0',
    color: '#4a5568',
    border: 'none',
    borderRadius: '6px',
    fontSize: '13px',
    cursor: 'pointer',
  },
  form: {
    backgroundColor: '#fff',
    padding: '24px',
    borderRadius: '12px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
  },
  formRow: {
    display: 'flex',
    gap: '16px',
    marginBottom: '16px',
  },
  formGroup: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  label: {
    fontSize: '13px',
    fontWeight: 500,
    color: '#4a5568',
  },
  input: {
    padding: '10px 12px',
    border: '1px solid #cbd5e0',
    borderRadius: '6px',
    fontSize: '14px',
    outline: 'none',
    transition: 'border-color 0.2s',
  },
  textarea: {
    padding: '10px 12px',
    border: '1px solid #cbd5e0',
    borderRadius: '6px',
    fontSize: '14px',
    outline: 'none',
    minHeight: '80px',
    resize: 'vertical',
    fontFamily: 'inherit',
  },
  voiceBtn: {
    padding: '8px 12px',
    backgroundColor: '#edf2f7',
    color: '#2d3748',
    border: 'none',
    borderRadius: '6px',
    fontSize: '13px',
    cursor: 'pointer',
    marginBottom: '16px',
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  sentimentGroup: {
    display: 'flex',
    gap: '16px',
    marginBottom: '16px',
  },
  sentimentLabel: {
    fontSize: '13px',
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    cursor: 'pointer',
  },
  buttonGroup: {
    display: 'flex',
    justifyContent: 'flex-end',
    gap: '12px',
    marginTop: '20px',
  },
  saveBtn: {
    padding: '10px 24px',
    backgroundColor: '#2f855a',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: 500,
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  logBtnIcon: {
    fontSize: '16px',
  }
};

function LogInteractionScreen() {
  const dispatch = useDispatch();
  const { currentInteraction, chatHistory, loading } = useSelector((state) => state.interactions);

  const [chatInput, setChatInput] = useState('');
  const [formData, setFormData] = useState({
    hcp_name: '',
    interaction_type: 'Meeting',
    date: '',
    time: '',
    attendees: '',
    topics_discussed: '',
    materials_shared: '',
    samples_distributed: '',
    sentiment: 'Neutral',
    outcomes: '',
  });

  useEffect(() => {
    if (currentInteraction) {
      setFormData({
        hcp_name: currentInteraction.hcp_name || '',
        interaction_type: currentInteraction.interaction_type || 'Meeting',
        date: currentInteraction.date || '',
        time: currentInteraction.time || '',
        attendees: currentInteraction.attendees || '',
        topics_discussed: currentInteraction.topics_discussed || '',
        materials_shared: currentInteraction.materials_shared || '',
        samples_distributed: currentInteraction.samples_distributed || '',
        sentiment: currentInteraction.sentiment || 'Neutral',
        outcomes: currentInteraction.outcomes || '',
      });
    }
  }, [currentInteraction]);

  const handleChatSubmit = (e) => {
    e.preventDefault();
    if (chatInput.trim()) {
      dispatch(sendChatMessage(chatInput.trim()));
      setChatInput('');
    }
  };

  const handleFormChange = (e) => {
    const { name, value, type, checked } = e.target;
    if (type === 'radio') {
      setFormData((prev) => ({ ...prev, sentiment: value }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    if (currentInteraction?.id) {
      dispatch(updateInteraction({ id: currentInteraction.id, data: formData }));
    } else {
      dispatch(createInteraction(formData));
    }
  };

  const handleReset = () => {
    dispatch(setCurrentInteraction(null));
    dispatch(clearChatHistory());
    setFormData({
      hcp_name: '',
      interaction_type: 'Meeting',
      date: '',
      time: '',
      attendees: '',
      topics_discussed: '',
      materials_shared: '',
      samples_distributed: '',
      sentiment: 'Neutral',
      outcomes: '',
    });
  };

  const handleRefresh = () => {
    // Refresh the page or re-fetch data
    window.location.reload();
  };

  return (
    <div style={styles.container}>
      {/* LEFT PANEL - Form (swapped) */}
      <div style={styles.leftPanel}>
        <div style={styles.formHeader}>
          <h2 style={styles.formTitle}>Log HCP Interaction</h2>
          <div style={styles.buttonGroupHeader}>
            <button onClick={handleRefresh} style={styles.refreshBtn}>
              🔄 Refresh
            </button>
            <button onClick={handleReset} style={styles.resetBtn}>
              New
            </button>
          </div>
        </div>
        <form onSubmit={handleFormSubmit} style={styles.form}>
          <div style={styles.formRow}>
            <div style={styles.formGroup}>
              <label style={styles.label}>HCP Name</label>
              <input
                type="text"
                name="hcp_name"
                value={formData.hcp_name}
                onChange={handleFormChange}
                style={styles.input}
                required
              />
            </div>
            <div style={styles.formGroup}>
              <label style={styles.label}>Interaction Type</label>
              <select
                name="interaction_type"
                value={formData.interaction_type}
                onChange={handleFormChange}
                style={styles.input}
              >
                <option value="Meeting">Meeting</option>
                <option value="Call">Call</option>
                <option value="Email">Email</option>
                <option value="Visit">Visit</option>
              </select>
            </div>
          </div>

          <div style={styles.formRow}>
            <div style={styles.formGroup}>
              <label style={styles.label}>Date</label>
              <input
                type="date"
                name="date"
                value={formData.date}
                onChange={handleFormChange}
                style={styles.input}
              />
            </div>
            <div style={styles.formGroup}>
              <label style={styles.label}>Time</label>
              <input
                type="time"
                name="time"
                value={formData.time}
                onChange={handleFormChange}
                style={styles.input}
              />
            </div>
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>Attendees</label>
            <input
              type="text"
              name="attendees"
              value={formData.attendees}
              onChange={handleFormChange}
              placeholder="Enter names or search..."
              style={styles.input}
            />
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>Topics Discussed</label>
            <textarea
              name="topics_discussed"
              value={formData.topics_discussed}
              onChange={handleFormChange}
              placeholder="Enter key discussion points..."
              style={styles.textarea}
            />
          </div>

          <button type="button" style={styles.voiceBtn}>
            🔊 Summarize from Voice Note (Requires Consent)
          </button>

          <div style={styles.formGroup}>
            <label style={styles.label}>Materials Shared</label>
            <input
              type="text"
              name="materials_shared"
              value={formData.materials_shared}
              onChange={handleFormChange}
              style={styles.input}
            />
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>Samples Distributed</label>
            <input
              type="text"
              name="samples_distributed"
              value={formData.samples_distributed}
              onChange={handleFormChange}
              style={styles.input}
            />
          </div>

          <div>
            <label style={styles.label}>Observed/Inferred HCP Sentiment</label>
            <div style={styles.sentimentGroup}>
              <label style={styles.sentimentLabel}>
                <input
                  type="radio"
                  name="sentiment"
                  value="Positive"
                  checked={formData.sentiment === 'Positive'}
                  onChange={handleFormChange}
                />
                😊 Positive
              </label>
              <label style={styles.sentimentLabel}>
                <input
                  type="radio"
                  name="sentiment"
                  value="Neutral"
                  checked={formData.sentiment === 'Neutral'}
                  onChange={handleFormChange}
                />
                😐 Neutral
              </label>
              <label style={styles.sentimentLabel}>
                <input
                  type="radio"
                  name="sentiment"
                  value="Negative"
                  checked={formData.sentiment === 'Negative'}
                  onChange={handleFormChange}
                />
                😟 Negative
              </label>
            </div>
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>Outcomes</label>
            <textarea
              name="outcomes"
              value={formData.outcomes}
              onChange={handleFormChange}
              placeholder="Key outcomes or agreements..."
              style={styles.textarea}
            />
          </div>

          <div style={styles.buttonGroup}>
            <button type="submit" style={styles.saveBtn} disabled={loading}>
              {loading ? 'Saving...' : (currentInteraction?.id ? 'Update Interaction' : 'Save Interaction')}
            </button>
          </div>
        </form>
      </div>

      {/* RIGHT PANEL - Chat (swapped) */}
      <div style={styles.rightPanel}>
        <div style={styles.chatHeader}>
          <h3 style={styles.chatTitle}>AI Assistant</h3>
          <p style={styles.chatSubtitle}>Log interaction via chat</p>
        </div>
        <div style={styles.chatMessages}>
          {chatHistory.length === 0 ? (
            <div style={styles.emptyChat}>
              <p>Log interaction details here (e.g., "Met Dr. Smith, discussed Product X efficacy, positive sentiment, shared brochure") or ask for help.</p>
            </div>
          ) : (
            chatHistory.map((msg, idx) => (
              <div key={idx} style={msg.type === 'user' ? styles.userMessage : styles.aiMessage}>
                {msg.text}
              </div>
            ))
          )}
        </div>
        <form onSubmit={handleChatSubmit} style={styles.chatInputContainer}>
          <input
            type="text"
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            placeholder="Describe interaction..."
            style={styles.chatInput}
            disabled={loading}
          />
          <button type="submit" style={styles.chatSendBtn} disabled={loading || !chatInput.trim()}>
            <span style={styles.logBtnIcon}>📤</span> Log
          </button>
        </form>
      </div>
    </div>
  );
}

export default LogInteractionScreen;