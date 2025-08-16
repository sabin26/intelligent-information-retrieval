import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { DocCategory, ClassificationResult } from '../types'
import { BrainCircuitIcon } from './icons'
import Loader from './Loader'
import Alert from './Alert'
import { classifyDocument } from '../services/apiService'

interface Task2Props {
	onComplete: () => void
}

const Task2_DocumentClassifier: React.FC<Task2Props> = ({ onComplete }) => {
	const [documentText, setDocumentText] = useState<string>('')
	const [result, setResult] = useState<ClassificationResult | null>(null)
	const [isLoading, setIsLoading] = useState<boolean>(false)
	const [classified, setClassified] = useState<boolean>(false)
	const [error, setError] = useState<string | null>(null)

	const handleClassify = async () => {
		if (!documentText.trim()) return
		setIsLoading(true)
		setResult(null)
		setError(null)
		try {
			const classificationResult = await classifyDocument(documentText)
			setResult(classificationResult)
			setClassified(true)
		} catch (err) {
			setError(
				err instanceof Error
					? err.message
					: 'An unknown error occurred.'
			)
			setClassified(false)
		} finally {
			setIsLoading(false)
		}
	}

	const handleResetClassification = () => {
		setDocumentText('')
		setResult(null)
		setClassified(false)
		setError(null)
	}

	const getResultBadgeClass = (category: DocCategory | undefined) => {
		switch (category) {
			case DocCategory.Health:
				return 'bg-emerald-100 text-emerald-800'
			case DocCategory.Business:
				return 'bg-sky-100 text-sky-800'
			case DocCategory.Politics:
				return 'bg-purple-100 text-purple-800'
			default:
				return 'bg-slate-100 text-slate-800'
		}
	}

	return (
		<div className="bg-white/80 backdrop-blur-sm p-6 sm:p-8 rounded-lg shadow-lg border border-slate-200/80">
			<h3 className="text-xl font-bold text-slate-800 font-display tracking-wide">
				Task 2: Document Classification
			</h3>
			<p className="text-sm text-slate-600 mt-1 mb-6">
				Enter a document (e.g., a sentence or paragraph) to classify it
				into one of the existing categories: Politics, Business, or
				Health.
			</p>

			<div className="mb-6">
				<div className="inline-flex items-center bg-sky-100 text-sky-800 text-sm font-bold px-4 py-2 rounded-full shadow-sm">
					Naive Bayes Classifier + K-Fold Cross Validation
				</div>
			</div>

			<div className="space-y-4">
				<textarea
					value={documentText}
					onChange={(e) => setDocumentText(e.target.value)}
					placeholder="Paste or type your document here..."
					className="w-full h-40 p-3 border border-slate-400 rounded-md shadow-inner bg-slate-50 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 transition disabled:opacity-60 disabled:bg-slate-100"
					disabled={isLoading || classified}
				/>
				<motion.button
					onClick={handleClassify}
					className="w-full flex items-center justify-center px-6 py-3 bg-slate-800 text-white font-semibold rounded-md shadow-md hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-500 transition disabled:opacity-50 disabled:cursor-not-allowed"
					disabled={isLoading || classified || !documentText.trim()}
					whileHover={{ y: -2 }}
					whileTap={{ scale: 0.98 }}
				>
					{isLoading ? (
						<Loader isButtonLoader />
					) : (
						<>
							<BrainCircuitIcon className="w-5 h-5 mr-2" />
							<span>Classify Document</span>
						</>
					)}
				</motion.button>
			</div>

			{error && (
				<div className="mt-4">
					<Alert message={error} />
				</div>
			)}

			<AnimatePresence>
				{result && (
					<motion.div
						initial={{ opacity: 0, y: 10 }}
						animate={{ opacity: 1, y: 0 }}
						exit={{ opacity: 0 }}
						className="mt-8 pt-6 border-t border-slate-200"
					>
						<h3 className="text-lg font-medium text-slate-800 mb-3">
							Classification Result
						</h3>
						<div className="text-center bg-slate-50 p-6 rounded-lg">
							<p className="text-sm text-slate-500 mb-2">
								The document is classified as:
							</p>
							<span
								className={`px-6 py-2 text-lg font-bold rounded-full inline-block ${getResultBadgeClass(
									result.category
								)}`}
							>
								{result.category}
							</span>
							{result.confidence && (
								<div className="mt-4">
									<p className="text-xs text-slate-500">
										Classification Confidence
									</p>
									<p className="font-bold text-lg text-slate-700">
										{(result.confidence * 100).toFixed(1)}%
									</p>
								</div>
							)}
						</div>
					</motion.div>
				)}
			</AnimatePresence>

			{classified && !isLoading && (
				<div className="text-center mt-8 flex justify-center gap-4">
					<motion.button
						onClick={handleResetClassification}
						className="px-8 py-3 bg-slate-600 text-white font-bold rounded-lg shadow-md hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-500 transition-colors font-display tracking-wider"
						whileHover={{ scale: 1.05 }}
						whileTap={{ scale: 0.95 }}
					>
						Classify Another
					</motion.button>
					<motion.button
						onClick={onComplete}
						className="px-8 py-3 bg-amber-600 text-white font-bold rounded-lg shadow-md hover:bg-amber-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-amber-500 transition-colors font-display tracking-wider"
						whileHover={{ scale: 1.05 }}
						whileTap={{ scale: 0.95 }}
					>
						Finish
					</motion.button>
				</div>
			)}
		</div>
	)
}

export default Task2_DocumentClassifier
