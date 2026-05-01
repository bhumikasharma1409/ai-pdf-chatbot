import { useState } from 'react'

function App() {
  const [serverResponse, setServerResponse] = useState('')
  const [loading, setLoading] = useState(false)

  const fetchServerTest = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:5000/api/test')
      const data = await response.json()
      setServerResponse(data.message)
    } catch (error) {
      setServerResponse('Error: Could not connect to server')
      console.error('Error:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUploadPDF = () => {
    alert('PDF Upload feature coming soon!')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl p-8 max-w-md w-full">
        <h1 className="text-4xl font-bold text-center text-indigo-600 mb-2">
          AI PDF Chatbot
        </h1>
        <p className="text-center text-gray-600 mb-8">
          Upload and chat with your PDF documents
        </p>

        <button
          onClick={handleUploadPDF}
          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-4 rounded-lg transition duration-200 mb-6"
        >
          📄 Upload PDF
        </button>

        <div className="border-t pt-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            Server Status
          </h2>
          <button
            onClick={fetchServerTest}
            disabled={loading}
            className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-semibold py-2 px-4 rounded-lg transition duration-200"
          >
            {loading ? 'Checking...' : 'Test Connection'}
          </button>

          {serverResponse && (
            <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-800 font-medium">✓ {serverResponse}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
