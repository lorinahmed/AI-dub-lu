import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Download, Loader2, CheckCircle, XCircle, Clock, Play } from 'lucide-react';

const JobStatus = ({ jobId }) => {
  const [job, setJob] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (jobId) {
      fetchJobStatus();
      // Poll for status updates every 2 seconds
      const interval = setInterval(fetchJobStatus, 2000);
      return () => clearInterval(interval);
    }
  }, [jobId]);

  const fetchJobStatus = async () => {
    try {
      const response = await axios.get(`/status/${jobId}`);
      setJob(response.data);
      setError('');
    } catch (err) {
      setError('Failed to fetch job status');
      console.error('Error fetching job status:', err);
    }
  };

  const handleDownload = async () => {
    try {
      const response = await axios.get(`/download/${jobId}`);
      // Create a temporary link to download the file
      const link = document.createElement('a');
      link.href = response.data.download_url;
      link.download = `dubbed_video_${jobId}.mp4`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      setError('Failed to download video');
      console.error('Error downloading video:', err);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-6 w-6 text-green-500" />;
      case 'failed':
        return <XCircle className="h-6 w-6 text-red-500" />;
      case 'processing':
      case 'downloading':
      case 'extracting_audio':
      case 'transcribing':
      case 'translating':
      case 'generating_speech':
      case 'synchronizing':
        return <Loader2 className="h-6 w-6 text-blue-500 animate-spin" />;
      default:
        return <Clock className="h-6 w-6 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'failed':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'processing':
      case 'downloading':
      case 'extracting_audio':
      case 'transcribing':
      case 'translating':
      case 'generating_speech':
      case 'synchronizing':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getStatusMessage = (status) => {
    switch (status) {
      case 'initialized':
        return 'Job initialized';
      case 'downloading':
        return 'Downloading YouTube video...';
      case 'extracting_audio':
        return 'Extracting audio from video...';
      case 'transcribing':
        return 'Transcribing audio to text...';
      case 'translating':
        return 'Translating text...';
      case 'generating_speech':
        return 'Generating speech in target language...';
      case 'synchronizing':
        return 'Synchronizing audio with video...';
      case 'completed':
        return 'Dubbing completed successfully!';
      case 'failed':
        return 'Dubbing failed';
      default:
        return 'Processing...';
    }
  };

  const getProgressSteps = () => {
    const steps = [
      { key: 'downloading', label: 'Download Video', completed: false },
      { key: 'extracting_audio', label: 'Extract Audio', completed: false },
      { key: 'transcribing', label: 'Transcribe', completed: false },
      { key: 'translating', label: 'Translate', completed: false },
      { key: 'generating_speech', label: 'Generate Speech', completed: false },
      { key: 'synchronizing', label: 'Sync Audio', completed: false },
      { key: 'completed', label: 'Complete', completed: false }
    ];

    if (!job) return steps;

    const statusOrder = ['downloading', 'extracting_audio', 'transcribing', 'translating', 'generating_speech', 'synchronizing', 'completed'];
    const currentIndex = statusOrder.indexOf(job.status);

    return steps.map((step, index) => ({
      ...step,
      completed: index <= currentIndex,
      current: index === currentIndex && job.status !== 'completed' && job.status !== 'failed'
    }));
  };

  if (!job) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-center space-x-2">
          <Loader2 className="h-5 w-5 animate-spin text-blue-500" />
          <span className="text-gray-600">Loading job status...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          {getStatusIcon(job.status)}
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Dubbing Job #{jobId.slice(0, 8)}
            </h3>
            <p className="text-sm text-gray-500">
              {new Date().toLocaleString()}
            </p>
          </div>
        </div>
        <div className={`px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(job.status)}`}>
          {job.status.replace('_', ' ').toUpperCase()}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Progress</span>
          <span>{job.progress || 0}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${job.progress || 0}%` }}
          ></div>
        </div>
      </div>

      {/* Status Message */}
      <div className="mb-6">
        <p className="text-gray-700">{getStatusMessage(job.status)}</p>
        {job.message && (
          <p className="text-sm text-gray-500 mt-1">{job.message}</p>
        )}
        {job.error && (
          <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-700">{job.error}</p>
          </div>
        )}
      </div>

      {/* Progress Steps */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-900 mb-3">Processing Steps</h4>
        <div className="space-y-2">
          {getProgressSteps().map((step, index) => (
            <div key={step.key} className="flex items-center space-x-3">
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium ${
                step.completed 
                  ? 'bg-green-500 text-white' 
                  : step.current 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-200 text-gray-500'
              }`}>
                {step.completed ? (
                  <CheckCircle className="h-4 w-4" />
                ) : step.current ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  index + 1
                )}
              </div>
              <span className={`text-sm ${
                step.completed 
                  ? 'text-green-600 font-medium' 
                  : step.current 
                    ? 'text-blue-600 font-medium' 
                    : 'text-gray-500'
              }`}>
                {step.label}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Download Button */}
      {job.status === 'completed' && (
        <div className="border-t pt-4">
          <button
            onClick={handleDownload}
            className="w-full bg-green-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-green-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors flex items-center justify-center space-x-2"
          >
            <Download className="h-5 w-5" />
            <span>Download Dubbed Video</span>
          </button>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}
    </div>
  );
};

export default JobStatus; 