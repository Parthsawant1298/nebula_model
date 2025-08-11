"use client"

import { useState, useEffect } from "react"

export default function DatasetGeneratorPage() {
  // No tabs needed since we only have tabular data generation
  return (
    <div className="min-h-screen bg-black stars-background">
      <div className="stars-container">
        <div className="stars"></div>
        <div className="stars2"></div>
        <div className="stars3"></div>
      </div>
      
      <header className="bg-transparent border-b border-purple-800">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="flex items-center">
            <div className="nebula-logo mr-3">
              <span className="text-3xl">✧</span>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-purple-300 nebula-glow">Nebula Dataset Generator</h1>
              <p className="text-purple-200">Create AI-powered tabular datasets with just a few clicks</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="cosmic-card">
          <TabularGenerator />
        </div>
      </main>

      <footer className="bg-transparent border-t border-purple-800 mt-12 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-purple-300 text-sm">
            Powered by <span className="nebula-glow">Nebula AI</span> | Your cosmic companion for data generation
          </p>
        </div>
      </footer>
      
      <style jsx>{`
        .stars-background {
          position: relative;
          overflow: hidden;
        }
        
        .stars-container {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          z-index: -1;
        }
        
        .stars, .stars2, .stars3 {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background-image: 
            radial-gradient(2px 2px at 20px 30px, #eef 100%, transparent),
            radial-gradient(2px 2px at 40px 70px, #fff 100%, transparent),
            radial-gradient(1px 1px at 90px 40px, #fff 100%, transparent),
            radial-gradient(2px 2px at 160px 120px, #ddf 100%, transparent);
          background-repeat: repeat;
          background-size: 200px 200px;
        }
        
        .stars {
          animation: starfield 6s linear infinite;
        }
        
        .stars2 {
          background-image: 
            radial-gradient(2px 2px at 100px 50px, #eef 100%, transparent),
            radial-gradient(2px 2px at 200px 150px, #fff 100%, transparent),
            radial-gradient(1px 1px at 300px 250px, #fff 100%, transparent),
            radial-gradient(2px 2px at 400px 350px, #ddf 100%, transparent);
          background-size: 400px 400px;
          animation: starfield 10s linear infinite;
        }
        
        .stars3 {
          background-image: 
            radial-gradient(1px 1px at 50px 80px, #eef 100%, transparent),
            radial-gradient(1px 1px at 150px 250px, #fff 100%, transparent),
            radial-gradient(1px 1px at 250px 200px, #fff 100%, transparent),
            radial-gradient(1px 1px at 350px 400px, #ddf 100%, transparent);
          background-size: 600px 600px;
          animation: starfield 15s linear infinite;
        }
        
        @keyframes starfield {
          from {
            transform: translateY(0);
          }
          to {
            transform: translateY(200px);
          }
        }
        
        .cosmic-card {
          background: rgba(13, 6, 32, 0.85);
          border-radius: 12px;
          box-shadow: 0 0 20px rgba(138, 75, 255, 0.2);
          border: 1px solid rgba(138, 75, 255, 0.3);
          backdrop-filter: blur(5px);
          overflow: hidden;
        }
        
        .nebula-glow {
          text-shadow: 0 0 10px rgba(162, 102, 255, 0.8);
        }
      `}</style>
    </div>
  )
}

