from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import asyncio
from ..models.model_router import ModelRouter
from ..config.key_manager import APIKeyManager
from .modifier import CodeModifier

class Agent:
    """Main agent class that orchestrates all operations."""
    
    def __init__(self, model_router: ModelRouter, key_manager: APIKeyManager):
        self.model_router = model_router
        self.key_manager = key_manager
        self.code_modifier = CodeModifier(model_router)
        self.workspace_path = Path("workspace")
        self.workspace_path.mkdir(exist_ok=True)
        self.memory: List[Dict[str, Any]] = []

    async def process_request(self, message: str, model: str = "gpt-4") -> str:
        """Process a user request and generate a response."""
        # Add message to memory
        self.memory.append({
            "role": "user",
            "content": message,
            "timestamp": asyncio.get_running_loop().time()
        })

        try:
            response = await self.model_router.route_request(
                model,
                "chat",
                messages=[
                    {
                        "role": "system",
                        "content": "You are Aiden, a self-improving AI agent. "
                                 "You can analyze and modify code, including your own implementation."
                    },
                    *[{"role": m["role"], "content": m["content"]} for m in self.memory[-5:]]
                ]
            )

            # Add response to memory
            self.memory.append({
                "role": "assistant",
                "content": response,
                "timestamp": asyncio.get_running_loop().time()
            })

            return response

        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            self.memory.append({
                "role": "error",
                "content": error_msg,
                "timestamp": asyncio.get_running_loop().time()
            })
            return error_msg

    async def analyze_self(self) -> Dict[str, Any]:
        """Analyze agent's own code for potential improvements."""
        agent_files = list(Path(__file__).parent.glob("*.py"))
        analyses = {}

        for file in agent_files:
            code = file.read_text()
            try:
                analysis = await self.model_router.route_request(
                    "claude",  # Using Claude for code analysis
                    "code_analysis",
                    code=code
                )
                analyses[file.name] = analysis
            except Exception as e:
                analyses[file.name] = {"error": str(e)}

        return analyses

    async def improve_self(self) -> Dict[str, Any]:
        """Attempt to improve agent's own code based on analysis."""
        analyses = await self.analyze_self()
        improvements = {}

        for file_name, analysis in analyses.items():
            if "error" in analysis:
                continue

            try:
                # Generate improvements based on analysis
                messages = [
                    {"role": "system", "content": "You are an expert code improver. "
                                                "Suggest specific, safe improvements to the code."},
                    {"role": "user", "content": f"Analysis: {json.dumps(analysis)}\n\n"
                                              f"Suggest improvements for {file_name}"}
                ]
                
                improvement_suggestions = await self.model_router.route_request(
                    "gpt-4",
                    "chat",
                    messages=messages
                )
                
                improvements[file_name] = improvement_suggestions

            except Exception as e:
                improvements[file_name] = {"error": str(e)}

        return improvements

    def save_memory(self, file_path: Optional[str] = None) -> None:
        """Save agent's memory to a file."""
        if file_path is None:
            file_path = self.workspace_path / "memory.json"

        with open(file_path, 'w') as f:
            json.dump(self.memory, f, indent=2)

    def load_memory(self, file_path: Optional[str] = None) -> None:
        """Load agent's memory from a file."""
        if file_path is None:
            file_path = self.workspace_path / "memory.json"

        if Path(file_path).exists():
            with open(file_path, 'r') as f:
                self.memory = json.load(f)

    async def execute_code_modification(self, file_path: str, changes: str) -> Dict[str, Any]:
        """Execute code modification with safety checks."""
        try:
            # First analyze the changes
            analysis = await self.code_modifier.analyze_code_changes(file_path, changes)
            
            # If analysis shows no major issues, apply changes
            if not analysis.get("critical_issues"):
                success, error = self.code_modifier.apply_changes(file_path, changes)
                if success:
                    return {"status": "success", "analysis": analysis}
                else:
                    return {"status": "error", "message": error, "analysis": analysis}
            else:
                return {"status": "rejected", "issues": analysis["critical_issues"]}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}