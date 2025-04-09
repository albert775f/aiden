from typing import Dict, Optional
from .base import AIModel

class ModelNotFoundError(Exception):
    """Raised when requested model is not found."""
    pass

class ModelRouter:
    """Routes requests to appropriate AI models."""
    
    def __init__(self):
        self.models: Dict[str, AIModel] = {}

    def register_model(self, name: str, model: AIModel) -> None:
        """Register a new model with the router."""
        self.models[name] = model

    def get_model(self, name: str) -> Optional[AIModel]:
        """Get a model by name."""
        return self.models.get(name)

    async def route_request(self, model_name: str, request_type: str, **kwargs):
        """Route a request to the appropriate model and method."""
        model = self.get_model(model_name)
        if not model:
            raise ModelNotFoundError(f"Model {model_name} not found")
        
        if request_type == "chat":
            return await model.generate_response(**kwargs)
        elif request_type == "code_analysis":
            return await model.analyze_code(**kwargs)
        else:
            raise ValueError(f"Unknown request type: {request_type}")