import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../app/store';
import { updateField, setFormData, setLoading } from '../features/interaction/interactionSlice';
import { Send, User, Calendar, Clock, Users, MessageSquare, FileText, Package, Smile, Target, CheckCircle } from 'lucide-react';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

const LogInteractionScreen: React.FC = () => {
  const dispatch = useDispatch();
  const formData = useSelector((state: RootState) => state.interaction);
  const [chatInput, setChatInput] = useState('');
  const [chatMessages, setChatMessages] = useState<Array<{role: string; content: string}>>([]);
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const handleFieldChange = (field: string, value: string) => {
    dispatch(updateField({ field: field as any, value }));
  };

  const sendChatMessage = async () => {
    if (!chatInput.trim()) return;

    const userMessage = chatInput;
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setChatInput('');
    setIsTyping(true);
    dispatch(setLoading(true));

    try {
      const response = await axios.post(`${API_URL}/interactions/chat`, {
        message: userMessage,
        history: chatMessages
      });

      const extractedData = response.data.extracted_data;
      if (extractedData) {
        const updates: any = {};
        if (extractedData.hcp_name) updates.hcp_name = extractedData.hcp_name;
        if (extractedData.interaction_type) updates.interaction_type = extractedData.interaction_type;
        if (extractedData.date) updates.date = extractedData.date;
        if (extractedData.time) updates.time = extractedData.time;
        if (extractedData.attendees) updates.attendees = extractedData.attendees;
        if (extractedData.topics_discussed) updates.topics_discussed = extractedData.topics_discussed;
        if (extractedData.summary) updates.summary = extractedData.summary;
        if (extractedData.materials_shared) updates.materials_shared = extractedData.materials_shared;
        if (extractedData.samples_distributed) updates.samples_distributed = extractedData.samples_distributed;
        if (extractedData.sentiment) updates.sentiment = extractedData.sentiment;
        if (extractedData.outcomes) updates.outcomes = extractedData.outcomes;
        
        dispatch(setFormData(updates));
      }

      setChatMessages(prev => [...prev, { role: 'assistant', content: response.data.response }]);
    } catch (error) {
      console.error('Chat error:', error);
      setChatMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }]);
    } finally {
      setIsTyping(false);
      dispatch(setLoading(false));
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChatMessage();
    }
  };

  const saveInteraction = async () => {
    try {
      dispatch(setLoading(true));
      await axios.post(`${API_URL}/interactions/chat`, {
        message: `Meeting with ${formData.hcp_name}. Discussed: ${formData.topics_discussed}. Sentiment: ${formData.sentiment}. Materials: ${formData.materials_shared}`,
        history: []
      });
      alert('✅ Interaction saved successfully!');
    } catch (error) {
      alert('❌ Error saving interaction');
    } finally {
      dispatch(setLoading(false));
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', fontFamily: "'Inter', sans-serif", backgroundColor: '#f9fafb' }}>
      {/* Left Side - Form */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '32px', backgroundColor: '#fff' }}>
        <h1 style={{ fontSize: '24px', fontWeight: '600', marginBottom: '32px' }}>Log HCP Interaction</h1>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div>
            <label style={{ fontSize: '14px', fontWeight: '500', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
              <User size={16} /> HCP Name
            </label>
            <input type="text" style={{ width: '100%', padding: '10px 12px', border: '1px solid #d1d5db', borderRadius: '8px' }} 
              value={formData.hcp_name} onChange={(e) => handleFieldChange('hcp_name', e.target.value)} />
          </div>

          <div>
            <label style={{ fontSize: '14px', fontWeight: '500', marginBottom: '6px', display: 'block' }}>Interaction Type</label>
            <select style={{ width: '100%', padding: '10px 12px', border: '1px solid #d1d5db', borderRadius: '8px' }}
              value={formData.interaction_type} onChange={(e) => handleFieldChange('interaction_type', e.target.value)}>
              <option>Meeting</option><option>Call</option><option>Email</option><option>Conference</option>
            </select>
          </div>

          <div style={{ display: 'flex', gap: '16px' }}>
            <div style={{ flex: 1 }}>
              <label style={{ fontSize: '14px', fontWeight: '500', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                <Calendar size={16} /> Date
              </label>
              <input type="date" style={{ width: '100%', padding: '10px 12px', border: '1px solid #d1d5db', borderRadius: '8px' }}
                value={formData.date} onChange={(e) => handleFieldChange('date', e.target.value)} />
            </div>
            <div style={{ flex: 1 }}>
              <label style={{ fontSize: '14px', fontWeight: '500', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                <Clock size={16} /> Time
              </label>
              <input type="time" style={{ width: '100%', padding: '10px 12px', border: '1px solid #d1d5db', borderRadius: '8px' }}
                value={formData.time} onChange={(e) => handleFieldChange('time', e.target.value)} />
            </div>
          </div>

          <div>
            <label style={{ fontSize: '14px', fontWeight: '500', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
              <Users size={16} /> Attendees
            </label>
            <input type="text" style={{ width: '100%', padding: '10px 12px', border: '1px solid #d1d5db', borderRadius: '8px' }}
              value={formData.attendees} onChange={(e) => handleFieldChange('attendees', e.target.value)} />
          </div>

          <div>
            <label style={{ fontSize: '14px', fontWeight: '500', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
              <MessageSquare size={16} /> Topics Discussed
            </label>
            <textarea rows={3} style={{ width: '100%', padding: '10px 12px', border: '1px solid #d1d5db', borderRadius: '8px' }}
              value={formData.topics_discussed} onChange={(e) => handleFieldChange('topics_discussed', e.target.value)} />
          </div>

          <div>
            <label style={{ fontSize: '14px', fontWeight: '500', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
              <FileText size={16} /> Summary
            </label>
            <textarea rows={2} style={{ width: '100%', padding: '10px 12px', border: '1px solid #d1d5db', borderRadius: '8px' }}
              value={formData.summary} onChange={(e) => handleFieldChange('summary', e.target.value)} />
          </div>

          <div>
            <label style={{ fontSize: '14px', fontWeight: '500', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
              <Package size={16} /> Materials Shared
            </label>
            <input type="text" style={{ width: '100%', padding: '10px 12px', border: '1px solid #d1d5db', borderRadius: '8px' }}
              value={formData.materials_shared} onChange={(e) => handleFieldChange('materials_shared', e.target.value)} />
          </div>

          <div>
            <label style={{ fontSize: '14px', fontWeight: '500', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
              <Smile size={16} /> HCP Sentiment
            </label>
            <div style={{ display: 'flex', gap: '20px' }}>
              {['Positive', 'Neutral', 'Negative'].map(sentiment => (
                <label key={sentiment} style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
                  <input type="radio" name="sentiment" value={sentiment} checked={formData.sentiment === sentiment}
                    onChange={(e) => handleFieldChange('sentiment', e.target.value)} />
                  <span style={{ color: sentiment === 'Positive' ? '#10b981' : sentiment === 'Negative' ? '#ef4444' : '#6b7280' }}>
                    {sentiment === 'Positive' ? '😊' : sentiment === 'Negative' ? '😞' : '😐'} {sentiment}
                  </span>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label style={{ fontSize: '14px', fontWeight: '500', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
              <Target size={16} /> Outcomes
            </label>
            <textarea rows={2} style={{ width: '100%', padding: '10px 12px', border: '1px solid #d1d5db', borderRadius: '8px' }}
              value={formData.outcomes} onChange={(e) => handleFieldChange('outcomes', e.target.value)} />
          </div>

          <button onClick={saveInteraction} disabled={formData.loading}
            style={{ backgroundColor: '#6366f1', color: '#fff', padding: '12px 24px', border: 'none', borderRadius: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
            <CheckCircle size={18} /> {formData.loading ? 'Saving...' : 'Save Interaction'}
          </button>
        </div>
      </div>

      {/* Right Side - AI Chat Assistant */}
      <div style={{ width: '400px', display: 'flex', flexDirection: 'column', backgroundColor: '#fff', borderLeft: '1px solid #e5e7eb' }}>
        <div style={{ padding: '20px', borderBottom: '1px solid #e5e7eb' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ fontSize: '32px' }}>🤖</div>
            <div>
              <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '600' }}>AI Assistant</h3>
              <p style={{ margin: '4px 0 0', fontSize: '12px', color: '#6b7280' }}>Log Interaction details here via chat</p>
            </div>
          </div>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {chatMessages.length === 0 && (
            <div style={{ backgroundColor: '#f3f4f6', padding: '16px', borderRadius: '8px', textAlign: 'center', color: '#6b7280', fontSize: '14px' }}>
              <p>Log interaction details here (e.g., "Met Dr. Smith, discussed Product X efficacy, positive sentiment, shared brochure") or ask for help.</p>
            </div>
          )}
          
          {chatMessages.map((msg, idx) => (
            <div key={idx} style={{
              padding: '10px 14px',
              borderRadius: '12px',
              maxWidth: '85%',
              fontSize: '14px',
              ...(msg.role === 'user' 
                ? { backgroundColor: '#6366f1', color: '#fff', alignSelf: 'flex-end' }
                : { backgroundColor: '#f3f4f6', color: '#111827', alignSelf: 'flex-start' })
            }}>
              <strong>{msg.role === 'user' ? 'You' : 'AI'}:</strong> {msg.content}
            </div>
          ))}
          
          {isTyping && (
            <div style={{ display: 'flex', gap: '4px', padding: '10px 14px', backgroundColor: '#f3f4f6', borderRadius: '12px', width: '50px' }}>
              <span>●</span><span>●</span><span>●</span>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        <div style={{ padding: '20px', borderTop: '1px solid #e5e7eb', display: 'flex', gap: '12px' }}>
          <textarea
            style={{ flex: 1, padding: '10px 12px', border: '1px solid #d1d5db', borderRadius: '8px', fontSize: '14px', fontFamily: 'inherit', resize: 'none' }}
            placeholder="Describe Interaction..."
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyPress={handleKeyPress}
            rows={2}
          />
          <button onClick={sendChatMessage} style={{ backgroundColor: '#6366f1', color: '#fff', border: 'none', borderRadius: '8px', width: '40px', cursor: 'pointer' }}>
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default LogInteractionScreen;