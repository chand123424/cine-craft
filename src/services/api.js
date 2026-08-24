import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

export const projectService = {
  list: () => api.get('/api/projects'),
  get: (id) => api.get(`/api/projects/${id}`),
  create: (payload) => api.post('/api/projects', payload),
}

export const scriptService = {
  generate: (payload) => api.post('/api/scripts/generate', payload),
  get: (projectId) => api.get(`/api/scripts/${projectId}`),
  update: (id, payload) => api.put(`/api/scripts/${id}`, payload),
  approve: (id) => api.post(`/api/scripts/${id}/approve`),
  regenerate: (id) => api.post(`/api/scripts/${id}/regenerate`),
}

export const sceneService = {
  generate: (payload) => api.post('/api/scenes/generate', payload),
  get: (projectId) => api.get(`/api/scenes/${projectId}`),
  update: (id, payload) => api.put(`/api/scenes/${id}`, payload),
  approve: (id) => api.post(`/api/scenes/${id}/approve`),
  regenerate: (id) => api.post(`/api/scenes/${id}/regenerate`),
}

export const mediaService = {
  generateImage: (payload) => api.post('/api/media/image/generate', payload),
  generateAudio: (payload) => api.post('/api/media/audio/generate', payload),
  regenerate: (id, payload) => api.post(`/api/media/${id}/regenerate`, payload),
}

export const videoService = {
  create: (payload) => api.post('/api/videos/create', payload),
  get: (projectId) => api.get(`/api/videos/${projectId}`),
}
