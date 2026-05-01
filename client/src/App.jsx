import { useState } from 'react'

function App() {
  const [serverResponse, setServerResponse] = useState('')
  const [loading, setLoading] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploadStatus, setUploadStatus] = useState('')
  const [uploading, setUploading] = useState(false)

  const fetchServerTest = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/test')
      const data = await response.json()
      setServerResponse(data.message)
    } catch (error) {
      setServerResponse('Error: Could not connect to server')
      console.error('Error:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFileChange = (event) => {
    const file = event.target.files[0]
    if (file && (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf'))) {
      setSelectedFile(file)
      setUploadStatus('')
    } else {
      setSelectedFile(null)
      setUploadStatus('Please select a valid PDF file')
    }
  }

  const handleUploadPDF = async () => {
    if (!selectedFile) {
      setUploadStatus('Please select a PDF file first')
      return
    }

    setUploading(true)
    setUploadStatus('Uploading...')

    const formData = new FormData()
    formData.append('pdf', selectedFile)

    try {
      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData
      })

      let data = null
      try {
        data = await response.json()
      } catch (parseError) {
        console.error('Failed to parse upload response as JSON', parseError)
      }

      if (response.ok) {
        setUploadStatus(`Success: ${data?.message || 'PDF uploaded successfully'}`)
        console.log('Upload successful:', data)
        setSelectedFile(null)
        document.getElementById('pdf-input').value = ''
      } else {
        const errorMessage = data?.error || data?.message || response.statusText || 'Upload failed'
        setUploadStatus(`Error: ${errorMessage}`)
        console.error('Upload error:', errorMessage, data)
      }
    } catch (error) {
      setUploadStatus('Error: Failed to upload PDF')
      console.error('Upload error:', error)
    } finally {
      setUploading(false)
    }
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

        <div className="mb-6">
          <input
            id="pdf-input"
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            className="w-full mb-4 p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            onClick={handleUploadPDF}
            disabled={uploading || !selectedFile}
            className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-semibold py-3 px-4 rounded-lg transition duration-200"
          >
            {uploading ? '📤 Uploading...' : '📄 Upload PDF'}
          </button>
          {uploadStatus && (
            <div className={`mt-4 p-4 rounded-lg ${
              uploadStatus.includes('Success') 
                ? 'bg-green-50 border border-green-200 text-green-800' 
                : 'bg-red-50 border border-red-200 text-red-800'
            }`}>
              <p className="font-medium">{uploadStatus}</p>
            </div>
          )}
        </div>

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
