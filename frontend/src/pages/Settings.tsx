import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useStore } from '../store/useStore';
import { settingsAPI, UserSettings } from '../services/api';

export default function Settings() {
  const navigate = useNavigate();
  const { user } = useStore();

  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<'ai' | 'learning' | 'ui'>('ai');
  const [saveMessage, setSaveMessage] = useState('');

  useEffect(() => {
    if (user) {
      loadSettings();
    }
  }, [user]);

  const loadSettings = async () => {
    if (!user) return;

    setIsLoading(true);
    try {
      const data = await settingsAPI.getSettings(user.user_id);
      setSettings(data);
    } catch (error) {
      console.error('Error loading settings:', error);
      alert('Error loading settings');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (!user || !settings) return;

    setIsSaving(true);
    setSaveMessage('');

    try {
      const updated = await settingsAPI.updateSettings(user.user_id, settings);
      setSettings(updated);
      setSaveMessage('✅ Settings saved successfully!');
      setTimeout(() => setSaveMessage(''), 3000);
    } catch (error) {
      console.error('Error saving settings:', error);
      setSaveMessage('❌ Error saving settings');
      setTimeout(() => setSaveMessage(''), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  const updateSetting = (field: keyof UserSettings, value: any) => {
    if (!settings) return;
    setSettings({ ...settings, [field]: value });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-gray-900">Loading settings...</div>
      </div>
    );
  }

  if (!settings) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-gray-900">No settings found</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
            <p className="text-gray-600 mt-1">Manage your learning preferences and AI configuration</p>
          </div>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
          >
            Back to Dashboard
          </button>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-md mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('ai')}
                className={`py-4 px-6 font-medium text-sm ${
                  activeTab === 'ai'
                    ? 'border-b-2 border-blue-500 text-blue-600'
                    : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                🤖 AI Providers
              </button>
              <button
                onClick={() => setActiveTab('learning')}
                className={`py-4 px-6 font-medium text-sm ${
                  activeTab === 'learning'
                    ? 'border-b-2 border-blue-500 text-blue-600'
                    : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                📚 Learning Preferences
              </button>
              <button
                onClick={() => setActiveTab('ui')}
                className={`py-4 px-6 font-medium text-sm ${
                  activeTab === 'ui'
                    ? 'border-b-2 border-blue-500 text-blue-600'
                    : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                🎨 Appearance
              </button>
            </nav>
          </div>

          <div className="p-6">
            {/* AI Providers Tab */}
            {activeTab === 'ai' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Provider Configuration</h3>
                  <p className="text-sm text-gray-600 mb-6">
                    Configure your AI provider API keys and models. Settings saved here override defaults from .env file.
                  </p>
                </div>

                {/* Preferred Provider */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Preferred Provider
                  </label>
                  <select
                    value={settings.preferred_provider || ''}
                    onChange={(e) => updateSetting('preferred_provider', e.target.value || null)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Auto-select based on task</option>
                    <option value="anthropic">Anthropic (Claude)</option>
                    <option value="openai">OpenAI (GPT)</option>
                    <option value="google">Google (Gemini)</option>
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    Leave as "Auto-select" to let the system choose the best AI for each task
                  </p>
                </div>

                {/* Anthropic Settings */}
                <div className="border-t pt-6">
                  <h4 className="font-semibold text-gray-900 mb-4">Anthropic (Claude)</h4>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        API Key
                      </label>
                      <input
                        type="password"
                        value={settings.anthropic_api_key || ''}
                        onChange={(e) => updateSetting('anthropic_api_key', e.target.value)}
                        placeholder="sk-ant-..."
                        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Model
                      </label>
                      <select
                        value={settings.anthropic_model}
                        onChange={(e) => updateSetting('anthropic_model', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="claude-sonnet-4-5-20250929">Claude Sonnet 4.5 (Recommended)</option>
                        <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</option>
                        <option value="claude-3-opus-20240229">Claude 3 Opus</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* OpenAI Settings */}
                <div className="border-t pt-6">
                  <h4 className="font-semibold text-gray-900 mb-4">OpenAI (GPT)</h4>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        API Key
                      </label>
                      <input
                        type="password"
                        value={settings.openai_api_key || ''}
                        onChange={(e) => updateSetting('openai_api_key', e.target.value)}
                        placeholder="sk-..."
                        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Model
                      </label>
                      <select
                        value={settings.openai_model}
                        onChange={(e) => updateSetting('openai_model', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="gpt-4o-mini">GPT-4o Mini (Fast & Affordable)</option>
                        <option value="gpt-4o">GPT-4o</option>
                        <option value="gpt-4-turbo">GPT-4 Turbo</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Google Settings */}
                <div className="border-t pt-6">
                  <h4 className="font-semibold text-gray-900 mb-4">Google (Gemini)</h4>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        API Key
                      </label>
                      <input
                        type="password"
                        value={settings.google_api_key || ''}
                        onChange={(e) => updateSetting('google_api_key', e.target.value)}
                        placeholder="AI..."
                        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Model
                      </label>
                      <select
                        value={settings.google_model}
                        onChange={(e) => updateSetting('google_model', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="gemini-2.0-flash-exp">Gemini 2.0 Flash (Experimental)</option>
                        <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                        <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Learning Preferences Tab */}
            {activeTab === 'learning' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Learning Preferences</h3>
                  <p className="text-sm text-gray-600 mb-6">
                    Customize how you learn and interact with the system.
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Default Learning Modality
                  </label>
                  <select
                    value={settings.default_modality || ''}
                    onChange={(e) => updateSetting('default_modality', e.target.value || null)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Auto-discover my learning style</option>
                    <option value="narrative_story">Narrative Stories</option>
                    <option value="interactive_hands_on">Interactive Hands-On</option>
                    <option value="socratic_dialogue">Socratic Dialogue</option>
                    <option value="visual_diagrams">Visual Diagrams</option>
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    Leave as "Auto-discover" to let the system learn your optimal style through experimentation
                  </p>
                </div>

                <div className="flex items-center justify-between py-4 border-t">
                  <div>
                    <h4 className="font-medium text-gray-900">Session Reminders</h4>
                    <p className="text-sm text-gray-600">Get reminded to continue learning</p>
                  </div>
                  <button
                    onClick={() => updateSetting('session_reminders', !settings.session_reminders)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      settings.session_reminders ? 'bg-blue-600' : 'bg-gray-200'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        settings.session_reminders ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>

                <div className="flex items-center justify-between py-4 border-t">
                  <div>
                    <h4 className="font-medium text-gray-900">Spaced Repetition</h4>
                    <p className="text-sm text-gray-600">Use spaced repetition for better retention</p>
                  </div>
                  <button
                    onClick={() =>
                      updateSetting('spaced_repetition_enabled', !settings.spaced_repetition_enabled)
                    }
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      settings.spaced_repetition_enabled ? 'bg-blue-600' : 'bg-gray-200'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        settings.spaced_repetition_enabled ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
              </div>
            )}

            {/* UI Preferences Tab */}
            {activeTab === 'ui' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Appearance</h3>
                  <p className="text-sm text-gray-600 mb-6">Customize how the app looks.</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Theme</label>
                  <select
                    value={settings.theme}
                    onChange={(e) => updateSetting('theme', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="light">Light</option>
                    <option value="dark">Dark (Coming Soon)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Language</label>
                  <select
                    value={settings.language}
                    onChange={(e) => updateSetting('language', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="en">English</option>
                    <option value="es">Spanish (Coming Soon)</option>
                    <option value="fr">French (Coming Soon)</option>
                  </select>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Save Button */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              {saveMessage && (
                <p className={`text-sm ${saveMessage.includes('✅') ? 'text-green-600' : 'text-red-600'}`}>
                  {saveMessage}
                </p>
              )}
            </div>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {isSaving ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
