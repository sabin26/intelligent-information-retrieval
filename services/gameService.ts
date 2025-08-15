import { TaskData } from '../types'

const taskData: TaskData = {
	id: 'ST7071CEM',
	title: 'Intelligent Information Retrieval Tasks',
	description:
		"This application demonstrates two primary tasks: a vertical search engine and a document classification system. The first task allows users to search for publications from Coventry University's FBL School of Economics, Finance and Accounting. The second task enables users to classify documents into categories such as Health, Business, and Politics.",
}

export const getTaskData = (): TaskData => {
	return taskData
}
