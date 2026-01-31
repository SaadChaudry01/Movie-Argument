import { useState, useEffect, useRef, useCallback } from 'react';
import { Search, X, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import type { MovieBasic } from '../types';
import { searchMovies, getPosterUrl } from '../services/api';

interface SearchBarProps {
  onSelect: (movie: MovieBasic) => void;
  placeholder?: string;
  className?: string;
}

export default function SearchBar({
  onSelect,
  placeholder = 'Search for a movie...',
  className = '',
}: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<MovieBasic[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<NodeJS.Timeout>();

  // Debounced search
  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    if (query.trim().length < 2) {
      setResults([]);
      setIsOpen(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    debounceRef.current = setTimeout(async () => {
      try {
        const response = await searchMovies(query);
        setResults(response.results.slice(0, 8));
        setIsOpen(true);
      } catch (err) {
        setError('Search failed. Please try again.');
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    }, 300);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [query]);

  // Close on click outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = useCallback((movie: MovieBasic) => {
    onSelect(movie);
    setQuery('');
    setResults([]);
    setIsOpen(false);
  }, [onSelect]);

  const handleClear = () => {
    setQuery('');
    setResults([]);
    setIsOpen(false);
    inputRef.current?.focus();
  };

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => results.length > 0 && setIsOpen(true)}
          placeholder={placeholder}
          className="input-field w-full pl-12 pr-12"
        />
        {isLoading && (
          <Loader2 className="absolute right-12 top-1/2 -translate-y-1/2 w-5 h-5 text-primary-500 animate-spin" />
        )}
        {query && (
          <button
            onClick={handleClear}
            className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Results dropdown */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute top-full left-0 right-0 mt-2 bg-dark-900 border border-dark-700 rounded-xl shadow-2xl overflow-hidden z-50"
          >
            {error ? (
              <div className="p-4 text-center text-red-400">{error}</div>
            ) : results.length > 0 ? (
              <ul className="max-h-96 overflow-y-auto">
                {results.map((movie, index) => (
                  <motion.li
                    key={movie.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <button
                      onClick={() => handleSelect(movie)}
                      className="w-full flex items-center gap-3 p-3 hover:bg-dark-800 transition-colors text-left"
                    >
                      <img
                        src={getPosterUrl(movie.poster_path, 'w185')}
                        alt={movie.title}
                        className="w-12 h-18 object-cover rounded"
                      />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-white truncate">
                          {movie.title}
                        </p>
                        <p className="text-sm text-gray-500">
                          {movie.release_date?.split('-')[0] || 'N/A'} •{' '}
                          <span className="text-primary-400">
                            {movie.vote_average.toFixed(1)}
                          </span>
                        </p>
                      </div>
                    </button>
                  </motion.li>
                ))}
              </ul>
            ) : (
              <div className="p-4 text-center text-gray-500">
                No movies found for "{query}"
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
