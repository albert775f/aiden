'use client'

import { useState } from 'react'
import { Input } from '../components/ui/input'
import { Button } from '../components/ui/button'
import { Select, SelectItem } from '../components/ui/select'

const MODELS = [
  { label: 'GPT-3.5 Turbo', value: 'gpt-3.5-turbo' },
  { label: 'GPT-4 Turbo', value: 'gpt-4-turbo' },
  { label: 'GPT-4', value: 'gpt-4' }
]

export default function Home() {
  const [messages, setMessages] = useState<string[]>([])
  const [input, setInput] = useState('')
  const [model, setModel] = useState('gpt-4-turbo')
  const [loading, setLoading] = useState(false)

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

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-4 text-center">Aiden.AI Chat</h1>
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
    </div>
  )
}