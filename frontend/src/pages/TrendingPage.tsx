import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Calendar, Loader2 } from 'lucide-react';
import MovieCard from '../components/MovieCard';
import { getTrending } from '../services/api';
import type { MovieBasic } from '../types';

export default function TrendingPage() {
  const [timeWindow, setTimeWindow] = useState<'day' | 'week'>('week');
  const [movies, setMovies] = useState<MovieBasic[]>([]);
  const [scoredMovies, setScoredMovies] = useState<
    Array<{ movie: MovieBasic; score: number; grade: string }>
  >([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showScores, setShowScores] = useState(false);

  useEffect(() => {
    async function loadTrending() {
      setIsLoading(true);
      try {
        const data = await getTrending(timeWindow, showScores);
        setMovies(data.results);
        if (data.scored_results) {
          setScoredMovies(data.scored_results);
        }
      } catch (error) {
        console.error('Failed to load trending:', error);
      } finally {
        setIsLoading(false);
      }
    }

    loadTrending();
  }, [timeWindow, showScores]);

  return (
    <div className="min-h-screen bg-dark-950 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="text-center mb-10"
        >
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-3 flex items-center justify-center gap-3">
            <TrendingUp className="w-10 h-10 text-primary-500" />
            Trending Movies
          </h1>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Discover what's popular right now based on TMDB's real-time trending data.
          </p>
        </motion.div>

        {/* Controls */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="flex flex-wrap items-center justify-center gap-4 mb-8"
        >
          {/* Time Window Toggle */}
          <div className="flex items-center bg-dark-800 rounded-lg p-1">
            <button
              onClick={() => setTimeWindow('day')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                timeWindow === 'day'
                  ? 'bg-primary-500 text-dark-950'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Today
            </button>
            <button
              onClick={() => setTimeWindow('week')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                timeWindow === 'week'
                  ? 'bg-primary-500 text-dark-950'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              This Week
            </button>
          </div>

          {/* Show Scores Toggle */}
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={showScores}
              onChange={(e) => setShowScores(e.target.checked)}
              className="w-4 h-4 rounded border-dark-600 bg-dark-800 text-primary-500 focus:ring-primary-500"
            />
            <span className="text-gray-400 text-sm">Show Engine Scores</span>
          </label>
        </motion.div>

        {/* Loading State */}
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-12 h-12 text-primary-500 animate-spin" />
          </div>
        ) : (
          <>
            {/* Movie Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4 md:gap-6">
              {showScores && scoredMovies.length > 0
                ? scoredMovies.map(({ movie, score, grade }, index) => (
                    <motion.div
                      key={movie.id}
                      initial={{ y: 30, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <MovieCard movie={movie} score={score} grade={grade} />
                    </motion.div>
                  ))
                : movies.map((movie, index) => (
                    <motion.div
                      key={movie.id}
                      initial={{ y: 30, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <MovieCard movie={movie} />
                    </motion.div>
                  ))}
            </div>

            {/* Stats */}
            {showScores && scoredMovies.length > 0 && (
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                className="mt-12 card p-6"
              >
                <h3 className="font-semibold text-white mb-4">
                  Trending Stats (Engine Scores)
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-primary-500">
                      {Math.max(...scoredMovies.map((m) => m.score)).toFixed(1)}
                    </p>
                    <p className="text-gray-500 text-sm">Highest Score</p>
                  </div>
                  <div className="text-center">
                    <p className="text-3xl font-bold text-primary-500">
                      {Math.min(...scoredMovies.map((m) => m.score)).toFixed(1)}
                    </p>
                    <p className="text-gray-500 text-sm">Lowest Score</p>
                  </div>
                  <div className="text-center">
                    <p className="text-3xl font-bold text-primary-500">
                      {(
                        scoredMovies.reduce((sum, m) => sum + m.score, 0) /
                        scoredMovies.length
                      ).toFixed(1)}
                    </p>
                    <p className="text-gray-500 text-sm">Average Score</p>
                  </div>
                  <div className="text-center">
                    <p className="text-3xl font-bold text-primary-500">
                      {scoredMovies.filter((m) => m.grade.startsWith('A')).length}
                    </p>
                    <p className="text-gray-500 text-sm">A-Grade Movies</p>
                  </div>
                </div>
              </motion.div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
