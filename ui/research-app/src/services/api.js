import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor for auth
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('kgas_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('kgas_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

const apiService = {
  // Document management
  uploadDocuments: (files) => {
    const formData = new FormData()
    files.forEach(file => formData.append('documents', file))
    return api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  getDocuments: (params) => api.get('/documents', { params }),
  getCollections: () => api.get('/collections'),
  deleteDocument: (id) => api.delete(`/documents/${id}`),
  
  // Analysis
  startAnalysis: (config) => api.post('/analysis/start', config),
  getAnalysisStatus: () => api.get('/analysis/status'),
  stopAnalysis: () => api.post('/analysis/stop'),
  
  // Graph operations
  getGraph: (params) => api.get('/graph', { params }),
  getGraphStats: () => api.get('/graph/stats'),
  exportGraph: (format) => api.get(`/graph/export/${format}`),
  
  // Query operations
  executeQuery: (query) => api.post('/query/execute', { query }),
  getQueryTemplates: () => api.get('/query/templates'),
  saveQueryTemplate: (template) => api.post('/query/templates', template),
  
  // Export operations
  exportResults: (config) => api.post('/export/generate', config),
  getExportFormats: () => api.get('/export/formats'),
  getCitationStyles: () => api.get('/export/citation-styles')
}

export default apiService