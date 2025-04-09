from typing import List, Dict, Any
import openai
from .base import AIModel

class OpenAIModel(AIModel):
    """OpenAI model implementation."""
    
    def __init__(self, api_key: str):
        """Initialize with API key."""
        openai.api_key = api_key

    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a response using OpenAI's chat completion."""
        try:
            response = await openai.ChatCompletion.acreate(
                model=kwargs.get('model', 'gpt-4'),
                messages=messages,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 2000)
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    async def analyze_code(self, code: str, **kwargs) -> Dict[str, Any]:
        """Analyze code using OpenAI."""
        prompt = f"""Analyze the following code and provide insights:
        
        {code}
        
        Please provide:
        1. Potential issues or bugs
        2. Security concerns
        3. Performance considerations
        4. Suggested improvements
        
        Format the response as a JSON object with these categories as keys."""

        messages = [
            {"role": "system", "content": "You are a code analysis expert. Provide detailed, actionable insights."},
            {"role": "user", "content": prompt}
        ]

        try:
            response = await self.generate_response(messages)
            # Note: The response should be valid JSON string
            return eval(response)  # In production, use proper JSON parsing with error handling
        except Exception as e:
            raise Exception(f"Code analysis failed: {str(e)}")

    async def stream_response(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """Stream response tokens from OpenAI."""
        try:
            stream = await openai.ChatCompletion.acreate(
                model=kwargs.get('model', 'gpt-4'),
                messages=messages,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 2000),
                stream=True
            )
            
            async for chunk in stream:
                if chunk and chunk.choices and chunk.choices[0].delta.get('content'):
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise Exception(f"OpenAI streaming error: {str(e)}")