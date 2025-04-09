import { useState } from 'react'
import { Button } from './ui/button'

interface Improvement {
  suggestions: string[]
  priority: string
  implementation: string
  risks: string[]
}

interface AnalysisResult {
  [key: string]: {
    improvements: Improvement[]
    error?: string
  }
}

export const AgentImprovement = () => {
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null)
  const [implementing, setImplementing] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const requestAnalysis = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch('/api/agent/analysis')
      const data = await response.json()
      setAnalysis(data)
    } catch (err) {
      setError('Failed to fetch analysis')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const implementImprovement = async (file: string, improvement: Improvement) => {
    try {
      setImplementing(prev => [...prev, file])
      const response = await fetch('/api/agent/improve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file,
          improvement
        })
      })
      
      const result = await response.json()
      
      if (result.error) {
        setError(`Implementation failed: ${result.error}`)
      } else {
        // Refresh analysis after successful implementation
        requestAnalysis()
      }
    } catch (err) {
      setError('Failed to implement improvement')
      console.error(err)
    } finally {
      setImplementing(prev => prev.filter(f => f !== file))
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Agent Selbstverbesserung</h2>
        <Button
          onClick={requestAnalysis}
          disabled={loading}
        >
          {loading ? 'Analysiere...' : 'Neue Analyse starten'}
        </Button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {analysis && (
        <div className="space-y-6">
          {Object.entries(analysis).map(([file, result]) => (
            <div key={file} className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-2">{file}</h3>
              
              {result.error ? (
                <div className="text-red-600">{result.error}</div>
              ) : (
                <div className="space-y-4">
                  {result.improvements.map((improvement, index) => (
                    <div key={index} className="border-l-4 border-blue-500 pl-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="font-medium">
                            Priorität: {improvement.priority}
                          </div>
                          <ul className="list-disc list-inside space-y-1">
                            {improvement.suggestions.map((suggestion, i) => (
                              <li key={i} className="text-sm">{suggestion}</li>
                            ))}
                          </ul>
                        </div>
                        <Button
                          onClick={() => implementImprovement(file, improvement)}
                          disabled={implementing.includes(file)}
                          size="sm"
                        >
                          {implementing.includes(file) ? 'Wird implementiert...' : 'Implementieren'}
                        </Button>
                      </div>
                      
                      {improvement.risks.length > 0 && (
                        <div className="mt-2">
                          <div className="text-sm font-medium text-red-600">Risiken:</div>
                          <ul className="list-disc list-inside space-y-1">
                            {improvement.risks.map((risk, i) => (
                              <li key={i} className="text-sm text-red-600">{risk}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      <div className="mt-2">
                        <div className="text-sm font-medium">Implementation:</div>
                        <pre className="text-sm bg-gray-100 p-2 rounded mt-1 overflow-x-auto">
                          {improvement.implementation}
                        </pre>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}