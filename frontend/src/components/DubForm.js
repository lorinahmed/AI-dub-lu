import React, { useState } from 'react';
import { Play, Globe, Loader2 } from 'lucide-react';

const DubForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    youtube_url: '',
    target_language: 'es',
    source_language: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const languages = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh': 'Chinese',
    'hi': 'Hindi',
    'ar': 'Arabic',
    'nl': 'Dutch',
    'sv': 'Swedish',
    'no': 'Norwegian',
    'da': 'Danish',
    'fi': 'Finnish',
    'pl': 'Polish',
    'tr': 'Turkish',
    'he': 'Hebrew',
    'th': 'Thai',
    'vi': 'Vietnamese',
    'id': 'Indonesian',
    'ms': 'Malay',
    'tl': 'Filipino',
    'bn': 'Bengali',
    'ur': 'Urdu',
    'fa': 'Persian',
    'uk': 'Ukrainian',
    'cs': 'Czech',
    'sk': 'Slovak',
    'hu': 'Hungarian',
    'ro': 'Romanian',
    'bg': 'Bulgarian',
    'hr': 'Croatian',
    'sr': 'Serbian',
    'sl': 'Slovenian',
    'et': 'Estonian',
    'lv': 'Latvian',
    'lt': 'Lithuanian',
    'el': 'Greek',
    'is': 'Icelandic',
    'mt': 'Maltese',
    'ga': 'Irish',
    'cy': 'Welsh',
    'eu': 'Basque',
    'ca': 'Catalan',
    'gl': 'Galician',
    'sq': 'Albanian',
    'mk': 'Macedonian',
    'bs': 'Bosnian',
    'me': 'Montenegrin',
    'ka': 'Georgian',
    'hy': 'Armenian',
    'az': 'Azerbaijani',
    'kk': 'Kazakh',
    'ky': 'Kyrgyz',
    'uz': 'Uzbek',
    'tk': 'Turkmen',
    'mn': 'Mongolian',
    'ne': 'Nepali',
    'si': 'Sinhala',
    'my': 'Burmese',
    'km': 'Khmer',
    'lo': 'Lao',
    'am': 'Amharic',
    'sw': 'Swahili',
    'zu': 'Zulu',
    'af': 'Afrikaans',
    'xh': 'Xhosa',
    'yo': 'Yoruba',
    'ig': 'Igbo',
    'ha': 'Hausa',
    'so': 'Somali',
    'rw': 'Kinyarwanda',
    'mg': 'Malagasy',
    'st': 'Sesotho',
    'sn': 'Shona',
    'ny': 'Chichewa',
    'lg': 'Luganda',
    'ak': 'Akan',
    'tw': 'Twi',
    'ee': 'Ewe',
    'fon': 'Fon',
    'wo': 'Wolof',
    'ff': 'Fula',
    'bm': 'Bambara',
    'dy': 'Dyula',
    'sg': 'Sango',
    'ln': 'Lingala',
    'kg': 'Kongo',
    'sw': 'Swahili',
    'rw': 'Kinyarwanda',
    'lg': 'Luganda',
    'ak': 'Akan',
    'tw': 'Twi',
    'ee': 'Ewe',
    'fon': 'Fon',
    'wo': 'Wolof',
    'ff': 'Fula',
    'bm': 'Bambara',
    'dy': 'Dyula',
    'sg': 'Sango',
    'ln': 'Lingala',
    'kg': 'Kongo'
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // Validate YouTube URL
      if (!formData.youtube_url.includes('youtube.com') && !formData.youtube_url.includes('youtu.be')) {
        throw new Error('Please enter a valid YouTube URL');
      }

      await onSubmit(formData);
      setFormData({ youtube_url: '', target_language: 'es', source_language: '' });
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-indigo-100 rounded-full mb-4">
          <Play className="h-8 w-8 text-indigo-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Start Dubbing
        </h2>
        <p className="text-gray-600">
          Enter a YouTube URL and select your target language
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* YouTube URL Input */}
        <div>
          <label htmlFor="youtube_url" className="block text-sm font-medium text-gray-700 mb-2">
            YouTube Video URL
          </label>
          <input
            type="url"
            id="youtube_url"
            name="youtube_url"
            value={formData.youtube_url}
            onChange={handleInputChange}
            placeholder="https://www.youtube.com/watch?v=..."
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
            required
          />
        </div>

        {/* Target Language Selection */}
        <div>
          <label htmlFor="target_language" className="block text-sm font-medium text-gray-700 mb-2">
            Target Language
          </label>
          <div className="relative">
            <select
              id="target_language"
              name="target_language"
              value={formData.target_language}
              onChange={handleInputChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors appearance-none bg-white"
              required
            >
              {Object.entries(languages).map(([code, name]) => (
                <option key={code} value={code}>
                  {name}
                </option>
              ))}
            </select>
            <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
              <Globe className="h-5 w-5 text-gray-400" />
            </div>
          </div>
        </div>

        {/* Source Language (Optional) */}
        <div>
          <label htmlFor="source_language" className="block text-sm font-medium text-gray-700 mb-2">
            Source Language (Optional - Auto-detect if left empty)
          </label>
          <div className="relative">
            <select
              id="source_language"
              name="source_language"
              value={formData.source_language}
              onChange={handleInputChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors appearance-none bg-white"
            >
              <option value="">Auto-detect</option>
              {Object.entries(languages).map(([code, name]) => (
                <option key={code} value={code}>
                  {name}
                </option>
              ))}
            </select>
            <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
              <Globe className="h-5 w-5 text-gray-400" />
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        >
          {isLoading ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin" />
              <span>Processing...</span>
            </>
          ) : (
            <>
              <Play className="h-5 w-5" />
              <span>Start AI Dubbing</span>
            </>
          )}
        </button>
      </form>

      {/* Info Section */}
      <div className="mt-8 p-4 bg-blue-50 rounded-lg">
        <h3 className="text-sm font-medium text-blue-900 mb-2">How AI dubbing works:</h3>
        <ol className="text-sm text-blue-800 space-y-1">
          <li>1. Download the YouTube video</li>
          <li>2. Extract and analyze audio with speaker diarization</li>
          <li>3. Transcribe and translate with timing awareness</li>
          <li>4. Generate natural-sounding speech with voice matching</li>
          <li>5. Synchronize the new audio with the video</li>
        </ol>
      </div>
    </div>
  );
};

export default DubForm; 