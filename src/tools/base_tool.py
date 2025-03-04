# Base class for all tools

from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, Optional, List

class BaseTool(ABC):
    """Base abstract class for all tools used by agents.
    
    All specific tool implementations should inherit from this class
    and implement the required methods.
    """
    
    def __init__(self, name: str, description: str):
        """Initialize the base tool.
        
        Args:
            name: The name of the tool
            description: A description of what the tool does
        """
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"tool.{name}")
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the tool with the given parameters.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            The result of the tool execution
        """
        pass
    
    def get_tool_spec(self) -> Dict[str, Any]:
        """Get the tool specification for agent function calling.
        
        Returns:
            A dictionary containing the tool's specification.
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.get_parameters_schema()
            }
        }
    
    @abstractmethod
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for the tool's parameters.
        
        Returns:
            A dictionary containing the JSON schema for the tool's parameters.
        """
        pass
