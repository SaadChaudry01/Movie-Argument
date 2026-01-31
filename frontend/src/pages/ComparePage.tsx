import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { GitCompare, Loader2, X, AlertCircle } from 'lucide-react';
import SearchBar from '../components/SearchBar';
import MovieCard from '../components/MovieCard';
import WeightSliders from '../components/WeightSliders';
import ComparisonResultComponent from '../components/ComparisonResult';
import { compareMovies, getPosterUrl } from '../services/api';
import type { MovieBasic, ComparisonResult, WeightConfig } from '../types';
import { DEFAULT_WEIGHTS } from '../types';

export default function ComparePage() {
  const [movie1, setMovie1] = useState<MovieBasic | null>(null);
  const [movie2, setMovie2] = useState<MovieBasic | null>(null);
  const [weights, setWeights] = useState<WeightConfig>(DEFAULT_WEIGHTS);
  const [result, setResult] = useState<ComparisonResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCompare = async () => {
    if (!movie1 || !movie2) return;

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const comparison = await compareMovies(movie1.id, movie2.id, weights);
      setResult(comparison);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Comparison failed');
    } finally {
      setIsLoading(false);
    }
  };

  const clearMovie1 = () => {
    setMovie1(null);
    setResult(null);
  };

  const clearMovie2 = () => {
    setMovie2(null);
    setResult(null);
  };

  return (
    <div className="min-h-screen bg-dark-950 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="text-center mb-10"
        >
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-3">
            Movie Comparison Engine
          </h1>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Select two movies to compare. Get detailed, evidence-based arguments 
            for which movie is better based on multiple factors.
          </p>
        </motion.div>

        {/* Movie Selection */}
        <div className="grid md:grid-cols-2 gap-8 mb-8">
          {/* Movie 1 */}
          <motion.div
            initial={{ x: -30, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            className="space-y-4"
          >
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <span className="w-8 h-8 rounded-full bg-primary-500 text-dark-950 flex items-center justify-center font-bold">
                1
              </span>
              First Movie
            </h2>
            
            {movie1 ? (
              <div className="card p-4 relative">
                <button
                  onClick={clearMovie1}
                  className="absolute top-2 right-2 p-1 hover:bg-dark-700 rounded-full transition-colors"
                >
                  <X className="w-5 h-5 text-gray-400" />
                </button>
                <div className="flex gap-4">
                  <img
                    src={getPosterUrl(movie1.poster_path, 'w185')}
                    alt={movie1.title}
                    className="w-24 h-36 object-cover rounded-lg"
                  />
                  <div>
                    <h3 className="font-semibold text-white">{movie1.title}</h3>
                    <p className="text-gray-500 text-sm">
                      {movie1.release_date?.split('-')[0] || 'N/A'}
                    </p>
                    <p className="text-primary-400 text-sm mt-1">
                      Rating: {movie1.vote_average.toFixed(1)}/10
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <SearchBar
                onSelect={setMovie1}
                placeholder="Search for first movie..."
              />
            )}
          </motion.div>

          {/* Movie 2 */}
          <motion.div
            initial={{ x: 30, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            className="space-y-4"
          >
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <span className="w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center font-bold">
                2
              </span>
              Second Movie
            </h2>
            
            {movie2 ? (
              <div className="card p-4 relative">
                <button
                  onClick={clearMovie2}
                  className="absolute top-2 right-2 p-1 hover:bg-dark-700 rounded-full transition-colors"
                >
                  <X className="w-5 h-5 text-gray-400" />
                </button>
                <div className="flex gap-4">
                  <img
                    src={getPosterUrl(movie2.poster_path, 'w185')}
                    alt={movie2.title}
                    className="w-24 h-36 object-cover rounded-lg"
                  />
                  <div>
                    <h3 className="font-semibold text-white">{movie2.title}</h3>
                    <p className="text-gray-500 text-sm">
                      {movie2.release_date?.split('-')[0] || 'N/A'}
                    </p>
                    <p className="text-blue-400 text-sm mt-1">
                      Rating: {movie2.vote_average.toFixed(1)}/10
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <SearchBar
                onSelect={setMovie2}
                placeholder="Search for second movie..."
              />
            )}
          </motion.div>
        </div>

        {/* Weight Configuration */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <WeightSliders weights={weights} onChange={setWeights} />
        </motion.div>

        {/* Compare Button */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-center mb-12"
        >
          <button
            onClick={handleCompare}
            disabled={!movie1 || !movie2 || isLoading}
            className="btn-primary inline-flex items-center gap-2 text-lg px-10 py-4 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-6 h-6 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <GitCompare className="w-6 h-6" />
                Compare Movies
              </>
            )}
          </button>
        </motion.div>

        {/* Error */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mb-8 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-3"
            >
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
              <p className="text-red-400">{error}</p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Results */}
        <AnimatePresence>
          {result && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <ComparisonResultComponent result={result} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
