import { useState, useEffect } from 'react'
import { Input } from './ui/input'
import { Button } from './ui/button'

interface ApiKey {
  service: string
  key: string
}

export const ApiKeyManager = () => {
  const [services, setServices] = useState<string[]>([])
  const [newKey, setNewKey] = useState<ApiKey>({ service: '', key: '' })
  const [status, setStatus] = useState<string>('')

  useEffect(() => {
    fetchServices()
  }, [])

  const fetchServices = async () => {
    try {
      const response = await fetch('/api/keys/services')
      const data = await response.json()
      setServices(data.services)
    } catch (error) {
      setStatus('Error fetching services')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const response = await fetch('/api/keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newKey)
      })
      
      if (response.ok) {
        setStatus('API key stored successfully')
        setNewKey({ service: '', key: '' })
        fetchServices()
      } else {
        const error = await response.json()
        setStatus(`Error: ${error.detail}`)
      }
    } catch (error) {
      setStatus('Error storing API key')
    }
  }

  const handleRemove = async (service: string) => {
    try {
      const response = await fetch(`/api/keys/${service}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        setStatus(`Removed API key for ${service}`)
        fetchServices()
      } else {
        const error = await response.json()
        setStatus(`Error: ${error.detail}`)
      }
    } catch (error) {
      setStatus('Error removing API key')
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">API Key Management</h2>
      
      {/* Current Services */}
      <div className="space-y-2">
        <h3 className="text-lg font-semibold">Current API Keys</h3>
        {services.length === 0 ? (
          <p className="text-gray-500">No API keys stored</p>
        ) : (
          <ul className="space-y-2">
            {services.map(service => (
              <li key={service} className="flex items-center justify-between">
                <span>{service}</span>
                <Button
                  onClick={() => handleRemove(service)}
                  variant="destructive"
                  size="sm"
                >
                  Remove
                </Button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Add New Key */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <h3 className="text-lg font-semibold">Add New API Key</h3>
        
        <div className="space-y-2">
          <Input
            placeholder="Service (e.g., openai, anthropic)"
            value={newKey.service}
            onChange={e => setNewKey({ ...newKey, service: e.target.value })}
            required
          />
          
          <Input
            type="password"
            placeholder="API Key"
            value={newKey.key}
            onChange={e => setNewKey({ ...newKey, key: e.target.value })}
            required
          />
        </div>

        <Button type="submit">Store API Key</Button>
      </form>

      {/* Status Message */}
      {status && (
        <div className={`p-2 rounded ${
          status.startsWith('Error') ? 'bg-red-100' : 'bg-green-100'
        }`}>
          {status}
        </div>
      )}
    </div>
  )
}