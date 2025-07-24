import React, { useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { DocumentIcon, FolderIcon, TrashIcon } from '@heroicons/react/24/outline'
import { useMutation, useQuery } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import api from '../services/api'

const DocumentManager = () => {
  const [selectedCollection, setSelectedCollection] = useState('all')
  const [documents, setDocuments] = useState([])
  
  // Fetch documents
  const { data: collections } = useQuery({
    queryKey: ['collections'],
    queryFn: api.getCollections
  })
  
  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: api.uploadDocuments,
    onSuccess: (data) => {
      toast.success(`${data.count} documents uploaded successfully`)
      queryClient.invalidateQueries(['documents'])
    },
    onError: (error) => {
      toast.error(`Upload failed: ${error.message}`)
    }
  })
  
  // Dropzone configuration
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc', '.docx'],
      'text/plain': ['.txt']
    },
    onDrop: (acceptedFiles) => {
      uploadMutation.mutate(acceptedFiles)
    }
  })
  
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4 flex items-center">
          <DocumentIcon className="w-8 h-8 mr-2 text-indigo-600" />
          Document Manager
        </h2>
        
        {/* Upload Zone */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-indigo-400'
          }`}
        >
          <input {...getInputProps()} />
          <DocumentIcon className="w-16 h-16 mx-auto mb-4 text-gray-400" />
          {isDragActive ? (
            <p className="text-lg">Drop the documents here...</p>
          ) : (
            <div>
              <p className="text-lg mb-2">Drag & drop documents here</p>
              <p className="text-sm text-gray-500">or click to select files</p>
              <p className="text-xs text-gray-400 mt-2">Supports PDF, DOCX, TXT</p>
            </div>
          )}
        </div>
        
        {/* Collections */}
        <div className="mt-8">
          <h3 className="text-lg font-semibold mb-4">Collections</h3>
          <div className="grid grid-cols-3 gap-4">
            {collections?.map((collection) => (
              <button
                key={collection.id}
                onClick={() => setSelectedCollection(collection.id)}
                className={`p-4 rounded-lg border-2 transition-all ${
                  selectedCollection === collection.id
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-gray-200 hover:border-indigo-300'
                }`}
              >
                <FolderIcon className="w-8 h-8 mb-2 mx-auto text-indigo-600" />
                <p className="font-medium">{collection.name}</p>
                <p className="text-sm text-gray-500">{collection.count} documents</p>
              </button>
            ))}
          </div>
        </div>
        
        {/* Document List */}
        <div className="mt-8">
          <h3 className="text-lg font-semibold mb-4">Recent Documents</h3>
          <div className="space-y-2">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100"
              >
                <div className="flex items-center">
                  <DocumentIcon className="w-5 h-5 mr-3 text-gray-600" />
                  <div>
                    <p className="font-medium">{doc.name}</p>
                    <p className="text-sm text-gray-500">
                      {doc.size} • {doc.uploadedAt}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(doc.id)}
                  className="p-2 text-red-600 hover:bg-red-50 rounded"
                >
                  <TrashIcon className="w-5 h-5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default DocumentManager