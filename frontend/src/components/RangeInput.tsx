import { useState, useEffect } from 'react';
import { HelpCircle, AlertCircle, CheckCircle, BookOpen } from 'lucide-react';
import { parsePageRanges, getPageRangeExamples, formatPageRanges } from '../utils/parseRange';

interface RangeInputProps {
  value: string;
  onChange: (value: string) => void;
  totalPages?: number;
  disabled?: boolean;
}

export default function RangeInput({ value, onChange, totalPages, disabled = false }: RangeInputProps) {
  const [showHelp, setShowHelp] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isValid, setIsValid] = useState(false);

  useEffect(() => {
    if (!value.trim()) {
      setError(null);
      setIsValid(false);
      return;
    }

    const result = parsePageRanges(value);
    if (!result.isValid) {
      setError(result.error || 'Invalid range format');
      setIsValid(false);
      return;
    }

    if (totalPages && result.pages) {
      const outOfBoundsPages = result.pages.filter(page => page > totalPages);
      if (outOfBoundsPages.length > 0) {
        setError(`Page(s) ${outOfBoundsPages.join(', ')} are out of bounds (PDF has ${totalPages} pages)`);
        setIsValid(false);
        return;
      }
    }

    setError(null);
    setIsValid(true);
  }, [value, totalPages]);

  const handleExampleClick = (example: string) => {
    onChange(example);
    setShowHelp(false);
  };

  const generateQuickOptions = () => {
    if (!totalPages) return [];
    
    const options = [];
    
    // First 5 pages
    if (totalPages >= 5) {
      options.push('1-5');
    }
    
    // Last 5 pages
    if (totalPages >= 5) {
      options.push(`${totalPages - 4}-${totalPages}`);
    }
    
    // All pages
    options.push(`1-${totalPages}`);
    
    // Odd pages
    if (totalPages >= 3) {
      const oddPages = [];
      for (let i = 1; i <= totalPages; i += 2) {
        oddPages.push(i);
      }
      options.push(formatPageRanges(oddPages));
    }
    
    // Even pages
    if (totalPages >= 4) {
      const evenPages = [];
      for (let i = 2; i <= totalPages; i += 2) {
        evenPages.push(i);
      }
      options.push(formatPageRanges(evenPages));
    }
    
    return options;
  };

  const quickOptions = generateQuickOptions();
  const examples = getPageRangeExamples();

  return (
    <div className="space-y-4">
      <div className="relative">
        <label htmlFor="page-ranges" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Page Ranges
          <button
            type="button"
            onClick={() => setShowHelp(!showHelp)}
            className="ml-2 inline-flex items-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            title="Show help"
          >
            <HelpCircle className="h-4 w-4" />
          </button>
        </label>
        
        <div className="relative">
          <input
            id="page-ranges"
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            disabled={disabled}
            placeholder="e.g., 1-5,8,10-12"
            className={`
              input w-full pr-10
              ${error 
                ? 'border-red-300 focus:border-red-500 focus:ring-red-500' 
                : isValid && value.trim()
                  ? 'border-green-300 focus:border-green-500 focus:ring-green-500'
                  : ''
              }
            `}
          />
          
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            {error && <AlertCircle className="h-5 w-5 text-red-500" />}
            {isValid && value.trim() && !error && <CheckCircle className="h-5 w-5 text-green-500" />}
          </div>
        </div>
        
        {totalPages && (
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400 flex items-center">
            <BookOpen className="h-4 w-4 mr-1" />
            PDF has {totalPages} pages
          </p>
        )}
      </div>

      {error && (
        <div className="flex items-center space-x-2 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
          <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {quickOptions.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Quick Options:</p>
          <div className="flex flex-wrap gap-2">
            {quickOptions.map((option, index) => (
              <button
                key={index}
                onClick={() => handleExampleClick(option)}
                disabled={disabled}
                className="px-3 py-1 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {option}
              </button>
            ))}
          </div>
        </div>
      )}

      {showHelp && (
        <div className="card p-4 space-y-3 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
          <h4 className="font-medium text-blue-900 dark:text-blue-100">Page Range Format</h4>
          <div className="text-sm text-blue-800 dark:text-blue-200 space-y-2">
            <p>Use commas to separate individual pages and ranges:</p>
            <ul className="list-disc list-inside space-y-1 ml-2">
              <li><code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">5</code> - Single page</li>
              <li><code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">1-5</code> - Page range</li>
              <li><code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">1-3,5,7-9</code> - Multiple ranges and pages</li>
            </ul>
          </div>
          
          <div className="space-y-2">
            <p className="text-sm font-medium text-blue-900 dark:text-blue-100">Examples:</p>
            <div className="flex flex-wrap gap-2">
              {examples.map((example, index) => (
                <button
                  key={index}
                  onClick={() => handleExampleClick(example)}
                  disabled={disabled}
                  className="px-2 py-1 text-xs bg-blue-200 dark:bg-blue-800 text-blue-800 dark:text-blue-200 rounded hover:bg-blue-300 dark:hover:bg-blue-700 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}