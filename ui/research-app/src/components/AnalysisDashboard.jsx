import React, { useState, useEffect } from 'react'
import { PlayIcon, PauseIcon, ChartBarIcon } from '@heroicons/react/24/outline'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { useQuery, useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import api from '../services/api'

const AnalysisDashboard = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [toolStatus, setToolStatus] = useState([])
  
  // Fetch current analysis status
  const { data: analysisStatus } = useQuery({
    queryKey: ['analysisStatus'],
    queryFn: api.getAnalysisStatus,
    refetchInterval: isAnalyzing ? 1000 : false
  })
  
  // Start analysis mutation
  const startAnalysis = useMutation({
    mutationFn: api.startAnalysis,
    onSuccess: () => {
      setIsAnalyzing(true)
      toast.success('Analysis started')
    }
  })
  
  // Update progress
  useEffect(() => {
    if (analysisStatus) {
      setProgress(analysisStatus.progress)
      setToolStatus(analysisStatus.toolStatus || [])
      if (analysisStatus.status === 'completed') {
        setIsAnalyzing(false)
        toast.success('Analysis completed!')
      }
    }
  }, [analysisStatus])
  
  const performanceData = [
    { name: 'PDF Loader', time: 0.45 },
    { name: 'NER Extraction', time: 1.23 },
    { name: 'Graph Builder', time: 0.87 },
    { name: 'PageRank', time: 2.15 },
    { name: 'Query Engine', time: 0.32 }
  ]
  
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4 flex items-center">
          <ChartBarIcon className="w-8 h-8 mr-2 text-indigo-600" />
          Real-Time Analysis Dashboard
        </h2>
        
        {/* Progress Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Analysis Progress</h3>
            <button
              onClick={() => startAnalysis.mutate()}
              disabled={isAnalyzing}
              className={`flex items-center px-4 py-2 rounded-lg transition-colors ${
                isAnalyzing
                  ? 'bg-red-500 hover:bg-red-600 text-white'
                  : 'bg-indigo-600 hover:bg-indigo-700 text-white'
              }`}
            >
              {isAnalyzing ? (
                <>
                  <PauseIcon className="w-5 h-5 mr-2" />
                  Pause Analysis
                </>
              ) : (
                <>
                  <PlayIcon className="w-5 h-5 mr-2" />
                  Start Analysis
                </>
              )}
            </button>
          </div>
          
          <div className="relative">
            <div className="w-full bg-gray-200 rounded-full h-6">
              <div
                className="bg-indigo-600 h-6 rounded-full transition-all duration-500 flex items-center justify-center"
                style={{ width: `${progress}%` }}
              >
                <span className="text-xs text-white font-medium">
                  {progress > 0 && `${progress}%`}
                </span>
              </div>
            </div>
          </div>
          
          <p className="mt-2 text-sm text-gray-600">
            {isAnalyzing ? 'Analysis in progress...' : 'Ready to analyze documents'}
          </p>
        </div>
        
        {/* Tool Status */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold mb-4">Tool Execution Status</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tool</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Items</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {toolStatus.map((tool, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {tool.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        tool.status === 'completed' ? 'bg-green-100 text-green-800' :
                        tool.status === 'running' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {tool.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {tool.time}s
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {tool.itemsProcessed || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        
        {/* Performance Chart */}
        <div>
          <h3 className="text-lg font-semibold mb-4">Tool Performance</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="time" fill="#6366f1" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AnalysisDashboard