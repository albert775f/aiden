from typing import Dict, Any, List, Optional
import json
from pathlib import Path
from datetime import datetime
import asyncio
from ..models.model_router import ModelRouter

class AgentLearning:
    """Handles the agent's learning and self-improvement capabilities."""
    
    def __init__(self, model_router: ModelRouter):
        self.model_router = model_router
        self.learning_path = Path("learning_history")
        self.learning_path.mkdir(exist_ok=True)
        self.current_learnings: List[Dict[str, Any]] = []

    async def learn_from_interaction(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Learn from a single interaction with a user."""
        try:
            # Analyze the interaction
            analysis = await self._analyze_interaction(interaction)
            
            # Store the learning
            self._store_learning({
                "timestamp": datetime.now().isoformat(),
                "interaction": interaction,
                "analysis": analysis,
                "type": "interaction_learning"
            })

            return analysis
        except Exception as e:
            return {"error": f"Failed to learn from interaction: {str(e)}"}

    async def learn_from_code_changes(self, file_path: str, old_code: str, new_code: str) -> Dict[str, Any]:
        """Learn from code modifications."""
        try:
            # Analyze the code changes
            analysis = await self._analyze_code_changes(old_code, new_code)
            
            # Store the learning
            self._store_learning({
                "timestamp": datetime.now().isoformat(),
                "file_path": file_path,
                "analysis": analysis,
                "type": "code_learning"
            })

            return analysis
        except Exception as e:
            return {"error": f"Failed to learn from code changes: {str(e)}"}

    async def generate_improvement_plan(self) -> Dict[str, Any]:
        """Generate a plan for self-improvement based on accumulated learnings."""
        try:
            recent_learnings = self._get_recent_learnings(limit=50)
            
            # Create a prompt for the AI to analyze learnings
            prompt = f"""Based on these recent learning experiences, suggest improvements:

            Recent Learnings:
            {json.dumps(recent_learnings, indent=2)}

            Please analyze these learnings and suggest:
            1. Patterns in user interactions
            2. Common challenges or limitations
            3. Potential improvements to:
               - Code structure
               - Response quality
               - Learning capabilities
               - Error handling
            4. Specific implementation suggestions

            Format your response as a structured improvement plan."""

            response = await self.model_router.route_request(
                "gpt-4",
                "chat",
                messages=[
                    {"role": "system", "content": "You are an AI learning specialist."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse and structure the improvement plan
            plan = self._structure_improvement_plan(response)
            
            return plan
        except Exception as e:
            return {"error": f"Failed to generate improvement plan: {str(e)}"}

    async def _analyze_interaction(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a user interaction for learning purposes."""
        try:
            prompt = f"""Analyze this interaction for learning opportunities:

            User Input: {interaction.get('user_input')}
            Agent Response: {interaction.get('agent_response')}
            Success: {interaction.get('success')}
            Duration: {interaction.get('duration')}

            Please identify:
            1. What worked well
            2. What could be improved
            3. Any patterns or insights
            4. Specific learning points"""

            analysis = await self.model_router.route_request(
                "gpt-4",
                "chat",
                messages=[
                    {"role": "system", "content": "You are an interaction analysis specialist."},
                    {"role": "user", "content": prompt}
                ]
            )

            return json.loads(analysis)
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}

    async def _analyze_code_changes(self, old_code: str, new_code: str) -> Dict[str, Any]:
        """Analyze code changes for learning purposes."""
        try:
            prompt = f"""Compare these code versions and analyze the changes:

            Original Code:
            {old_code}

            New Code:
            {new_code}

            Please identify:
            1. Nature of changes
            2. Improvement patterns
            3. Potential risks
            4. Learning points"""

            analysis = await self.model_router.route_request(
                "gpt-4",
                "chat",
                messages=[
                    {"role": "system", "content": "You are a code analysis specialist."},
                    {"role": "user", "content": prompt}
                ]
            )

            return json.loads(analysis)
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}

    def _store_learning(self, learning: Dict[str, Any]) -> None:
        """Store a learning experience."""
        # Add to current learnings
        self.current_learnings.append(learning)
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = self.learning_path / f"learning_{timestamp}.json"
        
        with open(file_path, 'w') as f:
            json.dump(learning, f, indent=2)

    def _get_recent_learnings(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent learning experiences."""
        # Combine current learnings with stored learnings
        all_learnings = []
        
        # Load from files
        learning_files = sorted(self.learning_path.glob("learning_*.json"), reverse=True)
        for file in learning_files[:limit]:
            try:
                with open(file, 'r') as f:
                    learning = json.load(f)
                    all_learnings.append(learning)
            except Exception:
                continue

        # Add current learnings
        all_learnings.extend(self.current_learnings)
        
        # Return most recent ones
        return sorted(
            all_learnings,
            key=lambda x: x.get('timestamp', ''),
            reverse=True
        )[:limit]

    def _structure_improvement_plan(self, raw_plan: str) -> Dict[str, Any]:
        """Structure the raw improvement plan into a formatted response."""
        try:
            # Attempt to parse if it's already JSON
            return json.loads(raw_plan)
        except json.JSONDecodeError:
            # If not JSON, structure it manually
            return {
                "raw_plan": raw_plan,
                "timestamp": datetime.now().isoformat(),
                "status": "unstructured"
            }