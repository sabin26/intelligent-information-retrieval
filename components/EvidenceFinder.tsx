import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Task1Data, Publication, IndexingStrategy } from '../types';
import { SearchIcon, CheckCircleIcon, UserIcon } from './icons';
import { getTaskData } from '../services/gameService';
import Loader from './Loader';

interface Task1Props {
  onComplete: () => void;
}

const Task1_SearchEngine: React.FC<Task1Props> = ({ onComplete }) => {
  const [taskData] = useState<Task1Data>(getTaskData().task1);
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [foundPublications, setFoundPublications] = useState<Publication[] | null>(null);
  const [indexingStrategy, setIndexingStrategy] = useState<IndexingStrategy>(IndexingStrategy.Inverted);
  const [searchAttempted, setSearchAttempted] = useState(false);

  const handleSearch = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setSearchAttempted(true);
    setIsLoading(true);
    setError(null);
    setFoundPublications(null);

    setTimeout(() => {
      const queryLower = query.toLowerCase().trim();
      let isMatch = false;

      if (indexingStrategy === IndexingStrategy.Positional) {
        const expectedPhrase = taskData.expectedKeywords.join(' ');
        isMatch = queryLower.includes(expectedPhrase);
      } else {
        isMatch = taskData.expectedKeywords.every(kw => queryLower.includes(kw));
      }

      if (isMatch) {
        setFoundPublications(taskData.mockPublications);
      } else {
        setError(`No relevant publications found for that query using the ${indexingStrategy === IndexingStrategy.Positional ? 'Positional' : 'Inverted'} Index. Please try searching for keywords mentioned in the task description.`);
      }
      setIsLoading(false);
    }, 1500);
  }, [query, taskData, indexingStrategy]);

  const handleResetSearch = () => {
    setSearchAttempted(false);
    setFoundPublications(null);
    setError(null);
    setQuery('');
  };

  const IndexingStrategyToggle: React.FC = () => (
    <div className="flex items-center justify-center bg-slate-200/60 p-1 rounded-lg mb-6">
      <button
        onClick={() => setIndexingStrategy(IndexingStrategy.Inverted)}
        className={`w-1/2 py-2 text-sm font-semibold rounded-md transition-colors duration-200 ${indexingStrategy === IndexingStrategy.Inverted ? 'bg-white shadow text-slate-800' : 'text-slate-500 hover:bg-slate-200'} disabled:opacity-60 disabled:cursor-not-allowed`}
        disabled={isLoading || searchAttempted}
      >
        Inverted Index
      </button>
      <button
        onClick={() => setIndexingStrategy(IndexingStrategy.Positional)}
        className={`w-1/2 py-2 text-sm font-semibold rounded-md transition-colors duration-200 ${indexingStrategy === IndexingStrategy.Positional ? 'bg-white shadow text-slate-800' : 'text-slate-500 hover:bg-slate-200'} disabled:opacity-60 disabled:cursor-not-allowed`}
        disabled={isLoading || searchAttempted}
      >
        Positional Index
      </button>
    </div>
  );

  return (
    <div className="bg-white/80 backdrop-blur-sm p-6 sm:p-8 rounded-lg shadow-lg border border-slate-200/80">
      <h3 className="text-xl font-bold text-slate-800 font-display tracking-wide">Task 1: Vertical Search Engine</h3>
      <p className="text-sm text-slate-600 mt-1 mb-6">{taskData.prompt}</p>

      <IndexingStrategyToggle />

      <form onSubmit={handleSearch} className="flex items-center gap-2 mb-6">
        <div className="relative flex-grow">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <SearchIcon className="w-5 h-5 text-slate-400" />
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for publications..."
            className="w-full pl-10 pr-4 py-2.5 border border-slate-400 rounded-md shadow-inner bg-slate-50 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 transition disabled:opacity-60 disabled:bg-slate-100"
            disabled={isLoading || searchAttempted}
          />
        </div>
        <motion.button 
            type="submit" 
            className="px-6 py-2.5 bg-slate-800 text-white font-semibold rounded-md shadow-md hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-500 transition disabled:opacity-50 disabled:cursor-not-allowed" 
            disabled={isLoading || searchAttempted || !query.trim()}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
        >
          {isLoading ? 'Searching...' : 'Search'}
        </motion.button>
      </form>
      
      <AnimatePresence>
        {isLoading && <div className="flex justify-center py-4"><Loader /></div>}
        {searchAttempted && error && !isLoading && <p className="text-sm text-red-600 text-center mt-4">{error}</p>}
        {searchAttempted && foundPublications && (
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-6"
            >
                <div className="flex items-center justify-center gap-2 text-green-700 bg-green-100 p-3 rounded-md">
                    <CheckCircleIcon className="w-6 h-6"/>
                    <p className="font-bold">Search Complete! Publications Found.</p>
                </div>
                <div className="space-y-4 mt-4">
                    {foundPublications.map((pub, index) => (
                        <motion.div 
                            key={index} 
                            className="p-4 border border-slate-300 rounded-lg bg-white shadow"
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.2 + 0.5 }}
                        >
                            <div className="flex justify-between items-start">
                                <a href={pub.publicationUrl} target="_blank" rel="noopener noreferrer" className="font-bold text-slate-800 hover:text-amber-700 pr-4">{pub.title}</a>
                                {pub.relevancyScore && (
                                    <div className="text-right flex-shrink-0">
                                        <span className="text-xs text-slate-500">Relevancy</span>
                                        <p className="font-bold text-amber-700">{pub.relevancyScore.toFixed(2)}</p>
                                    </div>
                                )}
                            </div>
                            <p className="text-sm text-slate-500 mt-1">{pub.year}</p>
                            <div className="mt-2 flex items-center gap-2 flex-wrap text-sm text-slate-700">
                                <UserIcon className="w-4 h-4 text-slate-500"/>
                                {pub.authors.map((author, i) => (
                                  <span key={i}>
                                    {author.profileUrl ? (
                                      <a href={author.profileUrl} target="_blank" rel="noopener noreferrer" className="hover:underline">
                                        {author.name}
                                      </a>
                                    ) : (
                                      author.name
                                    )}
                                    {i < pub.authors.length - 1 && ', '}
                                  </span>
                                ))}
                            </div>
                        </motion.div>
                    ))}
                </div>
            </motion.div>
        )}
      </AnimatePresence>

      {searchAttempted && !isLoading && (
        <div className="text-center mt-8 flex justify-center gap-4">
          <motion.button
            onClick={handleResetSearch}
            className="px-8 py-3 bg-slate-600 text-white font-bold rounded-lg shadow-md hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-500 transition-colors font-display tracking-wider"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Search Again
          </motion.button>
          
          {foundPublications && (
              <motion.button
                onClick={onComplete}
                className="px-8 py-3 bg-amber-600 text-white font-bold rounded-lg shadow-md hover:bg-amber-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-amber-500 transition-colors font-display tracking-wider"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
            >
                Proceed to Task 2
            </motion.button>
          )}
        </div>
      )}
    </div>
  );
};

export default Task1_SearchEngine;