import ast
from typing import Dict, Any, Optional
from pathlib import Path
import astor
from ..models.model_router import ModelRouter

class CodeModifier:
    """Handles code modification with safety checks."""
    
    def __init__(self, model_router: ModelRouter):
        self.model_router = model_router

    def read_file(self, file_path: str) -> str:
        """Read a file's contents."""
        with open(file_path, 'r') as f:
            return f.read()

    async def analyze_code_changes(
        self, 
        file_path: str, 
        proposed_changes: str
    ) -> Dict[str, Any]:
        """Analyze proposed code changes using AI model."""
        current_code = self.read_file(file_path)
        
        analysis = await self.model_router.route_request(
            "gpt-4",
            "code_analysis",
            code=current_code,
            changes=proposed_changes
        )
        
        return analysis

    def validate_syntax(self, code: str) -> bool:
        """Validate Python code syntax."""
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    def validate_safety(self, code: str) -> tuple[bool, Optional[str]]:
        """
        Validate code safety by checking for dangerous operations.
        Returns (is_safe, reason_if_unsafe)
        """
        try:
            tree = ast.parse(code)
            
            # Check for dangerous imports
            dangerous_modules = {'os', 'subprocess', 'sys'}
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        if name.name in dangerous_modules:
                            return False, f"Dangerous import: {name.name}"
                elif isinstance(node, ast.ImportFrom):
                    if node.module in dangerous_modules:
                        return False, f"Dangerous import: {node.module}"
            
            return True, None
            
        except Exception as e:
            return False, str(e)

    def apply_changes(
        self, 
        file_path: str, 
        changes: str,
        backup: bool = True
    ) -> tuple[bool, Optional[str]]:
        """
        Apply code changes with safety checks.
        Returns (success, error_message_if_failed)
        """
        # Validate syntax
        if not self.validate_syntax(changes):
            return False, "Invalid Python syntax"

        # Validate safety
        is_safe, safety_reason = self.validate_safety(changes)
        if not is_safe:
            return False, f"Safety check failed: {safety_reason}"

        # Create backup
        if backup:
            backup_path = f"{file_path}.bak"
            Path(file_path).rename(backup_path)

        try:
            # Write new code
            with open(file_path, 'w') as f:
                f.write(changes)
            return True, None
            
        except Exception as e:
            # Restore from backup if something went wrong
            if backup:
                Path(backup_path).rename(file_path)
            return False, str(e)