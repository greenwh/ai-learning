import { useState } from 'react';
import { useStore } from '../store/useStore';
import { authAPI } from '../services/api';

export default function Login() {
  const [isRegistering, setIsRegistering] = useState(false);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const { setUser } = useStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      if (isRegistering) {
        const user = await authAPI.register(username, email, password);
        setUser(user);
      } else {
        const user = await authAPI.login(username, password);
        setUser(user);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            AI Personalized Learning
          </h1>
          <p className="text-gray-600">
            Discover how you learn best
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-xl p-8">
          <div className="flex gap-2 mb-6">
            <button
              onClick={() => setIsRegistering(false)}
              className={`flex-1 py-2 rounded ${
                !isRegistering
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600'
              }`}
            >
              Login
            </button>
            <button
              onClick={() => setIsRegistering(true)}
              className={`flex-1 py-2 rounded ${
                isRegistering
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600'
              }`}
            >
              Register
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>

            {isRegistering && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email (optional)
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}

            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition-colors font-medium"
            >
              {isRegistering ? 'Create Account' : 'Login'}
            </button>
          </form>
        </div>

        <div className="mt-6 text-center text-sm text-gray-600">
          <p>✨ AI will discover how YOU learn best</p>
          <p className="mt-1">📚 Start learning any subject right away</p>
        </div>
      </div>
    </div>
  );
}
