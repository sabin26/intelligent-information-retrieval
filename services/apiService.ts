import { Publication, ClassificationResult, DocCategory } from '../types'

const API_BASE_URL = 'http://127.0.0.1:8000' // Default for FastAPI

export const searchPublications = async (
	query: string
): Promise<{ publications: Publication[] }> => {
	const params = new URLSearchParams({ q: query })
	try {
		const response = await fetch(
			`${API_BASE_URL}/search?${params.toString()}`
		)

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}))
			let errorMsg =
				errorData.detail ||
				errorData.message ||
				errorData.error ||
				`API request failed with status ${response.status}`

			// Check if errorData.detail is an array with msg field(s)
			if (
				Array.isArray(errorData.detail) &&
				errorData.detail.length > 0
			) {
				const firstMsg = errorData.detail[0]?.msg
				if (firstMsg) {
					errorMsg = firstMsg
				}
			}

			throw new Error(errorMsg)
		}

		const data = await response.json()
		const allPublications: Publication[] = data.results || []

		// Filter out publications with relevancy score that rounds to 0.00 when displayed with 2 decimal places
		const filteredPublications = allPublications.filter(
			(pub: Publication) =>
				Math.round(pub.relevancyScore * 100) / 100 > 0.0
		)

		return { publications: filteredPublications }
	} catch (error) {
		console.error('Error searching publications:', error)
		throw new Error(
			error instanceof Error
				? error.message
				: 'Failed to fetch publication data from the backend server. Is it running?'
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
		const response = await fetch(`${API_BASE_URL}/classify`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ text: documentText }),
		})

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}))
			let errorMsg =
				errorData.detail ||
				errorData.message ||
				errorData.error ||
				`API request failed with status ${response.status}`

			// Check if errorData.detail is an array with msg field(s)
			if (
				Array.isArray(errorData.detail) &&
				errorData.detail.length > 0
			) {
				const firstMsg = errorData.detail[0]?.msg
				if (firstMsg) {
					errorMsg = firstMsg
				}
			}

			throw new Error(errorMsg)
		}

		const result: ClassificationResult = await response.json()
		if (!Object.values(DocCategory).includes(result.category)) {
			return { ...result, category: DocCategory.Unknown }
		}
		return result
	} catch (error) {
		console.error('Error classifying document:', error)
		throw new Error(
			error instanceof Error
				? error.message
				: 'Failed to classify document. Is the backend server running?'
		)
	}
}
