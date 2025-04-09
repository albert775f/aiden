from abc import ABC, abstractmethod
from typing import List, Dict, Any

class AIModel(ABC):
    """Base class for AI model implementations."""
    
    @abstractmethod
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a response from the model based on input messages."""
        pass

    @abstractmethod
    async def analyze_code(self, code: str, **kwargs) -> Dict[str, Any]:
        """Analyze code and return insights."""
        pass