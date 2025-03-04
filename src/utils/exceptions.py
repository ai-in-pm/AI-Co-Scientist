# Custom exceptions for the AI Co-Scientist system

class AICoScientistError(Exception):
    """Base exception class for all AI Co-Scientist errors."""
    pass

class ConfigError(AICoScientistError):
    """Exception raised for errors in the configuration."""
    pass

class AgentError(AICoScientistError):
    """Exception raised for errors related to agents."""
    pass

class ToolError(AICoScientistError):
    """Exception raised for errors related to tools."""
    pass

class ValidationError(AICoScientistError):
    """Exception raised for validation errors."""
    pass

class ModelError(AICoScientistError):
    """Exception raised for errors related to the LLM models."""
    pass

class WorkflowError(AICoScientistError):
    """Exception raised for errors in the research workflow."""
    pass
