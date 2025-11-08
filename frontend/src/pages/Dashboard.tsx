import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useStore } from '../store/useStore';
import { dynamicAPI, ConversationMessage, AssessmentResponse, contentAPI, Module } from '../services/api';

export default function Dashboard() {
  const navigate = useNavigate();
  const { user, setUser } = useStore();

  const [subject, setSubject] = useState('');
  const [isAssessing, setIsAssessing] = useState(false);
  const [conversation, setConversation] = useState<ConversationMessage[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [userAnswer, setUserAnswer] = useState('');
  const [assessment, setAssessment] = useState<AssessmentResponse | null>(null);
  const [isCreatingModule, setIsCreatingModule] = useState(false);
  const [availableModules, setAvailableModules] = useState<Module[]>([]);
  const [isLoadingModules, setIsLoadingModules] = useState(true);

  // Load available modules on component mount
  useEffect(() => {
    const loadModules = async () => {
      try {
        const modules = await contentAPI.listModules();
        setAvailableModules(modules);
      } catch (error) {
        console.error('Error loading modules:', error);
      } finally {
        setIsLoadingModules(false);
      }
    };

    loadModules();
  }, []);

  const handleStartLearning = async () => {
    if (!subject.trim() || !user) return;

    setIsAssessing(true);
    setConversation([]);

    try {
      const response = await dynamicAPI.startAssessment(user.user_id, subject);
      setCurrentQuestion(response.question || '');
      setAssessment(response);
    } catch (error) {
      console.error('Error starting assessment:', error);
      alert('Error starting assessment. Make sure backend is running with valid API key.');
      setIsAssessing(false);
    }
  };

  const handleSendAnswer = async () => {
    if (!userAnswer.trim() || !user || !currentQuestion) return;

    // Add user's answer to conversation
    const newConversation: ConversationMessage[] = [
      ...conversation,
      { role: 'assistant', content: currentQuestion },
      { role: 'user', content: userAnswer },
    ];

    setConversation(newConversation);
    setUserAnswer('');

    try {
      const response = await dynamicAPI.continueAssessment(
        user.user_id,
        subject,
        newConversation
      );

      if (response.assessment_complete) {
        // Assessment complete!
        setAssessment(response);
        setCurrentQuestion('');
      } else {
        // Continue assessment
        setCurrentQuestion(response.question || '');
        setAssessment(response);
      }
    } catch (error) {
      console.error('Error continuing assessment:', error);
      alert('Error processing answer');
    }
  };

  const handleCreateModule = async () => {
    if (!user || !assessment || !assessment.assessment_complete) return;

    setIsCreatingModule(true);

    try {
      const module = await dynamicAPI.createModule(user.user_id, subject, {
        knowledge_level: assessment.knowledge_level,
        summary: assessment.summary,
        gaps: assessment.gaps,
        starting_point: assessment.starting_point,
        learning_objectives: assessment.learning_objectives,
      });

      // Navigate to learning session
      navigate(`/learn/${module.module_id}`);
    } catch (error) {
      console.error('Error creating module:', error);
      alert('Error creating learning module');
      setIsCreatingModule(false);
    }
  };

  const handleLogout = () => {
    setUser(null);
  };

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Welcome, {user?.username}!
            </h1>
            <p className="text-gray-600 mt-1">
              What would you like to learn today?
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => navigate('/progress')}
              className="px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
            >
              My Progress
            </button>
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
            >
              Logout
            </button>
          </div>
        </div>

        {/* Available Modules Section */}
        {!isAssessing && availableModules.length > 0 && (
          <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              📚 Available Learning Modules
            </h2>
            <p className="text-gray-600 mb-6">
              Start learning from our curated modules
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {availableModules.map((module) => (
                <div
                  key={module.module_id}
                  className="border border-gray-200 rounded-lg p-5 hover:border-blue-500 hover:shadow-md transition-all cursor-pointer"
                  onClick={() => navigate(`/learn/${module.module_id}`)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-gray-900 text-lg flex-1">
                      {module.title}
                    </h3>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full ml-2">
                      Level {module.difficulty_level}
                    </span>
                  </div>

                  <p className="text-sm text-gray-600 mb-3">
                    {module.description}
                  </p>

                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>⏱️ {module.estimated_time} min</span>
                    <span className="text-blue-600 font-medium">Start Learning →</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Main Content */}
        {!isAssessing && (
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              🎯 Learn About Anything
            </h2>
            <p className="text-gray-600 mb-6">
              Or type what you want to learn, and I'll assess your current knowledge
              and create a personalized lesson just for you.
            </p>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  What do you want to learn?
                </label>
                <input
                  type="text"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder="e.g., stock fundamentals, Warren Buffett's investing philosophy, how bonds work..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                  onKeyPress={(e) => e.key === 'Enter' && handleStartLearning()}
                />
              </div>

              <button
                onClick={handleStartLearning}
                disabled={!subject.trim()}
                className="w-full bg-blue-600 text-white py-3 rounded-md hover:bg-blue-700 transition-colors font-medium text-lg disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Start Learning
              </button>
            </div>

            <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="text-2xl mb-2">💡</div>
                <h3 className="font-semibold text-gray-900 mb-1">Knowledge Assessment</h3>
                <p className="text-sm text-gray-600">
                  We'll ask a few questions to understand what you already know
                </p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="text-2xl mb-2">🎯</div>
                <h3 className="font-semibold text-gray-900 mb-1">Personalized Content</h3>
                <p className="text-sm text-gray-600">
                  AI generates lessons that match YOUR learning style
                </p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <div className="text-2xl mb-2">📈</div>
                <h3 className="font-semibold text-gray-900 mb-1">Adaptive Learning</h3>
                <p className="text-sm text-gray-600">
                  System discovers and optimizes how you learn best
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Assessment in Progress */}
        {isAssessing && !assessment?.assessment_complete && (
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">
              Quick Knowledge Check
            </h2>
            <p className="text-gray-600 mb-6">
              Learning about: <span className="font-semibold">{subject}</span>
            </p>

            {/* Conversation History */}
            <div className="space-y-4 mb-6">
              {conversation.map((msg, idx) => (
                <div
                  key={idx}
                  className={`${
                    msg.role === 'assistant'
                      ? 'bg-blue-50 text-gray-900'
                      : 'bg-gray-50 text-gray-900'
                  } p-4 rounded-lg`}
                >
                  <div className="text-xs font-semibold text-gray-500 mb-1">
                    {msg.role === 'assistant' ? 'AI Tutor' : 'You'}
                  </div>
                  <div>{msg.content}</div>
                </div>
              ))}
            </div>

            {/* Current Question */}
            {currentQuestion && (
              <div className="mb-6">
                <div className="bg-blue-50 p-4 rounded-lg mb-4">
                  <div className="text-xs font-semibold text-gray-500 mb-1">
                    AI Tutor
                  </div>
                  <div className="text-gray-900">{currentQuestion}</div>
                </div>

                <div className="space-y-3">
                  <textarea
                    value={userAnswer}
                    onChange={(e) => setUserAnswer(e.target.value)}
                    placeholder="Type your answer here..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                    rows={3}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSendAnswer();
                      }
                    }}
                  />
                  <button
                    onClick={handleSendAnswer}
                    disabled={!userAnswer.trim()}
                    className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition-colors font-medium disabled:bg-gray-300 disabled:cursor-not-allowed"
                  >
                    Send Answer
                  </button>
                </div>
              </div>
            )}

            <div className="text-sm text-gray-500 text-center">
              Question {assessment?.questions_asked || 1} of 3
            </div>
          </div>
        )}

        {/* Assessment Complete */}
        {assessment?.assessment_complete && (
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">
              Assessment Complete! 🎉
            </h2>
            <p className="text-gray-600 mb-6">
              Subject: <span className="font-semibold">{subject}</span>
            </p>

            <div className="space-y-6">
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Your Current Level</h3>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-blue-600 h-3 rounded-full"
                      style={{ width: `${(assessment.knowledge_level || 1) * 20}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-700">
                    Level {assessment.knowledge_level}/5
                  </span>
                </div>
                <p className="text-sm text-gray-600 mt-2">{assessment.summary}</p>
              </div>

              <div>
                <h3 className="font-semibold text-gray-900 mb-2">What You'll Learn</h3>
                <ul className="space-y-2">
                  {assessment.learning_objectives?.map((obj, idx) => (
                    <li key={idx} className="flex items-start">
                      <span className="text-green-600 mr-2">✓</span>
                      <span className="text-gray-700">{obj}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Starting Point</h3>
                <p className="text-gray-700">{assessment.starting_point}</p>
              </div>

              <button
                onClick={handleCreateModule}
                disabled={isCreatingModule}
                className="w-full bg-green-600 text-white py-3 rounded-md hover:bg-green-700 transition-colors font-medium text-lg disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                {isCreatingModule ? 'Creating Your Lesson...' : 'Start My Personalized Lesson'}
              </button>

              <button
                onClick={() => {
                  setIsAssessing(false);
                  setAssessment(null);
                  setConversation([]);
                  setSubject('');
                }}
                className="w-full text-gray-600 py-2 hover:bg-gray-100 rounded-md transition-colors"
              >
                Learn Something Else
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
