'use client'

import { useState } from 'react'
import { Input } from '../components/ui/input'
import { Button } from '../components/ui/button'
import { Select, SelectItem } from '../components/ui/select'
import { ApiKeyManager } from '../components/ApiKeyManager'
import { AgentImprovement } from '../components/AgentImprovement'
import { LearningOverview } from '../components/LearningOverview'

const MODELS = [
  { label: 'GPT-3.5 Turbo', value: 'gpt-3.5-turbo' },
  { label: 'GPT-4 Turbo', value: 'gpt-4-turbo' },
  { label: 'GPT-4', value: 'gpt-4' },
  { label: 'Claude-2', value: 'claude' }
]

type Tab = 'chat' | 'settings' | 'analysis' | 'learning'

export default function Home() {
  const [messages, setMessages] = useState<string[]>([])
  const [input, setInput] = useState('')
  const [model, setModel] = useState('gpt-4-turbo')
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<Tab>('chat')
  const [analysisResult, setAnalysisResult] = useState<any>(null)

  const sendMessage = async () => {
    if (!input.trim()) return
    setLoading(true)
    setMessages(prev => [...prev, `🧑‍💻: ${input}`])
    setInput('')
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: input, model })
    })
    const data = await res.json()
    setMessages(prev => [...prev, `🤖: ${data.reply}`])
    setLoading(false)
  }

  const requestAnalysis = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/agent/analysis')
      const data = await response.json()
      setAnalysisResult(data)
    } catch (error) {
      console.error('Error requesting analysis:', error)
    } finally {
      setLoading(false)
    }
  }

  const renderTabs = () => (
    <div className="flex space-x-2 mb-4">
      <Button
        variant={activeTab === 'chat' ? 'default' : 'outline'}
        onClick={() => setActiveTab('chat')}
      >
        Chat
      </Button>
      <Button
        variant={activeTab === 'settings' ? 'default' : 'outline'}
        onClick={() => setActiveTab('settings')}
      >
        Einstellungen
      </Button>
      <Button
        variant={activeTab === 'analysis' ? 'default' : 'outline'}
        onClick={() => setActiveTab('analysis')}
      >
        Analyse
      </Button>
      <Button
        variant={activeTab === 'learning' ? 'default' : 'outline'}
        onClick={() => setActiveTab('learning')}
      >
        Lernen
      </Button>
    </div>
  )

  const renderChat = () => (
    <>
      <div className="mb-4">
        <Select value={model} onValueChange={setModel}>
          {MODELS.map(({ label, value }) => (
            <SelectItem key={value} value={value}>{label}</SelectItem>
          ))}
        </Select>
      </div>
      <div className="bg-gray-100 rounded-xl p-4 h-96 overflow-y-auto mb-4 space-y-2">
        {messages.map((msg, i) => (
          <div key={i} className="whitespace-pre-wrap">{msg}</div>
        ))}
        {loading && <div className="text-gray-500 italic">Aiden denkt ...</div>}
      </div>
      <div className="flex gap-2">
        <Input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
          placeholder="Schreib eine Anweisung..."
        />
        <Button onClick={sendMessage}>Senden</Button>
      </div>
    </>
  )

  const renderAnalysis = () => (
    <div className="space-y-4">
      <Button 
        onClick={requestAnalysis}
        disabled={loading}
      >
        {loading ? 'Analysiere...' : 'Selbstanalyse durchführen'}
      </Button>
      
      {analysisResult && (
        <div className="bg-gray-100 rounded-xl p-4 space-y-4">
          {Object.entries(analysisResult).map(([file, analysis]) => (
            <div key={file} className="space-y-2">
              <h3 className="font-bold">{file}</h3>
              <pre className="whitespace-pre-wrap text-sm">
                {JSON.stringify(analysis, null, 2)}
              </pre>
            </div>
          ))}
        </div>
      )}
    </div>
  )

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-4 text-center">Aiden.AI</h1>
      {renderTabs()}
      
      <div className="mt-6">
        {activeTab === 'chat' && renderChat()}
        {activeTab === 'settings' && <ApiKeyManager />}
        {activeTab === 'analysis' && renderAnalysis()}
{activeTab === 'learning' && renderLearning()}
      </div>
    </div>
  )

  const renderLearning = () => (
    <LearningOverview />
  )
}