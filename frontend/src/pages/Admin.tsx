import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

// Backend API URL
const API_URL = 'http://localhost:8000';

interface LLMConfig {
  model: string;
  api_key: string;
  organization_id?: string;
  temperature: number;
  max_tokens?: number;
}

interface PromptConfig {
  name: string;
  description: string;
  prompt_template: string;
  llm_config: LLMConfig;
  version: string;
  last_modified?: string;
  modified_by?: string;
}

interface PromptConfigurations {
  analysis_prompt: PromptConfig;
  findings_prompt: PromptConfig;
}

export function AdminPage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [prompts, setPrompts] = useState<PromptConfigurations | null>(null);
  const [selectedPrompt, setSelectedPrompt] = useState<'analysis_prompt' | 'findings_prompt'>('analysis_prompt');
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('admin_token');
    if (token) {
      setIsAuthenticated(true);
      fetchPrompts(token);
    }
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_URL}/admin/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          username,
          password,
          grant_type: 'password',
        }),
      });

      if (!response.ok) throw new Error('Invalid credentials');

      const data = await response.json();
      localStorage.setItem('admin_token', data.access_token);
      setIsAuthenticated(true);
      fetchPrompts(data.access_token);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    }
  };

  const fetchPrompts = async (token: string) => {
    try {
      const response = await fetch(`${API_URL}/admin/prompts`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!response.ok) throw new Error('Failed to fetch prompts');
      const data = await response.json();
      setPrompts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch prompts');
    }
  };

  const handleUpdate = async (promptName: string, config: PromptConfig) => {
    try {
      const token = localStorage.getItem('admin_token');
      if (!token) throw new Error('Not authenticated');

      const response = await fetch(`${API_URL}/admin/prompts/${promptName}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(config),
      });

      if (!response.ok) throw new Error('Failed to update prompt');
      
      const data = await response.json();
      setPrompts(data);
      setError('Prompt updated successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Update failed');
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Admin Login
          </h2>
        </div>

        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
            <form className="space-y-6" onSubmit={handleLogin}>
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                  Username
                </label>
                <input
                  id="username"
                  type="text"
                  required
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  required
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>

              {error && (
                <div className="text-red-600 text-sm">
                  {error}
                </div>
              )}

              <button
                type="submit"
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
              >
                Sign in
              </button>
            </form>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-6 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Prompt Management
          </h1>
          <button
            onClick={() => {
              localStorage.removeItem('admin_token');
              setIsAuthenticated(false);
            }}
            className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700"
          >
            Logout
          </button>
        </div>

        {error && (
          <div className={`mb-4 p-4 rounded-md ${error.includes('success') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
            {error}
          </div>
        )}

        {prompts && (
          <div className="bg-white shadow rounded-lg">
            <div className="border-b border-gray-200">
              <nav className="flex -mb-px">
                <button
                  onClick={() => setSelectedPrompt('analysis_prompt')}
                  className={`px-6 py-4 text-sm font-medium ${
                    selectedPrompt === 'analysis_prompt'
                      ? 'border-b-2 border-blue-500 text-blue-600'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Analysis Prompt
                </button>
                <button
                  onClick={() => setSelectedPrompt('findings_prompt')}
                  className={`ml-8 px-6 py-4 text-sm font-medium ${
                    selectedPrompt === 'findings_prompt'
                      ? 'border-b-2 border-blue-500 text-blue-600'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Findings Prompt
                </button>
              </nav>
            </div>

            <div className="p-6">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleUpdate(selectedPrompt, prompts[selectedPrompt]);
                }}
                className="space-y-6"
              >
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Name
                  </label>
                  <input
                    type="text"
                    value={prompts[selectedPrompt].name}
                    onChange={(e) => {
                      const newPrompts = { ...prompts };
                      newPrompts[selectedPrompt].name = e.target.value;
                      setPrompts(newPrompts);
                    }}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Description
                  </label>
                  <input
                    type="text"
                    value={prompts[selectedPrompt].description}
                    onChange={(e) => {
                      const newPrompts = { ...prompts };
                      newPrompts[selectedPrompt].description = e.target.value;
                      setPrompts(newPrompts);
                    }}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Prompt Template
                  </label>
                  <textarea
                    value={prompts[selectedPrompt].prompt_template}
                    onChange={(e) => {
                      const newPrompts = { ...prompts };
                      newPrompts[selectedPrompt].prompt_template = e.target.value;
                      setPrompts(newPrompts);
                    }}
                    rows={10}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3"
                  />
                </div>

                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      LLM Model
                    </label>
                    <input
                      type="text"
                      value={prompts[selectedPrompt].llm_config.model}
                      onChange={(e) => {
                        const newPrompts = { ...prompts };
                        newPrompts[selectedPrompt].llm_config.model = e.target.value;
                        setPrompts(newPrompts);
                      }}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      API Key
                    </label>
                    <input
                      type="password"
                      value={prompts[selectedPrompt].llm_config.api_key}
                      onChange={(e) => {
                        const newPrompts = { ...prompts };
                        newPrompts[selectedPrompt].llm_config.api_key = e.target.value;
                        setPrompts(newPrompts);
                      }}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Temperature
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      min="0"
                      max="2"
                      value={prompts[selectedPrompt].llm_config.temperature}
                      onChange={(e) => {
                        const newPrompts = { ...prompts };
                        newPrompts[selectedPrompt].llm_config.temperature = parseFloat(e.target.value);
                        setPrompts(newPrompts);
                      }}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Max Tokens
                    </label>
                    <input
                      type="number"
                      value={prompts[selectedPrompt].llm_config.max_tokens}
                      onChange={(e) => {
                        const newPrompts = { ...prompts };
                        newPrompts[selectedPrompt].llm_config.max_tokens = parseInt(e.target.value);
                        setPrompts(newPrompts);
                      }}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3"
                    />
                  </div>
                </div>

                {prompts[selectedPrompt].last_modified && (
                  <div className="text-sm text-gray-500">
                    Last modified by {prompts[selectedPrompt].modified_by} at {new Date(prompts[selectedPrompt].last_modified).toLocaleString()}
                  </div>
                )}

                <div className="flex justify-end">
                  <button
                    type="submit"
                    className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                  >
                    Save Changes
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 