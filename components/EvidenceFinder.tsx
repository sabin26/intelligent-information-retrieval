import React, { useState, useCallback, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Publication } from '../types'
import { SearchIcon, CheckCircleIcon, UserIcon, BookIcon } from './icons'
import { searchPublications } from '../services/apiService'
import Loader from './Loader'

interface Task1Props {
	onComplete: () => void
}

const PAGE_SIZE_OPTIONS = [10, 25, 50]

const Task1_SearchEngine: React.FC<Task1Props> = ({ onComplete }) => {
	const [query, setQuery] = useState('')
	const [isLoading, setIsLoading] = useState(false)
	const [error, setError] = useState<string | null>(null)
	const [foundPublications, setFoundPublications] = useState<Publication[]>(
		[]
	)
	const [searchAttempted, setSearchAttempted] = useState(false)
	const [currentPage, setCurrentPage] = useState(1)
	const [pageSize, setPageSize] = useState(PAGE_SIZE_OPTIONS[0])
	const [expandedAbstracts, setExpandedAbstracts] = useState<Set<string>>(
		new Set()
	)
	const componentRootRef = useRef<HTMLDivElement>(null)

	const handleSearch = useCallback(
		async (e: React.FormEvent) => {
			e.preventDefault()
			if (!query.trim()) return

			setSearchAttempted(true)
			setIsLoading(true)
			setError(null)
			setFoundPublications([])
			setCurrentPage(1)
			setExpandedAbstracts(new Set())

			try {
				const { publications } = await searchPublications(query)
				setFoundPublications(publications)
			} catch (err) {
				setError(
					err instanceof Error
						? err.message
						: 'An unknown error occurred.'
				)
			} finally {
				setIsLoading(false)
			}
		},
		[query]
	)

	const handleResetSearch = () => {
		setSearchAttempted(false)
		setFoundPublications([])
		setError(null)
		setQuery('')
		setCurrentPage(1)
		setExpandedAbstracts(new Set())
	}

	const handlePageSizeChange = (newPageSize: number) => {
		setPageSize(newPageSize)
		setCurrentPage(1) // Reset to first page when changing page size
	}

	const toggleAbstract = (publicationUrl: string) => {
		setExpandedAbstracts((prev) => {
			// If the clicked abstract is already expanded, collapse it
			if (prev.has(publicationUrl)) {
				return new Set()
			}
			// Otherwise, expand only this abstract (collapse all others)
			return new Set([publicationUrl])
		})
	}

	const truncateText = (text: string, maxLength: number = 150) => {
		if (text.length <= maxLength) return text
		return text.slice(0, maxLength) + '...'
	}

	// Pagination logic
	const totalPages = Math.ceil(foundPublications.length / pageSize)
	const startIndex = (currentPage - 1) * pageSize
	const endIndex = startIndex + pageSize
	const currentPublications = foundPublications.slice(startIndex, endIndex)

	const handlePageChange = (newPage: number) => {
		setCurrentPage(newPage)
	}

	useEffect(() => {
		if (searchAttempted) {
			componentRootRef.current?.scrollIntoView({
				behavior: 'smooth',
				block: 'start',
			})
		}
	}, [currentPage])

	return (
		<div
			ref={componentRootRef}
			className="bg-white/80 backdrop-blur-sm p-6 sm:p-8 rounded-lg shadow-lg border border-slate-200/80"
		>
			<h3 className="text-xl font-bold text-slate-800 font-display tracking-wide">
				Task 1: Vertical Search Engine
			</h3>
			<p className="text-sm text-slate-600 mt-1 mb-6">
				Find research papers, articles, and publications from Coventry
				University's FBL School of Economics, Finance and Accounting.
			</p>

			<div className="mb-6">
				<div className="inline-flex items-center bg-amber-100 text-amber-800 text-sm font-bold px-4 py-2 rounded-full shadow-sm">
					Crawling + Positional Indexing + TF-IDF Ranking with Cosine
					Similarity
				</div>
			</div>

			<form
				onSubmit={handleSearch}
				className="flex items-center gap-2 mb-6"
			>
				<div className="relative flex-grow">
					<div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
						<SearchIcon className="w-5 h-5 text-slate-400" />
					</div>
					<input
						type="text"
						value={query}
						onChange={(e) => setQuery(e.target.value)}
						placeholder="Search for publications..."
						className="w-full pl-10 pr-4 py-2.5 border border-slate-400 rounded-md shadow-inner bg-slate-50 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 transition disabled:opacity-60 disabled:bg-slate-100"
						disabled={isLoading}
					/>
				</div>
				<motion.button
					type="submit"
					className="px-6 py-2.5 bg-slate-800 text-white font-semibold rounded-md shadow-md hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-500 transition disabled:opacity-50 disabled:cursor-not-allowed"
					disabled={isLoading || !query.trim()}
					whileHover={{ scale: 1.05 }}
					whileTap={{ scale: 0.95 }}
				>
					{isLoading ? 'Searching...' : 'Search'}
				</motion.button>
			</form>

			<AnimatePresence>
				{isLoading && (
					<div className="flex justify-center py-4">
						<Loader />
					</div>
				)}

				{searchAttempted && !isLoading && error && (
					<p className="text-sm text-red-600 text-center mt-4">
						{error}
					</p>
				)}

				{searchAttempted &&
					!isLoading &&
					!error &&
					foundPublications.length === 0 && (
						<motion.div
							initial={{ opacity: 0, y: 10 }}
							animate={{ opacity: 1, y: 0 }}
							className="text-center py-10 px-4 bg-slate-50 rounded-lg mt-4"
						>
							<BookIcon className="w-12 h-12 text-slate-400 mx-auto mb-3" />
							<h3 className="text-lg font-medium text-slate-700">
								No Publications Found
							</h3>
							<p className="text-sm text-slate-500 mt-1">
								Try refining your search query for better
								results.
							</p>
						</motion.div>
					)}

				{searchAttempted && currentPublications.length > 0 && (
					<motion.div
						initial={{ opacity: 0, y: 10 }}
						animate={{ opacity: 1, y: 0 }}
						className="mt-6"
					>
						<div className="flex items-center justify-center gap-2 text-green-700 bg-green-100 p-3 rounded-md">
							<CheckCircleIcon className="w-6 h-6" />
							<p className="font-bold">
								Search Complete! {foundPublications.length}{' '}
								publication(s) found.
							</p>
						</div>

						{/* Page Size Selector */}
						<div className="flex items-center justify-between mt-4 pt-3 border-t border-slate-200">
							<div className="flex items-center gap-2">
								<span className="text-sm font-medium text-slate-600">
									Results per page:
								</span>
								<select
									value={pageSize}
									onChange={(e) =>
										handlePageSizeChange(
											Number(e.target.value)
										)
									}
									className="px-3 py-1 border border-slate-300 rounded-md text-sm focus:ring-2 focus:ring-amber-500 focus:border-amber-500 bg-white"
								>
									{PAGE_SIZE_OPTIONS.map((size) => (
										<option key={size} value={size}>
											{size}
										</option>
									))}
								</select>
							</div>
							<div className="text-sm text-slate-600">
								Showing {startIndex + 1}-
								{Math.min(endIndex, foundPublications.length)}{' '}
								of {foundPublications.length} results
							</div>
						</div>

						<div className="space-y-4 mt-4">
							{currentPublications.map((pub, index) => (
								<motion.div
									key={pub.publicationUrl}
									className="p-4 border border-slate-300 rounded-lg bg-white shadow"
									initial={{ opacity: 0, x: -20 }}
									animate={{ opacity: 1, x: 0 }}
									transition={{ delay: index * 0.15 }}
								>
									<div className="flex justify-between items-start">
										<a
											href={pub.publicationUrl}
											target="_blank"
											rel="noopener noreferrer"
											className="font-bold text-slate-800 hover:text-amber-700 pr-4"
										>
											{pub.title}
										</a>
										{pub.relevancyScore && (
											<div className="text-right flex-shrink-0">
												<span className="text-xs text-slate-500">
													Relevancy
												</span>
												<p className="font-bold text-amber-700">
													{pub.relevancyScore.toFixed(
														2
													)}
												</p>
											</div>
										)}
									</div>
									<p className="text-sm text-slate-500 mt-1">
										{pub.date}
									</p>
									<div className="mt-2 flex items-center gap-2 flex-wrap text-sm text-slate-700">
										<UserIcon className="w-4 h-4 text-slate-500" />
										{pub.authors.map((author, i) => (
											<span key={i}>
												{author.profileUrl ? (
													<a
														href={author.profileUrl}
														target="_blank"
														rel="noopener noreferrer"
														className="underline hover:text-amber-800"
													>
														{author.name}
													</a>
												) : (
													author.name
												)}
												{i < pub.authors.length - 1 &&
													', '}
											</span>
										))}
									</div>

									{pub.abstract && (
										<div className="mt-3 pt-3 border-t border-slate-200">
											<div className="text-sm text-slate-700">
												<span className="font-medium text-slate-600">
													Abstract:{' '}
												</span>
												{expandedAbstracts.has(
													pub.publicationUrl
												)
													? pub.abstract
													: truncateText(
															pub.abstract
													  )}
											</div>
											{pub.abstract.length > 150 && (
												<button
													onClick={() =>
														toggleAbstract(
															pub.publicationUrl
														)
													}
													className="text-xs text-amber-600 hover:text-amber-700 font-medium mt-1 focus:outline-none"
												>
													{expandedAbstracts.has(
														pub.publicationUrl
													)
														? 'Show less'
														: 'Show more'}
												</button>
											)}
										</div>
									)}
								</motion.div>
							))}
						</div>

						{totalPages > 1 && (
							<div className="flex justify-between items-center mt-6 pt-4 border-t border-slate-200">
								<button
									onClick={() =>
										handlePageChange(currentPage - 1)
									}
									disabled={currentPage === 1}
									className="px-4 py-2 bg-slate-200 text-slate-700 font-semibold rounded-md shadow-sm hover:bg-slate-300 disabled:opacity-50 disabled:cursor-not-allowed transition"
								>
									Previous
								</button>
								<span className="text-sm font-medium text-slate-600">
									Page {currentPage} of {totalPages}
								</span>
								<button
									onClick={() =>
										handlePageChange(currentPage + 1)
									}
									disabled={currentPage === totalPages}
									className="px-4 py-2 bg-slate-200 text-slate-700 font-semibold rounded-md shadow-sm hover:bg-slate-300 disabled:opacity-50 disabled:cursor-not-allowed transition"
								>
									Next
								</button>
							</div>
						)}
					</motion.div>
				)}
			</AnimatePresence>

			{searchAttempted && !isLoading && (
				<div className="text-center mt-8 flex justify-center gap-4">
					{foundPublications.length > 0 && (
						<motion.button
							onClick={onComplete}
							className="px-8 py-3 bg-amber-600 text-white font-bold rounded-lg shadow-md hover:bg-amber-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-amber-500 transition-colors font-display tracking-wider"
							whileHover={{ scale: 1.05 }}
							whileTap={{ scale: 0.95 }}
						>
							Proceed to Task 2
						</motion.button>
					)}
				</div>
			)}
		</div>
	)
}

export default Task1_SearchEngine
