from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import os

from ..core.agent.agent import Agent
from ..core.models.model_router import ModelRouter
from ..core.models.openai_model import OpenAIModel
from ..core.models.anthropic_model import AnthropicModel
from ..core.config.key_manager import APIKeyManager
from ..core.agent.learning import AgentLearning
from ..core.agent.improvement import CodeImprovement

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
key_manager = APIKeyManager()
model_router = ModelRouter()
agent = Agent(model_router, key_manager)
learning_system = AgentLearning(model_router)
improvement_system = CodeImprovement(model_router)

class APIKeyRequest(BaseModel):
    service: str
    key: str

class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-4"

class CodeModificationRequest(BaseModel):
    file_path: str
    changes: str

class LearningInteractionRequest(BaseModel):
    user_input: str
    agent_response: str
    success: bool
    duration: float
    metadata: Optional[Dict[str, Any]] = None

class ImprovementRequest(BaseModel):
    target_file: str
    improvement_type: str
    context: Optional[Dict[str, Any]] = None

@app.post("/api/keys")
async def store_api_key(request: APIKeyRequest):
    """Store an API key for a service."""
    try:
        key_manager.store_key(request.service, request.key)
        
        # If it's OpenAI or Anthropic, initialize the model
        if request.service == "openai":
            model_router.register_model("gpt-4", OpenAIModel(request.key))
            model_router.register_model("gpt-3.5-turbo", OpenAIModel(request.key))
        elif request.service == "anthropic":
            model_router.register_model("claude", AnthropicModel(request.key))
            
        return {"status": "success", "message": f"API key for {request.service} stored"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/keys/services")
async def list_services():
    """List all services with stored API keys."""
    return {"services": key_manager.list_services()}

@app.delete("/api/keys/{service}")
async def remove_api_key(service: str):
    """Remove an API key for a service."""
    if key_manager.remove_key(service):
        return {"status": "success", "message": f"API key for {service} removed"}
    raise HTTPException(status_code=404, detail=f"No API key found for {service}")

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Process a chat message."""
    try:
        response = await agent.process_request(request.message, request.model)
        return {"reply": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/code/modify")
async def modify_code(request: CodeModificationRequest):
    """Modify code with safety checks."""
    try:
        result = await agent.execute_code_modification(
            request.file_path,
            request.changes
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/analysis")
async def analyze_agent():
    """Analyze agent's code for potential improvements."""
    try:
        analysis = await agent.analyze_self()
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/improve")
async def improve_agent(request: ImprovementRequest):
    """Attempt to improve specific parts of the agent's code."""
    try:
        # Analyze current code
        with open(request.target_file, 'r') as f:
            current_code = f.read()
        
        # Generate improvement suggestions
        suggestions = await improvement_system.suggest_improvements(current_code)
        
        if request.improvement_type == "analyze_only":
            return suggestions
        
        # Implement improvements if requested
        if request.improvement_type == "implement":
            result = await improvement_system.implement_improvements(
                request.target_file,
                suggestions
            )
            
            if result.get("error"):
                raise HTTPException(status_code=400, detail=result["error"])
                
            return result
            
        return suggestions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/learn")
async def record_learning(request: LearningInteractionRequest):
    """Record and analyze a learning interaction."""
    try:
        analysis = await learning_system.learn_from_interaction({
            "user_input": request.user_input,
            "agent_response": request.agent_response,
            "success": request.success,
            "duration": request.duration,
            "metadata": request.metadata or {}
        })
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/improvement-plan")
async def get_improvement_plan():
    """Get a comprehensive improvement plan based on learning history."""
    try:
        plan = await learning_system.generate_improvement_plan()
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/code-learning")
async def learn_from_code(request: CodeModificationRequest):
    """Learn from code modifications."""
    try:
        # Get the original code
        with open(request.file_path, 'r') as f:
            old_code = f.read()
            
        analysis = await learning_system.learn_from_code_changes(
            request.file_path,
            old_code,
            request.changes
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))