import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import axios from 'axios';
import { Globe, Download, Play, Loader2, CheckCircle, XCircle } from 'lucide-react';
import DubForm from './components/DubForm';
import JobStatus from './components/JobStatus';
import JobHistory from './components/JobHistory';

// Configure axios base URL
axios.defaults.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [currentJob, setCurrentJob] = useState(null);
  const [jobs, setJobs] = useState([]);

  useEffect(() => {
    // Load recent jobs on app start
    loadRecentJobs();
  }, []);

  const loadRecentJobs = async () => {
    try {
      const response = await axios.get('/jobs');
      setJobs(response.data.recent_jobs || []);
    } catch (error) {
      console.error('Failed to load recent jobs:', error);
    }
  };

  const handleDubSubmit = async (formData) => {
    try {
      const response = await axios.post('/dub', formData);
      const jobId = response.data.job_id;
      setCurrentJob({ id: jobId, ...response.data });
      loadRecentJobs(); // Refresh job list
      return jobId;
    } catch (error) {
      console.error('Failed to submit dubbing job:', error);
      throw error;
    }
  };

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-6">
              <div className="flex items-center space-x-3">
                <Globe className="h-8 w-8 text-indigo-600" />
                <h1 className="text-2xl font-bold text-gray-900">
                  YouTube Video Dubber
                </h1>
              </div>
              <nav className="flex space-x-8">
                <a href="/" className="text-gray-700 hover:text-indigo-600 font-medium">
                  Home
                </a>
                <a href="/history" className="text-gray-700 hover:text-indigo-600 font-medium">
                  History
                </a>
              </nav>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route 
              path="/" 
              element={
                <div className="space-y-8">
                  {/* Hero Section */}
                  <div className="text-center">
                    <h2 className="text-4xl font-bold text-gray-900 mb-4">
                      Dub YouTube Videos in Any Language
                    </h2>
                    <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                      Transform any YouTube video with AI-powered dubbing. 
                      Upload a video URL, select your target language, and get a professionally dubbed version.
                    </p>
                  </div>

                  {/* Main Form */}
                  <div className="max-w-2xl mx-auto">
                    <DubForm onSubmit={handleDubSubmit} />
                  </div>

                  {/* Current Job Status */}
                  {currentJob && (
                    <div className="max-w-2xl mx-auto">
                      <JobStatus jobId={currentJob.id} />
                    </div>
                  )}

                  {/* Recent Jobs */}
                  {jobs.length > 0 && (
                    <div className="max-w-4xl mx-auto">
                      <h3 className="text-2xl font-semibold text-gray-900 mb-6">
                        Recent Jobs
                      </h3>
                      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                        {jobs.slice(0, 6).map((job) => (
                          <div key={job.job_id} className="bg-white rounded-lg shadow p-6">
                            <div className="flex items-center justify-between mb-4">
                              <div className="flex items-center space-x-2">
                                {job.status === 'completed' && (
                                  <CheckCircle className="h-5 w-5 text-green-500" />
                                )}
                                {job.status === 'failed' && (
                                  <XCircle className="h-5 w-5 text-red-500" />
                                )}
                                {job.status === 'processing' && (
                                  <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />
                                )}
                                <span className="text-sm font-medium text-gray-900 capitalize">
                                  {job.status}
                                </span>
                              </div>
                              <span className="text-xs text-gray-500">
                                {new Date(job.created_at).toLocaleDateString()}
                              </span>
                            </div>
                            
                            <div className="space-y-2">
                              <p className="text-sm text-gray-600 truncate">
                                {job.youtube_url}
                              </p>
                              <p className="text-sm text-gray-500">
                                Target: {job.target_language}
                              </p>
                              {job.status === 'completed' && (
                                <button className="w-full mt-3 bg-indigo-600 text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors">
                                  <Download className="h-4 w-4 inline mr-2" />
                                  Download
                                </button>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              } 
            />
            <Route 
              path="/history" 
              element={<JobHistory />} 
            />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 mt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="text-center text-gray-600">
              <p>&copy; 2024 YouTube Video Dubber. Powered by AI.</p>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App; 