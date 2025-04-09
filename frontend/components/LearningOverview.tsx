import { useState, useEffect } from 'react'
import { Button } from './ui/button'

interface LearningMetrics {
  totalInteractions: number
  successRate: number
  averageResponseTime: number
  commonPatterns: string[]
  recentLearnings: Array<{
    timestamp: string
    type: string
    summary: string
  }>
}

interface ImprovementPlan {
  patterns: string[]
  challenges: string[]
  improvements: Array<{
    area: string
    suggestions: string[]
    priority: 'high' | 'medium' | 'low'
  }>
  implementation: Array<{
    file: string
    changes: string
    risk: string
  }>
}

export const LearningOverview = () => {
  const [metrics, setMetrics] = useState<LearningMetrics | null>(null)
  const [plan, setPlan] = useState<ImprovementPlan | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchImprovementPlan = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch('/api/agent/improvement-plan')
      const data = await response.json()
      setPlan(data)
    } catch (err) {
      setError('Failed to fetch improvement plan')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const implementImprovement = async (file: string, changes: string) => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch('/api/agent/improve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target_file: file,
          improvement_type: 'implement',
          changes
        })
      })
      
      const result = await response.json()
      if (result.error) {
        setError(result.error)
      } else {
        // Refresh the improvement plan after successful implementation
        fetchImprovementPlan()
      }
    } catch (err) {
      setError('Failed to implement improvement')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Lernfortschritt & Verbesserungen</h2>
        <Button
          onClick={fetchImprovementPlan}
          disabled={loading}
        >
          {loading ? 'Lade...' : 'Verbesserungsplan generieren'}
        </Button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {metrics && (
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="font-semibold mb-2">Interaktionsstatistiken</h3>
            <div className="space-y-2">
              <div>Gesamtinteraktionen: {metrics.totalInteractions}</div>
              <div>Erfolgsrate: {(metrics.successRate * 100).toFixed(1)}%</div>
              <div>Durchschnittliche Antwortzeit: {metrics.averageResponseTime.toFixed(2)}s</div>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="font-semibold mb-2">Häufige Muster</h3>
            <ul className="list-disc list-inside">
              {metrics.commonPatterns.map((pattern, i) => (
                <li key={i}>{pattern}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {plan && (
        <div className="bg-white p-6 rounded-lg shadow mt-6">
          <h3 className="text-xl font-semibold mb-4">Verbesserungsplan</h3>
          
          <div className="space-y-6">
            <div>
              <h4 className="font-medium mb-2">Erkannte Muster</h4>
              <ul className="list-disc list-inside">
                {plan.patterns.map((pattern, i) => (
                  <li key={i}>{pattern}</li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="font-medium mb-2">Herausforderungen</h4>
              <ul className="list-disc list-inside">
                {plan.challenges.map((challenge, i) => (
                  <li key={i}>{challenge}</li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="font-medium mb-2">Vorgeschlagene Verbesserungen</h4>
              <div className="space-y-4">
                {plan.improvements.map((improvement, i) => (
                  <div key={i} className="border-l-4 border-blue-500 pl-4">
                    <div className="font-medium">{improvement.area}</div>
                    <div className="text-sm text-gray-600 mb-2">
                      Priorität: {improvement.priority}
                    </div>
                    <ul className="list-disc list-inside text-sm">
                      {improvement.suggestions.map((suggestion, j) => (
                        <li key={j}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="font-medium mb-2">Implementierungsvorschläge</h4>
              <div className="space-y-4">
                {plan.implementation.map((impl, i) => (
                  <div key={i} className="border p-4 rounded">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <div className="font-medium">{impl.file}</div>
                        <div className="text-sm text-red-600">Risiko: {impl.risk}</div>
                      </div>
                      <Button
                        onClick={() => implementImprovement(impl.file, impl.changes)}
                        disabled={loading}
                        size="sm"
                      >
                        Implementieren
                      </Button>
                    </div>
                    <pre className="text-sm bg-gray-50 p-2 rounded mt-2 overflow-x-auto">
                      {impl.changes}
                    </pre>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}