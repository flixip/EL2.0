import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:5000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export interface AiChatRequest {
  query: string
}

export interface AiChatResponse {
  status: string
  answer: string
}

export const aiChat = async (request: AiChatRequest): Promise<AiChatResponse> => {
  const response = await api.post('/aiChat', request)
  return response.data
}

export default {
  aiChat
}

