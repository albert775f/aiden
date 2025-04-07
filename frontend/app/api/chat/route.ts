// /frontend/app/api/chat/route.ts
import { NextResponse } from 'next/server'

export async function POST(req: Request) {
  const { message, model } = await req.json()

  const apiKey = process.env.OPENAI_API_KEY
  if (!apiKey) {
    return NextResponse.json({ reply: 'Fehlender OpenAI API Key.' }, { status: 500 })
  }

  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${apiKey}`
    },
    body: JSON.stringify({
      model: model || 'gpt-4-turbo',
      messages: [
        { role: 'system', content: 'Du bist Aiden, ein hilfreicher, aber ehrgeiziger KI-Operator.' },
        { role: 'user', content: message }
      ]
    })
  })

  if (!response.ok) {
    const err = await response.text()
    return NextResponse.json({ reply: `Fehler: ${err}` }, { status: 500 })
  }

  const data = await response.json()
  const reply = data.choices?.[0]?.message?.content || 'Keine Antwort erhalten.'

  return NextResponse.json({ reply })
}