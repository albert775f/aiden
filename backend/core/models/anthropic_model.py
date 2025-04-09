from typing import List, Dict, Any
import anthropic
from .base import AIModel

class AnthropicModel(AIModel):
    """Anthropic (Claude) model implementation."""
    
    def __init__(self, api_key: str):
        """Initialize with API key."""
        self.client = anthropic.Client(api_key=api_key)
        self.default_model = "claude-2"

    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a response using Anthropic's Claude."""
        try:
            # Convert chat format to Claude format
            prompt = self._convert_messages_to_prompt(messages)
            
            response = self.client.completion(
                model=kwargs.get('model', self.default_model),
                prompt=prompt,
                max_tokens_to_sample=kwargs.get('max_tokens', 2000),
                temperature=kwargs.get('temperature', 0.7)
            )
            return response.completion
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")

    async def analyze_code(self, code: str, **kwargs) -> Dict[str, Any]:
        """Analyze code using Claude."""
        prompt = f"""Please analyze this code and provide a detailed report:

        {code}

        Format your response as a JSON object with these keys:
        - potential_issues: List of potential bugs or issues
        - security_concerns: List of security considerations
        - performance_notes: List of performance-related observations
        - improvement_suggestions: List of specific improvements
        
        Be thorough but concise."""

        try:
            response = await self.generate_response([
                {"role": "system", "content": "You are an expert code analyzer."},
                {"role": "user", "content": prompt}
            ])
            # Note: The response should be valid JSON string
            return eval(response)  # In production, use proper JSON parsing with error handling
        except Exception as e:
            raise Exception(f"Code analysis failed: {str(e)}")

    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert chat messages to Claude's expected format."""
        prompt = ""
        for msg in messages:
            role = msg['role']
            content = msg['content']
            
            if role == 'system':
                prompt += f"\n\nSystem: {content}"
            elif role == 'user':
                prompt += f"\n\nHuman: {content}"
            elif role == 'assistant':
                prompt += f"\n\nAssistant: {content}"
                
        prompt += "\n\nAssistant:"
        return prompt.lstrip()

    async def stream_response(self, messages: List[Dict[str, str]], **kwargs):
        """
        Stream response from Claude.
        Note: Anthropic's Python client doesn't support streaming yet,
        this is a placeholder for future implementation.
        """
        # For now, we'll just return the full response
        response = await self.generate_response(messages, **kwargs)
        yield response