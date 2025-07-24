import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  DocumentTextIcon,
  ChartBarIcon,
  ShareIcon,
  MagnifyingGlassIcon,
  ArrowDownTrayIcon,
  BeakerIcon
} from '@heroicons/react/24/outline'

const Layout = ({ children }) => {
  const location = useLocation()
  
  const navigation = [
    { name: 'Documents', href: '/', icon: DocumentTextIcon },
    { name: 'Analysis', href: '/analysis', icon: ChartBarIcon },
    { name: 'Graph', href: '/graph', icon: ShareIcon },
    { name: 'Query', href: '/query', icon: MagnifyingGlassIcon },
    { name: 'Export', href: '/export', icon: ArrowDownTrayIcon },
  ]
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <BeakerIcon className="w-8 h-8 text-indigo-600 mr-3" />
              <h1 className="text-xl font-bold text-gray-900">KGAS Research UI</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">v1.0.0</span>
              <button className="text-gray-600 hover:text-gray-900">
                Settings
              </button>
            </div>
          </div>
        </div>
      </header>
      
      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {navigation.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.href
              
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center px-3 py-4 text-sm font-medium border-b-2 transition-colors ${
                    isActive
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-5 h-5 mr-2" />
                  {item.name}
                </Link>
              )
            })}
          </div>
        </div>
      </nav>
      
      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  )
}

export default Layout