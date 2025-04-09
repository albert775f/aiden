from typing import Dict, Any, List, Optional
from pathlib import Path
import ast
import astor
import json
from ..models.model_router import ModelRouter

class CodeImprovement:
    """Handles code improvement suggestions and implementations."""
    
    def __init__(self, model_router: ModelRouter):
        self.model_router = model_router
        self.safety_checks = [
            self._check_syntax,
            self._check_dangerous_imports,
            self._check_file_operations,
            self._check_network_operations
        ]

    async def suggest_improvements(self, code: str) -> Dict[str, Any]:
        """Generate improvement suggestions for the given code."""
        prompt = f"""Analyze this Python code and suggest improvements:

        {code}

        Focus on:
        1. Code quality and readability
        2. Performance optimizations
        3. Security improvements
        4. Error handling
        5. Architecture improvements

        Format your response as a JSON object with these keys:
        - suggestions: List of specific improvement suggestions
        - priority: Priority level for each suggestion (high/medium/low)
        - implementation: Concrete code examples for each suggestion
        - risks: Potential risks or side effects of each suggestion
        """

        try:
            response = await self.model_router.route_request(
                "gpt-4",
                "chat",
                messages=[
                    {"role": "system", "content": "You are a Python code improvement expert."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse the response as JSON
            return json.loads(response)
        except Exception as e:
            return {"error": f"Failed to generate improvements: {str(e)}"}

    async def implement_improvements(
        self,
        file_path: str,
        improvements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Implement suggested improvements with safety checks."""
        try:
            with open(file_path, 'r') as f:
                original_code = f.read()

            # Get implementation details from improvements
            implementations = improvements.get('implementation', {})
            if not implementations:
                return {"error": "No implementation details provided"}

            # Create AST from original code
            tree = ast.parse(original_code)
            
            # Apply improvements using AST transformation
            modified_tree = self._apply_improvements_to_ast(tree, implementations)
            
            # Convert modified AST back to code
            modified_code = astor.to_source(modified_tree)
            
            # Run safety checks
            for check in self.safety_checks:
                result = check(modified_code)
                if not result['safe']:
                    return {"error": f"Safety check failed: {result['reason']}"}

            # Create backup
            backup_path = f"{file_path}.bak"
            Path(file_path).rename(backup_path)

            try:
                # Write improved code
                with open(file_path, 'w') as f:
                    f.write(modified_code)
                
                return {
                    "status": "success",
                    "message": "Improvements implemented successfully",
                    "backup_created": backup_path
                }
                
            except Exception as write_error:
                # Restore from backup if write fails
                Path(backup_path).rename(file_path)
                return {"error": f"Failed to write improved code: {str(write_error)}"}
                
        except Exception as e:
            return {"error": f"Failed to implement improvements: {str(e)}"}

    def _apply_improvements_to_ast(
        self,
        tree: ast.AST,
        implementations: Dict[str, str]
    ) -> ast.AST:
        """Apply improvements by transforming the AST."""
        # This is a placeholder for actual AST transformation logic
        # In a real implementation, this would parse the implementation
        # details and modify the AST accordingly
        return tree

    def _check_syntax(self, code: str) -> Dict[str, Any]:
        """Check if the modified code has valid syntax."""
        try:
            ast.parse(code)
            return {"safe": True}
        except SyntaxError as e:
            return {"safe": False, "reason": f"Syntax error: {str(e)}"}

    def _check_dangerous_imports(self, code: str) -> Dict[str, Any]:
        """Check for potentially dangerous imports."""
        dangerous_modules = {
            'os', 'subprocess', 'sys', 'shutil',
            'requests', 'urllib', 'socket'
        }
        
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        if name.name in dangerous_modules:
                            return {
                                "safe": False,
                                "reason": f"Dangerous import detected: {name.name}"
                            }
                elif isinstance(node, ast.ImportFrom):
                    if node.module in dangerous_modules:
                        return {
                            "safe": False,
                            "reason": f"Dangerous import detected: {node.module}"
                        }
            
            return {"safe": True}
            
        except Exception as e:
            return {"safe": False, "reason": f"Import check failed: {str(e)}"}

    def _check_file_operations(self, code: str) -> Dict[str, Any]:
        """Check for potentially dangerous file operations."""
        dangerous_patterns = [
            'open(',
            'write(',
            'delete(',
            'remove(',
            'unlink('
        ]
        
        for pattern in dangerous_patterns:
            if pattern in code:
                return {
                    "safe": False,
                    "reason": f"Potentially dangerous file operation detected: {pattern}"
                }
        
        return {"safe": True}

    def _check_network_operations(self, code: str) -> Dict[str, Any]:
        """Check for potentially dangerous network operations."""
        dangerous_patterns = [
            'socket.',
            'connect(',
            'listen(',
            'bind(',
            'request.',
            'urlopen('
        ]
        
        for pattern in dangerous_patterns:
            if pattern in code:
                return {
                    "safe": False,
                    "reason": f"Potentially dangerous network operation detected: {pattern}"
                }
        
        return {"safe": True"}