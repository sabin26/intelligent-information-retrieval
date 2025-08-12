import React from 'react'
import { BrainCircuitIcon } from './icons'

const Header: React.FC = () => {
	return (
		<header className="bg-[#EAE5D9]/60 backdrop-blur-sm border-b-2 border-slate-700/10 shadow-sm sticky top-0 z-10">
			<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
				<div className="text-center flex items-center justify-center gap-4">
					<BrainCircuitIcon className="w-10 h-10 text-slate-700" />
					<div>
						<h1 className="text-4xl font-bold text-slate-800 tracking-wider font-display">
							Intelligent Information Retrieval
						</h1>
						<p className="mt-1 text-sm text-slate-500 tracking-widest font-bold">
							MODULE: ST7071CEM
						</p>
					</div>
				</div>
			</div>
		</header>
	)
}

export default Header
