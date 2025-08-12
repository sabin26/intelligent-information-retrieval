import React from 'react'
import { motion } from 'framer-motion'
import { CheckCircleIcon } from './icons'

interface TasksCompleteScreenProps {
	onRestart: () => void
}

const TasksCompleteScreen: React.FC<TasksCompleteScreenProps> = ({
	onRestart,
}) => {
	return (
		<motion.div
			initial={{ opacity: 0, scale: 0.8 }}
			animate={{ opacity: 1, scale: 1 }}
			transition={{
				type: 'spring',
				stiffness: 100,
				damping: 10,
				delay: 0.2,
			}}
			className="bg-white/70 backdrop-blur-sm p-8 rounded-lg shadow-2xl border-2 border-slate-700/10 text-center"
		>
			<motion.div
				initial={{ scale: 0, opacity: 0 }}
				animate={{ scale: 1, opacity: 1 }}
				transition={{ type: 'spring', delay: 0.3 }}
			>
				<CheckCircleIcon className="w-24 h-24 text-green-500 mx-auto" />
			</motion.div>

			<h2 className="text-3xl font-bold font-display text-slate-800 tracking-wide z-10 relative mt-4">
				Tasks Complete
			</h2>
			<p className="mt-2 text-slate-600 z-10 relative">
				You have successfully demonstrated both tasks.
			</p>

			<motion.button
				whileHover={{ scale: 1.05 }}
				whileTap={{ scale: 0.95 }}
				onClick={onRestart}
				className="mt-8 px-8 py-3 bg-slate-800 text-white font-bold rounded-lg shadow-md hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-500 transition-colors font-display tracking-wider z-10 relative"
			>
				Restart Demonstration
			</motion.button>
		</motion.div>
	)
}

export default TasksCompleteScreen
