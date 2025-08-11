import { TaskData, DocCategory } from '../types';

const taskData: TaskData = {
    id: 'ST7071CEM',
    title: 'Intelligent Information Retrieval Tasks',
    description: 'This application demonstrates the two primary tasks required by the module coursework: creating a vertical search engine and a document classification system.',
    task1: {
        prompt: 'Your first task is to create a vertical search engine. For this demonstration, find publications related to "financial risk".',
        expectedKeywords: ['financial', 'risk'],
        mockPublications: [
            {
                title: 'Assessing Risk in Emerging Financial Markets',
                authors: [{ name: 'Dr. Evelyn Reed', profileUrl: '#' }],
                year: '2023',
                publicationUrl: '#',
                relevancyScore: 0.92,
            },
            {
                title: 'A Framework for Financial Risk Management in the Tech Sector',
                authors: [{ name: 'Dr. Evelyn Reed', profileUrl: '#' }, { name: 'Prof. Samuel Jones', profileUrl: '#' }],
                year: '2022',
                publicationUrl: '#',
                relevancyScore: 0.87,
            }
        ]
    }
};

export const getTaskData = (): TaskData => {
    return taskData;
};