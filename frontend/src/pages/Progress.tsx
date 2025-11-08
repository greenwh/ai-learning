import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useStore } from '../store/useStore';
import { progressAPI } from '../services/api';

export default function Progress() {
  const navigate = useNavigate();
  const { user } = useStore();
  const [progress, setProgress] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (user) {
      loadProgress();
    }
  }, [user]);

  const loadProgress = async () => {
    if (!user) return;

    setIsLoading(true);
    try {
      const data = await progressAPI.getOverview(user.user_id);
      setProgress(data);
    } catch (error) {
      console.error('Error loading progress:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-gray-900">Loading your progress...</div>
      </div>
    );
  }

  const insights = progress?.learning_insights || {};
  const bestModalities = insights.best_modalities || [];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Your Learning Progress</h1>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-md"
          >
            Back to Dashboard
          </button>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-3xl font-bold text-blue-600">
              {progress?.total_sessions || 0}
            </div>
            <div className="text-gray-600 mt-1">Total Sessions</div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-3xl font-bold text-green-600">
              {progress?.modules_completed || 0}
            </div>
            <div className="text-gray-600 mt-1">Completed</div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-3xl font-bold text-purple-600">
              {progress?.modules_mastered || 0}
            </div>
            <div className="text-gray-600 mt-1">Mastered</div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-3xl font-bold text-orange-600">
              {progress?.total_time_spent || 0}
            </div>
            <div className="text-gray-600 mt-1">Minutes Learned</div>
          </div>
        </div>

        {/* Learning Style Insights */}
        {insights.status === 'discovered' && bestModalities.length > 0 ? (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              Your Learning Style
            </h2>

            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">
                  Best Teaching Methods for You
                </h3>
                <div className="space-y-3">
                  {bestModalities.map((mod: any, idx: number) => (
                    <div key={idx} className="flex items-center justify-between">
                      <div>
                        <div className="font-medium text-gray-900">
                          {mod.modality.replace('_', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}
                        </div>
                        <div className="text-sm text-gray-500">
                          {mod.sessions} sessions
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${mod.effectiveness}%` }}
                          />
                        </div>
                        <span className="text-sm font-semibold text-gray-700 w-12">
                          {mod.effectiveness}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {insights.recommendations && insights.recommendations.length > 0 && (
                <div className="mt-6">
                  <h3 className="font-semibold text-gray-900 mb-3">
                    Personalized Recommendations
                  </h3>
                  <ul className="space-y-2">
                    {insights.recommendations.map((rec: string, idx: number) => (
                      <li key={idx} className="flex items-start">
                        <span className="text-green-600 mr-2">✓</span>
                        <span className="text-gray-700">{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="bg-blue-50 rounded-lg p-6 mb-8 text-center">
            <div className="text-4xl mb-3">🔍</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Still Discovering Your Learning Style
            </h3>
            <p className="text-gray-600">
              Complete {insights.sessions_needed || 3} more lessons to unlock personalized insights!
            </p>
          </div>
        )}

        {/* No activity yet */}
        {(!progress || progress.total_sessions === 0) && (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <div className="text-6xl mb-4">📚</div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">
              Start Your Learning Journey
            </h2>
            <p className="text-gray-600 mb-6">
              Complete a few lessons and come back to see insights about your learning style!
            </p>
            <button
              onClick={() => navigate('/dashboard')}
              className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
            >
              Start Learning
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
