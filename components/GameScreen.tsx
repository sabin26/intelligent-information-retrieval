import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Case, Challenge, ChallengeType } from '../types';
import EvidenceFinder from './EvidenceFinder';
import ClueAnalyzer from './ClueAnalyzer';

interface GameScreenProps {
  currentCase: Case;
  challengeIndex: number;
  score: number;
  onSuccess: () => void;
}

const GameScreen: React.FC<GameScreenProps> = ({ currentCase, challengeIndex, score, onSuccess }) => {
  const challenge = currentCase.challenges[challengeIndex];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.4 }}
    >
      <div className="bg-slate-800 text-white p-4 rounded-t-lg shadow-lg">
          <div className="flex justify-between items-center">
              <h2 className="font-display text-xl tracking-wider">{currentCase.title}</h2>
              <div className="font-display text-lg">Score: <span className="font-bold text-amber-300">{score}</span></div>
          </div>
          <div className="w-full bg-slate-600 rounded-full h-2.5 mt-2">
            <motion.div 
                className="bg-amber-400 h-2.5 rounded-full" 
                initial={{ width: '0%' }}
                animate={{ width: `${((challengeIndex + 1) / currentCase.challenges.length) * 100}%` }}
                transition={{ duration: 0.5, ease: "easeInOut" }}
            />
          </div>
      </div>
      <div className="bg-white/80 backdrop-blur-sm p-6 sm:p-8 rounded-b-lg shadow-lg border border-slate-200/80">
        <AnimatePresence mode="wait">
            <motion.div
                key={challengeIndex}
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -50 }}
                transition={{ duration: 0.3 }}
            >
                {challenge.type === ChallengeType.Search && (
                    <EvidenceFinder onComplete={onSuccess} />
                )}
                {challenge.type === ChallengeType.Classify && (
                    <ClueAnalyzer onComplete={onSuccess} />
                )}
            </motion.div>
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default GameScreen;