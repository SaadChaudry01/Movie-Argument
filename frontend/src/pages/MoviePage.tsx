import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Star,
  Clock,
  Calendar,
  DollarSign,
  Users,
  Film,
  GitCompare,
  Loader2,
  AlertCircle,
  TrendingUp,
} from 'lucide-react';
import { getMovie, getMovieScore, getRecommendations, getCastAnalysis, getPosterUrl, getBackdropUrl } from '../services/api';
import { ScoreGauge, ScoreRadar, FeatureBreakdown } from '../components/ScoreBreakdownChart';
import MovieCard from '../components/MovieCard';
import type { MovieDetails, ScoreBreakdown, MovieBasic } from '../types';

export default function MoviePage() {
  const { id } = useParams<{ id: string }>();
  const [movie, setMovie] = useState<MovieDetails | null>(null);
  const [scoreBreakdown, setScoreBreakdown] = useState<ScoreBreakdown | null>(null);
  const [recommendations, setRecommendations] = useState<MovieBasic[]>([]);
  const [castAnalysis, setCastAnalysis] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadMovie() {
      if (!id) return;

      setIsLoading(true);
      setError(null);

      try {
        const movieId = parseInt(id);
        const [movieData, scoreData, recsData, castData] = await Promise.all([
          getMovie(movieId),
          getMovieScore(movieId),
          getRecommendations(movieId),
          getCastAnalysis(movieId),
        ]);

        setMovie(movieData);
        setScoreBreakdown(scoreData);
        setRecommendations(recsData.recommendations.slice(0, 6));
        setCastAnalysis(castData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load movie');
      } finally {
        setIsLoading(false);
      }
    }

    loadMovie();
  }, [id]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-dark-950 flex items-center justify-center">
        <Loader2 className="w-12 h-12 text-primary-500 animate-spin" />
      </div>
    );
  }

  if (error || !movie) {
    return (
      <div className="min-h-screen bg-dark-950 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-white mb-2">Error Loading Movie</h2>
          <p className="text-gray-400">{error || 'Movie not found'}</p>
          <Link to="/" className="btn-primary mt-4 inline-block">
            Go Home
          </Link>
        </div>
      </div>
    );
  }

  const year = movie.release_date?.split('-')[0] || 'N/A';
  const runtime = movie.runtime
    ? `${Math.floor(movie.runtime / 60)}h ${movie.runtime % 60}m`
    : 'N/A';

  return (
    <div className="min-h-screen bg-dark-950">
      {/* Hero Section with Backdrop */}
      <section className="relative">
        {movie.backdrop_path && (
          <div className="absolute inset-0 h-[500px]">
            <img
              src={getBackdropUrl(movie.backdrop_path)}
              alt=""
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-dark-950 via-dark-950/80 to-dark-950/40" />
          </div>
        )}

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 pb-12">
          <div className="flex flex-col md:flex-row gap-8">
            {/* Poster */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex-shrink-0"
            >
              <img
                src={getPosterUrl(movie.poster_path, 'w500')}
                alt={movie.title}
                className="w-64 md:w-80 rounded-xl shadow-2xl mx-auto"
              />
            </motion.div>

            {/* Info */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex-1"
            >
              <h1 className="text-3xl md:text-5xl font-bold text-white mb-2">
                {movie.title}
              </h1>
              {movie.tagline && (
                <p className="text-xl text-gray-400 italic mb-4">{movie.tagline}</p>
              )}

              {/* Meta Info */}
              <div className="flex flex-wrap items-center gap-4 text-gray-300 mb-6">
                <span className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  {year}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {runtime}
                </span>
                <span className="flex items-center gap-1">
                  <Star className="w-4 h-4 text-primary-500 fill-primary-500" />
                  {movie.vote_average.toFixed(1)}/10
                </span>
                <span className="text-gray-500">
                  ({movie.vote_count.toLocaleString()} votes)
                </span>
              </div>

              {/* Genres */}
              <div className="flex flex-wrap gap-2 mb-6">
                {movie.genres.map((genre) => (
                  <span
                    key={genre.id}
                    className="px-3 py-1 bg-dark-800 border border-dark-600 rounded-full text-sm text-gray-300"
                  >
                    {genre.name}
                  </span>
                ))}
              </div>

              {/* Overview */}
              <p className="text-gray-300 leading-relaxed mb-6">{movie.overview}</p>

              {/* Director & Financial */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                {movie.director && (
                  <div>
                    <p className="text-gray-500 text-sm">Director</p>
                    <p className="text-white font-medium">{movie.director}</p>
                  </div>
                )}
                {movie.budget > 0 && (
                  <div>
                    <p className="text-gray-500 text-sm">Budget</p>
                    <p className="text-white font-medium">
                      ${(movie.budget / 1000000).toFixed(0)}M
                    </p>
                  </div>
                )}
                {movie.revenue > 0 && (
                  <div>
                    <p className="text-gray-500 text-sm">Revenue</p>
                    <p className="text-white font-medium">
                      ${(movie.revenue / 1000000).toFixed(0)}M
                    </p>
                  </div>
                )}
                <div>
                  <p className="text-gray-500 text-sm">Popularity</p>
                  <p className="text-white font-medium">{movie.popularity.toFixed(1)}</p>
                </div>
              </div>

              {/* Compare CTA */}
              <Link
                to={`/compare?movie1=${movie.id}`}
                className="btn-primary inline-flex items-center gap-2"
              >
                <GitCompare className="w-5 h-5" />
                Compare This Movie
              </Link>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Score Analysis Section */}
      {scoreBreakdown && (
        <section className="py-12 bg-dark-900">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <motion.h2
              initial={{ y: 20, opacity: 0 }}
              whileInView={{ y: 0, opacity: 1 }}
              viewport={{ once: true }}
              className="text-2xl font-bold text-white mb-8 flex items-center gap-2"
            >
              <TrendingUp className="w-6 h-6 text-primary-500" />
              Score Analysis
            </motion.h2>

            <div className="grid md:grid-cols-3 gap-8">
              {/* Score Gauge */}
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                whileInView={{ scale: 1, opacity: 1 }}
                viewport={{ once: true }}
                className="card p-6 flex flex-col items-center"
              >
                <ScoreGauge
                  score={scoreBreakdown.total_score}
                  grade={scoreBreakdown.grade}
                  size="lg"
                />
                <p className="text-gray-400 text-center mt-4">
                  {scoreBreakdown.summary}
                </p>
                
                <div className="mt-4 w-full space-y-2">
                  <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wide">Strengths</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {scoreBreakdown.strengths.map((s) => (
                        <span key={s} className="text-xs bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                  {scoreBreakdown.weaknesses.length > 0 && (
                    <div>
                      <p className="text-xs text-gray-500 uppercase tracking-wide">Weaknesses</p>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {scoreBreakdown.weaknesses.map((w) => (
                          <span key={w} className="text-xs bg-red-500/20 text-red-400 px-2 py-0.5 rounded">
                            {w}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>

              {/* Radar Chart */}
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                whileInView={{ scale: 1, opacity: 1 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1 }}
                className="card p-6"
              >
                <h3 className="font-semibold text-white mb-4 text-center">
                  Feature Profile
                </h3>
                <ScoreRadar breakdown={scoreBreakdown} />
              </motion.div>

              {/* Feature Breakdown */}
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                whileInView={{ scale: 1, opacity: 1 }}
                viewport={{ once: true }}
                transition={{ delay: 0.2 }}
                className="card p-6"
              >
                <h3 className="font-semibold text-white mb-4">Score Breakdown</h3>
                <FeatureBreakdown breakdown={scoreBreakdown} />
              </motion.div>
            </div>
          </div>
        </section>
      )}

      {/* Cast Section */}
      {movie.cast && movie.cast.length > 0 && (
        <section className="py-12 bg-dark-950">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <motion.h2
              initial={{ y: 20, opacity: 0 }}
              whileInView={{ y: 0, opacity: 1 }}
              viewport={{ once: true }}
              className="text-2xl font-bold text-white mb-8 flex items-center gap-2"
            >
              <Users className="w-6 h-6 text-primary-500" />
              Cast
              {castAnalysis && (
                <span className="text-sm font-normal text-gray-400 ml-2">
                  Star Power: {castAnalysis.total_star_power.toFixed(0)}
                </span>
              )}
            </motion.h2>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {movie.cast.slice(0, 12).map((member, index) => (
                <motion.div
                  key={member.id}
                  initial={{ y: 20, opacity: 0 }}
                  whileInView={{ y: 0, opacity: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.05 }}
                  className="card overflow-hidden"
                >
                  <div className="aspect-[2/3] bg-dark-800">
                    {member.profile_path ? (
                      <img
                        src={`https://image.tmdb.org/t/p/w185${member.profile_path}`}
                        alt={member.name}
                        className="w-full h-full object-cover"
                        loading="lazy"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-gray-600">
                        <Users className="w-12 h-12" />
                      </div>
                    )}
                  </div>
                  <div className="p-3">
                    <p className="font-medium text-white text-sm truncate">
                      {member.name}
                    </p>
                    <p className="text-gray-500 text-xs truncate">{member.character}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <section className="py-12 bg-dark-900">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <motion.h2
              initial={{ y: 20, opacity: 0 }}
              whileInView={{ y: 0, opacity: 1 }}
              viewport={{ once: true }}
              className="text-2xl font-bold text-white mb-8 flex items-center gap-2"
            >
              <Film className="w-6 h-6 text-primary-500" />
              Similar Movies
            </motion.h2>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {recommendations.map((rec, index) => (
                <motion.div
                  key={rec.id}
                  initial={{ y: 20, opacity: 0 }}
                  whileInView={{ y: 0, opacity: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.05 }}
                >
                  <MovieCard movie={rec} />
                </motion.div>
              ))}
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
