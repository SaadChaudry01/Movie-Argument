import { motion } from 'framer-motion';
import { Trophy, ArrowRight, AlertCircle, CheckCircle, MinusCircle } from 'lucide-react';
import type { ComparisonResult as ComparisonResultType } from '../types';
import { ScoreGauge, ComparisonRadar, ComparisonBar } from './ScoreBreakdownChart';
import { getPosterUrl } from '../services/api';

interface ComparisonResultProps {
  result: ComparisonResultType;
}

export default function ComparisonResult({ result }: ComparisonResultProps) {
  const {
    movie1_title,
    movie1_score,
    movie1_breakdown,
    movie2_title,
    movie2_score,
    movie2_breakdown,
    winner,
    confidence,
    verdict,
    arguments: args,
    radar_data,
    bar_data,
  } = result;

  const winnerTitle = winner === 'movie1' ? movie1_title : winner === 'movie2' ? movie2_title : 'Tie';

  return (
    <div className="space-y-8 animate-in">
      {/* Winner Banner */}
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="card p-6 text-center bg-gradient-to-br from-dark-900 to-dark-800"
      >
        {winner !== 'tie' ? (
          <>
            <Trophy className="w-12 h-12 text-primary-500 mx-auto mb-3" />
            <h2 className="text-2xl font-bold text-white mb-2">
              {winnerTitle} Wins!
            </h2>
            <p className="text-gray-400 capitalize">
              {confidence.replace('_', ' ')} victory
            </p>
          </>
        ) : (
          <>
            <MinusCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <h2 className="text-2xl font-bold text-white mb-2">
              It's a Tie!
            </h2>
            <p className="text-gray-400">Both movies score nearly identical</p>
          </>
        )}
      </motion.div>

      {/* Score Comparison */}
      <div className="grid md:grid-cols-3 gap-6 items-center">
        {/* Movie 1 */}
        <motion.div
          initial={{ x: -50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          className={`card p-6 text-center ${
            winner === 'movie1' ? 'ring-2 ring-primary-500' : ''
          }`}
        >
          <h3 className="font-bold text-lg text-white mb-4">{movie1_title}</h3>
          <div className="flex justify-center mb-4">
            <ScoreGauge
              score={movie1_score}
              grade={movie1_breakdown.grade}
              size="lg"
            />
          </div>
          {winner === 'movie1' && (
            <span className="inline-flex items-center gap-1 text-primary-500 text-sm font-medium">
              <Trophy className="w-4 h-4" /> Winner
            </span>
          )}
        </motion.div>

        {/* VS */}
        <div className="text-center">
          <div className="text-4xl font-bold text-gray-600">VS</div>
          <div className="text-sm text-gray-500 mt-2">
            Score Difference: {result.score_difference.toFixed(1)} pts
          </div>
        </div>

        {/* Movie 2 */}
        <motion.div
          initial={{ x: 50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          className={`card p-6 text-center ${
            winner === 'movie2' ? 'ring-2 ring-blue-500' : ''
          }`}
        >
          <h3 className="font-bold text-lg text-white mb-4">{movie2_title}</h3>
          <div className="flex justify-center mb-4">
            <ScoreGauge
              score={movie2_score}
              grade={movie2_breakdown.grade}
              size="lg"
            />
          </div>
          {winner === 'movie2' && (
            <span className="inline-flex items-center gap-1 text-blue-500 text-sm font-medium">
              <Trophy className="w-4 h-4" /> Winner
            </span>
          )}
        </motion.div>
      </div>

      {/* Verdict */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="card p-6"
      >
        <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-primary-500" />
          The Verdict
        </h3>
        <p className="text-gray-300 leading-relaxed">{verdict}</p>
      </motion.div>

      {/* Charts */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Radar Chart */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="card p-6"
        >
          <h3 className="font-semibold text-white mb-4">Feature Comparison</h3>
          <div className="flex justify-center gap-6 mb-2 text-sm">
            <span className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-primary-500" />
              {movie1_title}
            </span>
            <span className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-500" />
              {movie2_title}
            </span>
          </div>
          <ComparisonRadar
            data={radar_data}
            movie1Title={movie1_title}
            movie2Title={movie2_title}
          />
        </motion.div>

        {/* Bar Chart */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="card p-6"
        >
          <h3 className="font-semibold text-white mb-4">Score Breakdown</h3>
          <ComparisonBar
            data={bar_data}
            movie1Title={movie1_title}
            movie2Title={movie2_title}
          />
        </motion.div>
      </div>

      {/* Arguments */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="card p-6"
      >
        <h3 className="font-semibold text-white mb-4">Detailed Arguments</h3>
        <div className="space-y-4">
          {args.map((arg, index) => (
            <motion.div
              key={arg.factor}
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.5 + index * 0.1 }}
              className={`p-4 rounded-lg border ${
                arg.importance === 'high'
                  ? 'bg-dark-800 border-primary-500/30'
                  : 'bg-dark-800/50 border-dark-700'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  {arg.winner === 'movie1' && (
                    <CheckCircle className="w-4 h-4 text-primary-500" />
                  )}
                  {arg.winner === 'movie2' && (
                    <CheckCircle className="w-4 h-4 text-blue-500" />
                  )}
                  {arg.winner === 'tie' && (
                    <MinusCircle className="w-4 h-4 text-gray-500" />
                  )}
                  <span className="font-medium text-white">{arg.factor}</span>
                  {arg.importance === 'high' && (
                    <span className="text-xs bg-primary-500/20 text-primary-400 px-2 py-0.5 rounded">
                      Key Factor
                    </span>
                  )}
                </div>
              </div>
              
              <div className="flex items-center gap-4 text-sm mb-2">
                <span className={arg.winner === 'movie1' ? 'text-primary-400 font-medium' : 'text-gray-400'}>
                  {movie1_title}: {arg.movie1_value}
                </span>
                <ArrowRight className="w-4 h-4 text-gray-600" />
                <span className={arg.winner === 'movie2' ? 'text-blue-400 font-medium' : 'text-gray-400'}>
                  {movie2_title}: {arg.movie2_value}
                </span>
              </div>
              
              <p className="text-sm text-gray-500">{arg.explanation}</p>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
