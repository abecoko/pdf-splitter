import React, { useState, useCallback, useEffect } from 'react';
import { Scissors, Download, Sun, Moon, Github, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import DropZone from './components/DropZone';
import RangeInput from './components/RangeInput';
import { parsePageRanges } from './utils/parseRange';

interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export default function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [pageRanges, setPageRanges] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [darkMode, setDarkMode] = useState(false);
  const [totalPages, setTotalPages] = useState<number | undefined>(undefined);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress | null>(null);

  // Initialize dark mode from localStorage
  useEffect(() => {
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    setDarkMode(savedDarkMode);
    if (savedDarkMode) {
      document.documentElement.classList.add('dark');
    }
  }, []);

  const toggleDarkMode = useCallback(() => {
    setDarkMode(!darkMode);
    if (!darkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('darkMode', 'true');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('darkMode', 'false');
    }
  }, [darkMode]);

  const handleFileSelect = useCallback(async (file: File) => {
    setSelectedFile(file);
    setError(null);
    setSuccess(null);
    setPageRanges('');
    setTotalPages(undefined);

    // In a real application, you might want to extract page count from the PDF
    // For now, we'll skip this step as it requires additional PDF processing on the frontend
  }, []);

  const handleFileRemove = useCallback(() => {
    setSelectedFile(null);
    setPageRanges('');
    setError(null);
    setSuccess(null);
    setTotalPages(undefined);
  }, []);

  const canSplit = selectedFile && pageRanges.trim() && parsePageRanges(pageRanges).isValid;

  const handleSplit = useCallback(async () => {
    if (!selectedFile || !canSplit) return;

    setIsProcessing(true);
    setError(null);
    setSuccess(null);
    setUploadProgress(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('page_ranges', pageRanges);

      const apiUrl = import.meta.env.VITE_API_URL || '/api';
      const xhr = new XMLHttpRequest();

      // Handle progress
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          setUploadProgress({
            loaded: e.loaded,
            total: e.total,
            percentage: Math.round((e.loaded / e.total) * 100)
          });
        }
      });

      // Handle completion
      xhr.addEventListener('load', () => {
        setUploadProgress(null);
        
        if (xhr.status === 200) {
          // Create blob from response
          const blob = new Blob([xhr.response], { type: 'application/zip' });
          const url = window.URL.createObjectURL(blob);
          
          // Get filename from Content-Disposition header or use default
          const contentDisposition = xhr.getResponseHeader('Content-Disposition');
          let filename = `${selectedFile.name.replace('.pdf', '')}_split.zip`;
          
          if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
            if (filenameMatch) {
              filename = filenameMatch[1];
            }
          }
          
          // Create download link and trigger download
          const a = document.createElement('a');
          a.href = url;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          window.URL.revokeObjectURL(url);
          
          setSuccess(`Successfully split PDF! Downloaded ${filename}`);
        } else {
          // Handle error response
          try {
            const errorResponse = JSON.parse(xhr.responseText);
            setError(errorResponse.detail || 'Failed to split PDF');
          } catch {
            setError(`Server error: ${xhr.status} ${xhr.statusText}`);
          }
        }
        setIsProcessing(false);
      });

      // Handle errors
      xhr.addEventListener('error', () => {
        setUploadProgress(null);
        setError('Network error occurred while uploading file');
        setIsProcessing(false);
      });

      xhr.addEventListener('timeout', () => {
        setUploadProgress(null);
        setError('Upload timed out. Please try again.');
        setIsProcessing(false);
      });

      // Configure and send request
      xhr.responseType = 'blob';
      xhr.timeout = 300000; // 5 minutes timeout
      xhr.open('POST', `${apiUrl}/split`);
      xhr.send(formData);

    } catch (err) {
      setUploadProgress(null);
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
      setIsProcessing(false);
    }
  }, [selectedFile, pageRanges, canSplit]);

  const clearMessages = useCallback(() => {
    setError(null);
    setSuccess(null);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-3">
            <Scissors className="h-8 w-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">PDF Splitter</h1>
          </div>
          
          <div className="flex items-center space-x-4">
            <button
              onClick={toggleDarkMode}
              className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors duration-200"
              title={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {darkMode ? <Sun className="h-5 w-5 text-gray-600 dark:text-gray-300" /> : <Moon className="h-5 w-5 text-gray-600" />}
            </button>
            
            <a
              href="https://github.com/your-username/pdf-splitter"
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors duration-200"
              title="View source on GitHub"
            >
              <Github className="h-5 w-5 text-gray-600 dark:text-gray-300" />
            </a>
          </div>
        </div>

        {/* Description */}
        <div className="mb-8 text-center">
          <p className="text-lg text-gray-600 dark:text-gray-300 mb-2">
            Split PDF files by extracting specific pages or page ranges
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Upload a PDF (up to 130MB), specify page ranges, and download the extracted pages as a ZIP file
          </p>
        </div>

        {/* Main content */}
        <div className="space-y-6">
          {/* File upload */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">1. Upload PDF File</h2>
            <DropZone
              onFileSelect={handleFileSelect}
              selectedFile={selectedFile}
              onFileRemove={handleFileRemove}
              disabled={isProcessing}
            />
          </div>

          {/* Page ranges */}
          {selectedFile && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">2. Specify Page Ranges</h2>
              <RangeInput
                value={pageRanges}
                onChange={setPageRanges}
                totalPages={totalPages}
                disabled={isProcessing}
              />
            </div>
          )}

          {/* Split button and progress */}
          {selectedFile && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">3. Split PDF</h2>
              
              <button
                onClick={handleSplit}
                disabled={!canSplit || isProcessing}
                className={`
                  w-full flex items-center justify-center space-x-2 py-3 px-4 rounded-lg font-medium transition-all duration-200
                  ${canSplit && !isProcessing
                    ? 'btn-primary'
                    : 'btn-disabled'
                  }
                `}
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <Download className="h-5 w-5" />
                    <span>Split & Download</span>
                  </>
                )}
              </button>

              {/* Upload progress */}
              {uploadProgress && (
                <div className="mt-4 space-y-2">
                  <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                    <span>Uploading...</span>
                    <span>{uploadProgress.percentage}%</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${uploadProgress.percentage}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Messages */}
          {(error || success) && (
            <div className="space-y-4">
              {error && (
                <div className="flex items-start space-x-3 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                  <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
                  </div>
                  <button
                    onClick={clearMessages}
                    className="text-red-400 hover:text-red-600 dark:hover:text-red-300"
                  >
                    ×
                  </button>
                </div>
              )}

              {success && (
                <div className="flex items-start space-x-3 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                  <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm text-green-600 dark:text-green-400">{success}</p>
                  </div>
                  <button
                    onClick={clearMessages}
                    className="text-green-400 hover:text-green-600 dark:hover:text-green-300"
                  >
                    ×
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <footer className="mt-12 pt-8 border-t border-gray-200 dark:border-gray-700 text-center text-sm text-gray-500 dark:text-gray-400">
          <p>
            Built with FastAPI, React, and TypeScript. 
            Process files locally with privacy in mind.
          </p>
        </footer>
      </div>
    </div>
  );
}