import { useState, useCallback } from 'react'
import { AnimatePresence } from 'framer-motion'
import Header from './components/Header'
import { AppStatus } from './types'
import IntroScreen from './components/IntroScreen'
import Task1_SearchEngine from './components/EvidenceFinder'
import Task2_DocumentClassifier from './components/ClueAnalyzer'
import TasksCompleteScreen from './components/CaseCompleteScreen'

function App() {
	const [appStatus, setAppStatus] = useState<AppStatus>(AppStatus.Intro)

	const startTasks = useCallback(() => {
		setAppStatus(AppStatus.Task1)
	}, [])

	const advanceToTask2 = useCallback(() => {
		setAppStatus(AppStatus.Task2)
	}, [])

	const finishTasks = useCallback(() => {
		setAppStatus(AppStatus.Complete)
	}, [])

	const restart = () => {
		setAppStatus(AppStatus.Intro)
	}

	const renderContent = () => {
		switch (appStatus) {
			case AppStatus.Intro:
				return <IntroScreen key="intro" onStart={startTasks} />
			case AppStatus.Task1:
				return (
					<Task1_SearchEngine
						key="task1"
						onComplete={advanceToTask2}
					/>
				)
			case AppStatus.Task2:
				return (
					<Task2_DocumentClassifier
						key="task2"
						onComplete={finishTasks}
					/>
				)
			case AppStatus.Complete:
				return (
					<TasksCompleteScreen key="complete" onRestart={restart} />
				)
			default:
				return <IntroScreen key="intro-default" onStart={startTasks} />
		}
	}

	return (
		<div className="min-h-screen bg-[#F4F1EA] flex flex-col">
			<Header />
			<main className="flex-grow max-w-4xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 flex items-center">
				<div className="w-full">
					<AnimatePresence mode="wait">
						{renderContent()}
					</AnimatePresence>
				</div>
			</main>
		</div>
	)
}

export default App
