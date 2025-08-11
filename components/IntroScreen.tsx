import React from 'react';
import { motion } from 'framer-motion';
import { BookIcon } from './icons';
import { getTaskData } from '../services/gameService';

interface IntroScreenProps {
  onStart: () => void;
}

const IntroScreen: React.FC<IntroScreenProps> = ({ onStart }) => {
  const taskDetails = getTaskData();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.5 }}
      className="bg-white/70 backdrop-blur-sm p-8 rounded-lg shadow-lg border-2 border-slate-700/10 text-center"
    >
      <BookIcon className="w-16 h-16 text-slate-500 mx-auto mb-4" />
      <h2 className="text-3xl font-bold font-display text-slate-800 tracking-wide">{taskDetails.title}</h2>
      <p className="mt-4 max-w-2xl mx-auto text-slate-600 leading-relaxed">{taskDetails.description}</p>
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={onStart}
        className="mt-8 px-8 py-3 bg-slate-800 text-white font-bold rounded-lg shadow-md hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-500 transition-colors font-display tracking-wider"
      >
        Begin Tasks
      </motion.button>
    </motion.div>
  );
};

export default IntroScreen;