function TabularGenerator() {
  const [tabularPrompt, setTabularPrompt] = useState("")
  const [numRows, setNumRows] = useState(100)
  const [includeHeader, setIncludeHeader] = useState(true)
  const [temperature, setTemperature] = useState(0.7)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [previewData, setPreviewData] = useState([])
  const [columns, setColumns] = useState([])
  const [rowCount, setRowCount] = useState(0)
  const [columnCount, setColumnCount] = useState(0)
  const [statistics, setStatistics] = useState({})
  const [insights, setInsights] = useState([])
  const [csvData, setCsvData] = useState("")
  const [successMessage, setSuccessMessage] = useState("")
  const [buttonAnimating, setButtonAnimating] = useState(false)

  const handleGenerateTabular = async () => {
    if (!tabularPrompt) {
      setError("Please provide a description for the tabular dataset.")
      return
    }

    setError("")
    setLoading(true)
    setButtonAnimating(true)
    setPreviewData([])
    setColumns([])
    setRowCount(0)
    setColumnCount(0)
    setStatistics({})
    setInsights([])
    setCsvData("")
    setSuccessMessage("")

    try {
      const response = await fetch("http://localhost:5004/api/generate-tabular", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: tabularPrompt,
          numRows,
          includeHeader,
          temperature
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || "Failed to generate tabular data")
      }

      setSuccessMessage(data.message)
      setPreviewData(data.previewData || [])
      setColumns(data.columns?.map(col => col.name) || [])
      setRowCount(data.rowCount || 0)
      setColumnCount(data.columnCount || 0)
      setStatistics(data.statistics || {})
      setInsights(data.insights || [])
      setCsvData(data.csvData || "")
      
      // Scroll to results
      setTimeout(() => {
        const previewElement = document.getElementById('dataset-preview')
        if (previewElement) {
          previewElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }
      }, 200)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
      // Keep the animation going for a bit longer to make it look nice
      setTimeout(() => setButtonAnimating(false), 500)
    }
  }

  const handleDownloadCsv = () => {
    if (!csvData) return

    const link = document.createElement("a")
    link.href = `data:text/csv;base64,${csvData}`
    
    // Create a more descriptive filename based on the prompt
    const cleanPrompt = tabularPrompt.toLowerCase().replace(/[^a-z0-9]/g, '_').substring(0, 30)
    const timestamp = new Date().toISOString().replace(/[-:]/g, '').split('.')[0]
    link.download = `nebula_${cleanPrompt}_${timestamp}.csv`
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <div className="text-purple-100 p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-purple-200 nebula-glow mb-3">Cosmic Data Generator</h2>
        <p className="text-purple-300">
          Describe the dataset you need, and Nebula's AI will create it for you. Generate realistic tabular data for projects, 
          tests, or demonstrations without the hassle of manual creation.
        </p>
      </div>

      {/* Input Form */}
      <div className="cosmic-panel mb-8">
        <div className="mb-5">
          <label className="block text-sm font-medium text-purple-200 mb-2">
            Describe the tabular dataset you want to generate:
          </label>
          <textarea
            className="w-full px-4 py-3 bg-purple-900/30 text-purple-100 border border-purple-700 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 placeholder-purple-400"
            rows={4}
            placeholder="Example: Create a dataset of e-commerce customer transactions with customer ID, name, purchase amount, product category, purchase date, and payment method."
            value={tabularPrompt}
            onChange={(e) => setTabularPrompt(e.target.value)}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-purple-200 mb-2">Number of rows:</label>
            <div className="relative">
              <input
                type="number"
                min="10"
                max="500"
                className="w-full px-4 py-2 bg-purple-900/30 text-purple-100 border border-purple-700 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                value={numRows}
                onChange={(e) => setNumRows(Math.min(500, Math.max(10, Number.parseInt(e.target.value) || 10)))}
              />
              <div className="absolute inset-y-0 right-0 pr-3 flex items-center text-purple-400 text-xs">
                Max: 500
              </div>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-purple-200 mb-2">Creativity (Temperature):</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              className="w-full appearance-none h-2 bg-purple-900 rounded-lg outline-none slider-thumb"
              value={temperature}
              onChange={(e) => setTemperature(Number.parseFloat(e.target.value))}
            />
            <div className="flex justify-between text-xs text-purple-400 mt-1">
              <span>Predictable</span>
              <span>{temperature.toFixed(1)}</span>
              <span>Creative</span>
            </div>
          </div>
        </div>
        
        <div className="mt-4 flex items-center">
          <input
            id="include-header"
            type="checkbox"
            className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-purple-300 rounded"
            checked={includeHeader}
            onChange={(e) => setIncludeHeader(e.target.checked)}
          />
          <label htmlFor="include-header" className="ml-2 block text-sm text-purple-200">
            Include header row
          </label>
        </div>
      </div>

      {/* Action Button */}
      <div className="mb-8 flex justify-center">
        <button
          className={`px-6 py-3 rounded-md text-white font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-purple-900 focus:ring-purple-500 transform transition-all ${
            buttonAnimating ? "nebula-pulse scale-105" : "hover:scale-105 hover:shadow-glow"
          } ${loading || !tabularPrompt ? "opacity-70 cursor-not-allowed" : "nebula-button"}`}
          onClick={handleGenerateTabular}
          disabled={loading || !tabularPrompt}
        >
          {loading ? (
            <span className="flex items-center">
              <svg
                className="animate-spin -ml-1 mr-2 h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Generating Cosmic Data...
            </span>
          ) : (
            <span className="flex items-center">
              <svg
                className="mr-2 h-5 w-5"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              Generate Dataset
            </span>
          )}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 cosmic-error-panel">
          <div className="flex items-start">
            <svg
              className="h-5 w-5 text-red-300 mt-0.5 mr-2"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Success Message */}
      {successMessage && (
        <div className="mb-6 cosmic-success-panel">
          <div className="flex items-start">
            <svg
              className="h-5 w-5 text-green-300 mt-0.5 mr-2"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
            <span>{successMessage}</span>
          </div>
        </div>
      )}

      {/* Dataset Insights */}
      {insights.length > 0 && (
        <div className="mb-8">
          <h3 className="text-lg font-medium text-purple-200 mb-2">✨ AI Insights</h3>
          <div className="cosmic-panel">
            <ul className="space-y-2">
              {insights.map((insight, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-purple-400 mr-2">•</span>
                  <span>{insight}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Dataset Preview */}
      {previewData.length > 0 && (
        <div className="mb-8" id="dataset-preview">
          <h3 className="text-lg font-medium text-purple-200 mb-2">
            🔮 Dataset Preview ({rowCount} rows, {columnCount} columns)
          </h3>
          <div className="overflow-x-auto cosmic-panel-alt">
            <table className="min-w-full divide-y divide-purple-800">
              <thead>
                <tr>
                  {columns.map((column, index) => (
                    <th
                      key={index}
                      scope="col"
                      className="px-6 py-3 text-left text-xs font-medium text-purple-300 uppercase tracking-wider"
                    >
                      {column}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-purple-800/50">
                {previewData.map((row, rowIndex) => (
                  <tr key={rowIndex} className="hover:bg-purple-900/30">
                    {columns.map((column, colIndex) => (
                      <td key={colIndex} className="px-6 py-4 whitespace-nowrap text-sm">
                        {row[column] !== null && row[column] !== undefined ? String(row[column]) : "-"}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          <div className="text-xs text-purple-400 mt-2 text-right">
            Showing {Math.min(previewData.length, 10)} of {rowCount} rows
          </div>
        </div>
      )}

      {/* Download Button */}
      {csvData && (
        <div className="mt-8 flex justify-center">
          <button
            onClick={handleDownloadCsv}
            className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-purple-900 focus:ring-indigo-500 transition-all duration-200 hover:scale-105 flex items-center shadow-glow-indigo"
          >
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
              ></path>
            </svg>
            Download CSV Dataset
          </button>
        </div>
      )}
      
      <style jsx>{`
        .cosmic-panel {
          background: rgba(45, 15, 85, 0.3);
          border-radius: 8px;
          padding: 16px;
          border: 1px solid rgba(138, 75, 255, 0.2);
        }
        
        .cosmic-panel-alt {
          background: rgba(30, 10, 60, 0.4);
          border-radius: 8px;
          border: 1px solid rgba(138, 75, 255, 0.2);
        }
        
        .cosmic-error-panel {
          background: rgba(80, 20, 20, 0.3);
          border-radius: 8px;
          padding: 12px;
          border: 1px solid rgba(255, 100, 100, 0.3);
          color: #ffc0c0;
        }
        
        .cosmic-success-panel {
          background: rgba(20, 80, 40, 0.3);
          border-radius: 8px;
          padding: 12px;
          border: 1px solid rgba(100, 255, 150, 0.3);
          color: #c0ffd0;
        }
        
        .nebula-button {
          background: linear-gradient(135deg, #9c42f5 0%, #6d28d9 100%);
        }
        
        .nebula-pulse {
          animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
          background: linear-gradient(135deg, #9c42f5 0%, #6d28d9 100%);
        }
        
        @keyframes pulse {
          0%, 100% {
            opacity: 1;
            background-position: 0% 50%;
          }
          50% {
            opacity: 0.8;
            background-position: 100% 50%;
          }
        }
        
        .shadow-glow {
          box-shadow: 0 0 15px rgba(138, 75, 255, 0.5);
        }
        
        .shadow-glow-indigo {
          box-shadow: 0 0 15px rgba(99, 102, 241, 0.5);
        }
        
        /* Slider thumb styling */
        .slider-thumb::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 18px;
          height: 18px;
          border-radius: 50%;
          background: #9c42f5;
          cursor: pointer;
          box-shadow: 0 0 5px rgba(138, 75, 255, 0.8);
        }
        
        .slider-thumb::-moz-range-thumb {
          width: 18px;
          height: 18px;
          border-radius: 50%;
          background: #9c42f5;
          cursor: pointer;
          box-shadow: 0 0 5px rgba(138, 75, 255, 0.8);
        }
      `}</style>
    </div>
  )
}