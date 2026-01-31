import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { GitCompare, TrendingUp, Search, Sparkles, BarChart3, Users } from 'lucide-react';
import SearchBar from '../components/SearchBar';
import MovieCard from '../components/MovieCard';
import { getTrending } from '../services/api';
import type { MovieBasic } from '../types';

export default function HomePage() {
  const [trendingMovies, setTrendingMovies] = useState<MovieBasic[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadTrending() {
      try {
        const data = await getTrending('week', false);
        setTrendingMovies(data.results.slice(0, 6));
      } catch (error) {
        console.error('Failed to load trending:', error);
      } finally {
        setIsLoading(false);
      }
    }
    loadTrending();
  }, []);

  const features = [
    {
      icon: GitCompare,
      title: 'Head-to-Head Comparison',
      description: 'Compare any two movies with detailed evidence-based arguments',
    },
    {
      icon: BarChart3,
      title: 'Explainable Scoring',
      description: 'Transparent scoring with feature-level attribution',
    },
    {
      icon: Users,
      title: 'Cast Analysis',
      description: 'Analyze star power and cast depth metrics',
    },
    {
      icon: Sparkles,
      title: 'AI-Powered Verdicts',
      description: 'Natural language explanations for all comparisons',
    },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-dark-900 to-dark-950 py-20">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiMyMDIwMjAiIGZpbGwtb3BhY2l0eT0iMC40Ij48cGF0aCBkPSJNMzYgMzRjMC0yLjIgMS44LTQgNC00czQgMS44IDQgNC0xLjggNC00IDQtNC0xLjgtNC00eiIvPjwvZz48L2c+PC9zdmc+')] opacity-30" />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
          <motion.div
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="text-center max-w-3xl mx-auto"
          >
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
              Settle Movie Arguments with{' '}
              <span className="text-primary-500">Data</span>
            </h1>
            <p className="text-xl text-gray-400 mb-10">
              An AI-powered engine that compares movies using ratings, critic scores, 
              popularity, and cast metadata with fully explainable verdicts.
            </p>
            
            <div className="max-w-xl mx-auto mb-8">
              <SearchBar
                onSelect={(movie) => {
                  window.location.href = `/movie/${movie.id}`;
                }}
                placeholder="Search for any movie to analyze..."
              />
            </div>

            <div className="flex flex-wrap justify-center gap-4">
              <Link to="/compare" className="btn-primary inline-flex items-center gap-2">
                <GitCompare className="w-5 h-5" />
                Compare Movies
              </Link>
              <Link to="/trending" className="btn-secondary inline-flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                View Trending
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-dark-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.h2
            initial={{ y: 20, opacity: 0 }}
            whileInView={{ y: 0, opacity: 1 }}
            viewport={{ once: true }}
            className="text-2xl md:text-3xl font-bold text-white text-center mb-12"
          >
            Data-Driven Movie Analysis
          </motion.h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ y: 30, opacity: 0 }}
                whileInView={{ y: 0, opacity: 1 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="card p-6 hover:border-primary-500/50 transition-colors"
              >
                <feature.icon className="w-10 h-10 text-primary-500 mb-4" />
                <h3 className="font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-gray-500 text-sm">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Trending Section */}
      <section className="py-16 bg-dark-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-8">
            <motion.h2
              initial={{ x: -20, opacity: 0 }}
              whileInView={{ x: 0, opacity: 1 }}
              viewport={{ once: true }}
              className="text-2xl font-bold text-white flex items-center gap-2"
            >
              <TrendingUp className="w-6 h-6 text-primary-500" />
              Trending This Week
            </motion.h2>
            <Link
              to="/trending"
              className="text-primary-500 hover:text-primary-400 text-sm font-medium"
            >
              View All
            </Link>
          </div>

          {isLoading ? (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="card aspect-[2/3] animate-pulse bg-dark-800" />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {trendingMovies.map((movie, index) => (
                <motion.div
                  key={movie.id}
                  initial={{ y: 30, opacity: 0 }}
                  whileInView={{ y: 0, opacity: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                >
                  <MovieCard movie={movie} />
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-primary-600 to-primary-700">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            whileInView={{ scale: 1, opacity: 1 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl md:text-4xl font-bold text-dark-950 mb-4">
              Ready to Settle the Debate?
            </h2>
            <p className="text-dark-800 text-lg mb-8">
              Compare your favorite movies and get data-backed answers
            </p>
            <Link
              to="/compare"
              className="inline-flex items-center gap-2 bg-dark-950 text-white px-8 py-3 rounded-lg font-semibold hover:bg-dark-900 transition-colors"
            >
              <GitCompare className="w-5 h-5" />
              Start Comparing
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
