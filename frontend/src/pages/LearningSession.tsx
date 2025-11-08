import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useStore } from '../store/useStore';
import { sessionAPI, chatAPI } from '../services/api';

export default function LearningSession() {
  const { moduleId } = useParams<{ moduleId: string }>();
  const navigate = useNavigate();
  const { user, currentSession, setCurrentSession } = useStore();

  const [isLoading, setIsLoading] = useState(true);
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<Array<{ role: string; content: string }>>([]);
  const [comprehensionScore, setComprehensionScore] = useState(0.8);
  const [engagementScore, setEngagementScore] = useState(0.8);

  useEffect(() => {
    if (moduleId && user) {
      loadSession();
    }
  }, [moduleId, user]);

  const loadSession = async () => {
    if (!moduleId || !user) return;

    setIsLoading(true);
    try {
      const session = await sessionAPI.startSession(user.user_id, moduleId);
      setCurrentSession(session);
    } catch (error) {
      console.error('Error loading session:', error);
      alert('Error starting lesson. Make sure backend is running.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!chatMessage.trim() || !currentSession) return;

    const userMessage = chatMessage;
    setChatMessage('');

    // Add to chat history
    setChatHistory([...chatHistory, { role: 'user', content: userMessage }]);

    try {
      const response = await chatAPI.sendMessage(currentSession.session_id, userMessage);
      setChatHistory((prev) => [
        ...prev,
        { role: 'assistant', content: response.response },
      ]);
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const handleComplete = async () => {
    if (!currentSession) return;

    try {
      await sessionAPI.completeSession(
        currentSession.session_id,
        comprehensionScore,
        engagementScore
      );
      navigate('/dashboard');
    } catch (error) {
      console.error('Error completing session:', error);
      alert('Error completing session');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-4">✨</div>
          <div className="text-xl font-semibold text-gray-900">
            Generating Your Personalized Lesson...
          </div>
          <div className="text-gray-600 mt-2">
            AI is creating content tailored just for you
          </div>
        </div>
      </div>
    );
  }

  if (!currentSession) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-xl text-gray-900">No active session</div>
          <button
            onClick={() => navigate('/dashboard')}
            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto p-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {currentSession.module.title}
              </h1>
              <div className="flex gap-4 mt-2 text-sm text-gray-600">
                <span>🎯 {currentSession.modality}</span>
                <span>⏱️ {currentSession.module.estimated_time} min</span>
              </div>
              <p className="text-sm text-gray-500 mt-2">
                {currentSession.selection_reason}
              </p>
            </div>
            <button
              onClick={() => navigate('/dashboard')}
              className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-md"
            >
              Exit
            </button>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Lesson Content */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Lesson Content
              </h2>
              <div className="prose max-w-none text-gray-700 whitespace-pre-wrap">
                {currentSession.content}
              </div>
            </div>
          </div>

          {/* AI Tutor Chat */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                AI Tutor
              </h2>

              {/* Chat Messages */}
              <div className="h-64 overflow-y-auto mb-4 space-y-3">
                {chatHistory.length === 0 && (
                  <div className="text-sm text-gray-500 text-center py-8">
                    Ask me anything about this lesson!
                  </div>
                )}
                {chatHistory.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`${
                      msg.role === 'user'
                        ? 'bg-blue-50 ml-4'
                        : 'bg-gray-50 mr-4'
                    } p-3 rounded-lg`}
                  >
                    <div className="text-xs font-semibold text-gray-500 mb-1">
                      {msg.role === 'user' ? 'You' : 'AI Tutor'}
                    </div>
                    <div className="text-sm text-gray-900">{msg.content}</div>
                  </div>
                ))}
              </div>

              {/* Chat Input */}
              <div className="space-y-2">
                <textarea
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  placeholder="Ask a question..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm resize-none"
                  rows={2}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage();
                    }
                  }}
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!chatMessage.trim()}
                  className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition-colors text-sm disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  Ask
                </button>
              </div>
            </div>

            {/* Complete Session */}
            <div className="bg-white rounded-lg shadow-md p-6 mt-6">
              <h3 className="font-semibold text-gray-900 mb-3">
                Finish Lesson
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                How well did you understand this lesson?
              </p>
              <button
                onClick={handleComplete}
                className="w-full bg-green-600 text-white py-2 rounded-md hover:bg-green-700 transition-colors"
              >
                Complete Lesson
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
