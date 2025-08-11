import React, { useState, useCallback } from 'react';
import { searchPublications } from '../services/geminiService';
import { Publication, GroundingMetadata } from '../types';
import { SearchIcon, BookIcon, UserIcon, LinkIcon } from './icons';
import Loader from './Loader';
import Alert from './Alert';

const PublicationSearch: React.FC = () => {
  const [query, setQuery] = useState<string>('');
  const [publications, setPublications] = useState<Publication[]>([]);
  const [groundingMetadata, setGroundingMetadata] = useState<GroundingMetadata | undefined>(undefined);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [searched, setSearched] = useState<boolean>(false);

  const handleSearch = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);
    setSearched(true);
    setPublications([]);
    setGroundingMetadata(undefined);

    try {
      const { publications: results, groundingMetadata } = await searchPublications(query);
      setPublications(results);
      setGroundingMetadata(groundingMetadata);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred.');
    } finally {
      setIsLoading(false);
    }
  }, [query]);

  return (
    <div className="bg-white p-6 sm:p-8 rounded-xl shadow-lg border border-slate-200/80">
      <h2 className="text-xl font-semibold text-slate-800 mb-1">Publication Search Engine</h2>
      <p className="text-sm text-slate-500 mb-6">Search for papers and books from Coventry University's School of Economics, Finance and Accounting.</p>
      
      <form onSubmit={handleSearch} className="flex items-center gap-2 mb-8">
        <div className="relative flex-grow">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <SearchIcon className="w-5 h-5 text-slate-400" />
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., 'financial risk management' or author name"
            className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition"
            disabled={isLoading}
          />
        </div>
        <button type="submit" className="px-6 py-2.5 bg-indigo-600 text-white font-semibold rounded-lg shadow-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition disabled:opacity-50 disabled:cursor-not-allowed" disabled={isLoading}>
          {isLoading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {isLoading && <div className="flex justify-center items-center py-10"><Loader /></div>}
      {error && <Alert message={error} />}
      
      {searched && !isLoading && !error && publications.length === 0 && (
         <div className="text-center py-10 px-4 bg-slate-50 rounded-lg">
            <BookIcon className="w-12 h-12 text-slate-400 mx-auto mb-3" />
            <h3 className="text-lg font-medium text-slate-700">No Publications Found</h3>
            <p className="text-sm text-slate-500 mt-1">Try refining your search query for better results.</p>
        </div>
      )}

      {publications.length > 0 && (
        <div className="space-y-6">
          <h3 className="text-lg font-medium text-slate-800 border-b pb-2">Search Results</h3>
          {publications.map((pub, index) => (
            <div key={index} className="p-4 border border-slate-200 rounded-lg hover:shadow-md transition-shadow duration-200 bg-slate-50/50">
              <a href={pub.publicationUrl} target="_blank" rel="noopener noreferrer" className="text-lg font-semibold text-indigo-700 hover:underline">{pub.title}</a>
              <p className="text-sm text-slate-500 mt-1">{pub.year}</p>
              <div className="mt-2 flex items-center gap-2 flex-wrap">
                <UserIcon className="w-4 h-4 text-slate-400 flex-shrink-0"/>
                {pub.authors.map((author, i) => (
                  <span key={i} className="text-sm text-slate-700">
                    {author.profileUrl ? (
                      <a href={author.profileUrl} target="_blank" rel="noopener noreferrer" className="hover:underline">{author.name}</a>
                    ) : (
                      author.name
                    )}
                    {i < pub.authors.length - 1 && ', '}
                  </span>
                ))}
              </div>
            </div>
          ))}

          {groundingMetadata && groundingMetadata.groundingChunks?.length > 0 && (
            <div className="pt-6 border-t border-slate-200">
                <h4 className="text-base font-semibold text-slate-700 mb-3 flex items-center">
                    <LinkIcon className="w-5 h-5 mr-2 text-slate-500" />
                    Sources
                </h4>
                <ul className="space-y-2">
                    {groundingMetadata.groundingChunks.map((chunk, index) => (
                        chunk.web && <li key={index} className="flex items-start gap-2.5 pl-1">
                            <span className="text-slate-400 mt-1">&#8226;</span>
                            <div>
                                <a href={chunk.web.uri} target="_blank" rel="noopener noreferrer" className="text-sm text-indigo-700 hover:underline break-all">
                                    {chunk.web.title || chunk.web.uri}
                                </a>
                                <p className="text-xs text-slate-500">{new URL(chunk.web.uri).hostname}</p>
                            </div>
                        </li>
                    ))}
                </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PublicationSearch;
