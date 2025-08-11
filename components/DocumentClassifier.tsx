import React, { useState, useCallback } from 'react';
import { classifyDocument } from '../services/geminiService';
import { ClassificationResult, DocCategory } from '../types';
import { BrainCircuitIcon } from './icons';
import Loader from './Loader';
import Alert from './Alert';

const DocumentClassifier: React.FC = () => {
  const [documentText, setDocumentText] = useState<string>('');
  const [result, setResult] = useState<ClassificationResult | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleClassify = useCallback(async () => {
    if (!documentText.trim()) {
      setError('Please enter some text to classify.');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const classification = await classifyDocument(documentText);
      setResult(classification);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred.');
    } finally {
      setIsLoading(false);
    }
  }, [documentText]);

  const getResultBadgeClass = (category: DocCategory | undefined) => {
    switch(category) {
      case DocCategory.Health: return 'bg-emerald-100 text-emerald-800';
      case DocCategory.Business: return 'bg-sky-100 text-sky-800';
      case DocCategory.Politics: return 'bg-purple-100 text-purple-800';
      default: return 'bg-slate-100 text-slate-800';
    }
  };
  
  return (
    <div className="bg-white p-6 sm:p-8 rounded-xl shadow-lg border border-slate-200/80">
      <h2 className="text-xl font-semibold text-slate-800 mb-1">Document Classifier</h2>
      <p className="text-sm text-slate-500 mb-6">Enter text to classify it into Politics, Business, or Health categories.</p>
      
      <div className="space-y-4">
        <textarea
          value={documentText}
          onChange={(e) => setDocumentText(e.target.value)}
          placeholder="Paste or type your document here... The longer the text, the better the classification."
          className="w-full h-48 p-3 border border-slate-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition"
          disabled={isLoading}
        />
        <button 
          onClick={handleClassify} 
          className="w-full flex items-center justify-center px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg shadow-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={isLoading}
        >
            {isLoading ? (
                <>
                    <Loader isButtonLoader={true} />
                    <span>Classifying...</span>
                </>
            ) : (
                <>
                    <BrainCircuitIcon className="w-5 h-5 mr-2"/>
                    <span>Classify Document</span>
                </>
            )}
        </button>
      </div>

      {error && <div className="mt-6"><Alert message={error} /></div>}

      {result && !isLoading && !error && (
        <div className="mt-8 pt-6 border-t border-slate-200">
          <h3 className="text-lg font-medium text-slate-800 mb-3">Classification Result</h3>
          <div className="text-center bg-slate-50 p-6 rounded-lg">
            <p className="text-sm text-slate-500 mb-2">The document is classified as:</p>
            <span className={`px-6 py-2 text-lg font-bold rounded-full inline-block ${getResultBadgeClass(result.category)}`}>
              {result.category}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentClassifier;
