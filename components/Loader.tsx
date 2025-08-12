import React from 'react'

interface LoaderProps {
	isButtonLoader?: boolean
}

const Loader: React.FC<LoaderProps> = ({ isButtonLoader = false }) => {
	const sizeClasses = isButtonLoader ? 'w-5 h-5 mr-2' : 'w-8 h-8'
	const borderClasses = isButtonLoader ? 'border-2' : 'border-4'

	return (
		<div
			className={`${sizeClasses} ${borderClasses} border-slate-400 border-t-amber-500 rounded-full animate-spin`}
			role="status"
		>
			<span className="sr-only">Loading...</span>
		</div>
	)
}

export default Loader
