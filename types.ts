export enum AppStatus {
	Intro = 'INTRO',
	Task1 = 'TASK_1',
	Task2 = 'TASK_2',
	Complete = 'COMPLETE',
}

export enum DocCategory {
	Politics = 'Politics',
	Business = 'Business',
	Health = 'Health',
	Unknown = 'Unknown',
}

export interface Author {
	name: string
	profileUrl?: string
}

export interface Publication {
	title: string
	authors: Author[]
	date: string
	publicationUrl: string
	relevancyScore?: number
}

export interface TaskData {
	id: string
	title: string
	description: string
}

export interface ClassificationResult {
	category: DocCategory
	confidence: number
}
