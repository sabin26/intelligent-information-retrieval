import { GoogleGenAI, Type, GenerateContentResponse } from '@google/genai'
import {
	Publication,
	GroundingMetadata,
	ClassificationResult,
	DocCategory,
} from '../types'

if (!process.env.API_KEY) {
	throw new Error('API_KEY environment variable not set')
}

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY })

const classificationSchema = {
	type: Type.OBJECT,
	properties: {
		category: {
			type: Type.STRING,
			enum: [
				DocCategory.Politics,
				DocCategory.Business,
				DocCategory.Health,
			],
			description: 'The classification category of the document.',
		},
	},
	required: ['category'],
}

export const searchPublications = async (
	query: string
): Promise<{
	publications: Publication[]
	groundingMetadata?: GroundingMetadata
}> => {
	try {
		const prompt = `
            You are an expert academic research assistant. Your task is to find publications from Coventry University's School of Economics, Finance and Accounting based on a user's query.

            You must use the provided search tools to look for information exclusively within the 'https://pureportal.coventry.ac.uk/en/organisations/fbl-school-of-economics-finance-and-accounting' domain and its subpages.

            For each relevant publication you find that matches the query "${query}", you must extract the following information:
            1.  title: The full title of the publication.
            2.  authors: A list of authors. For each author, provide their name and, if possible, a link to their profile on the pureportal.coventry.ac.uk website.
            3.  year: The year of publication as a string.
            4.  publicationUrl: The direct URL to the publication's page on the pureportal.coventry.ac.uk website.

            Return the findings as a single JSON array. Each element in the array is an object with keys "title", "authors", "year", and "publicationUrl". The "authors" key should have a value of an array of objects, where each object has a "name" and an optional "profileUrl".
            Do not add any text before or after the JSON array. Do not use markdown backticks.
            If no publications are found, return an empty array [].
        `

		const response: GenerateContentResponse =
			await ai.models.generateContent({
				model: 'gemini-2.5-flash',
				contents: prompt,
				config: {
					tools: [{ googleSearch: {} }],
				},
			})

		const groundingMetadata = response.candidates?.[0]
			?.groundingMetadata as GroundingMetadata | undefined

		let publications: Publication[] = []
		const responseText = response.text.trim()

		if (responseText) {
			try {
				// The model might still wrap the JSON in markdown
				const jsonMatch = responseText.match(
					/```(?:json)?\n([\s\S]*?)\n```/
				)
				const jsonString = jsonMatch ? jsonMatch[1] : responseText
				publications = JSON.parse(jsonString)
			} catch (e) {
				console.error(
					'Failed to parse JSON from Gemini response:',
					e,
					'Raw response:',
					responseText
				)
				throw new Error(
					'The model returned an unexpected response format. Could not parse publication data.'
				)
			}
		}

		return { publications, groundingMetadata }
	} catch (error) {
		console.error('Error searching publications:', error)
		if (
			error instanceof Error &&
			error.message.includes('unexpected response format')
		) {
			throw error
		}
		throw new Error(
			'Failed to fetch publication data from the Gemini API. Please check the console for details.'
		)
	}
}

export const classifyDocument = async (
	documentText: string
): Promise<ClassificationResult> => {
	if (!documentText.trim()) {
		throw new Error('Document text cannot be empty.')
	}

	try {
		const prompt = `
            You are a highly accurate document classification engine. Your sole purpose is to classify a given text into one of the following three categories: "Politics", "Business", or "Health".
            Analyze the provided text carefully and determine the most appropriate category.
            Return your response as a JSON object that strictly adheres to the provided schema, containing only the determined category.
            Text to classify:
            ---
            ${documentText}
            ---
        `

		const response = await ai.models.generateContent({
			model: 'gemini-2.5-flash',
			contents: prompt,
			config: {
				responseMimeType: 'application/json',
				responseSchema: classificationSchema,
			},
		})

		const result: ClassificationResult = JSON.parse(response.text)
		if (!Object.values(DocCategory).includes(result.category)) {
			return { category: DocCategory.Unknown }
		}
		return result
	} catch (error) {
		console.error('Error classifying document:', error)
		throw new Error(
			'Failed to classify document using the Gemini API. Please check the console for details.'
		)
	}
}
