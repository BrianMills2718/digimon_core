import React from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import DocumentManager from './components/DocumentManager'
import AnalysisDashboard from './components/AnalysisDashboard'
import GraphExplorer from './components/GraphExplorer'
import QueryBuilder from './components/QueryBuilder'
import ResultsExporter from './components/ResultsExporter'
import './App.css'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Toaster position="top-right" />
        <Layout>
          <Routes>
            <Route path="/" element={<DocumentManager />} />
            <Route path="/analysis" element={<AnalysisDashboard />} />
            <Route path="/graph" element={<GraphExplorer />} />
            <Route path="/query" element={<QueryBuilder />} />
            <Route path="/export" element={<ResultsExporter />} />
          </Routes>
        </Layout>
      </Router>
    </QueryClientProvider>
  )
}

export default App