# Agent Factory for creating agent instances

import logging
from typing import Dict, Any, Type, Optional

from .base_agent import BaseAgent
from .generation_agent import GenerationAgent
from .reflection_agent import ReflectionAgent
from .ranking_agent import RankingAgent
from .evolution_agent import EvolutionAgent
from .proximity_agent import ProximityAgent
from .meta_review_agent import MetaReviewAgent
from .supervisor_agent import SupervisorAgent

from ..config.config import AGENT_DEFAULT_MODEL

class AgentFactory:
    """Factory class for creating and managing agent instances."""
    
    def __init__(self):
        """Initialize the agent factory."""
        self.logger = logging.getLogger("agent_factory")
        self.agents = {}  # Cache of created agents
        
        # Register available agent classes
        self.agent_classes = {
            "generation": GenerationAgent,
            "reflection": ReflectionAgent,
            "ranking": RankingAgent,
            "evolution": EvolutionAgent,
            "proximity": ProximityAgent,
            "metareview": MetaReviewAgent,
            "supervisor": SupervisorAgent
        }
    
    def get_agent(self, agent_type: str, model: Optional[str] = None, temperature: Optional[float] = None) -> BaseAgent:
        """Get an agent instance of the specified type.
        
        Args:
            agent_type: The type of agent to create (case-insensitive)
            model: Optional model override
            temperature: Optional temperature override
            
        Returns:
            An agent instance
            
        Raises:
            ValueError: If the agent type is not recognized
        """
        agent_type = agent_type.lower()
        
        # Ensure model is never None - use the default from config if not provided
        if model is None:
            model = AGENT_DEFAULT_MODEL
        
        # Check if we have a cached instance with the same parameters
        cache_key = f"{agent_type}_{model}_{temperature}"
        if cache_key in self.agents:
            self.logger.debug(f"Returning cached agent: {agent_type}")
            return self.agents[cache_key]
        
        # Create a new agent instance
        if agent_type not in self.agent_classes:
            raise ValueError(f"Unknown agent type: {agent_type}. Available types: {', '.join(self.agent_classes.keys())}")
        
        agent_class = self.agent_classes[agent_type]
        agent = agent_class(model=model, temperature=temperature)
        
        # Cache the agent instance
        self.agents[cache_key] = agent
        self.logger.info(f"Created new agent: {agent_type}, model: {model}, temp: {temperature or 'default'}")
        
        return agent
    
    def get_supervisor(self, model: Optional[str] = None, temperature: Optional[float] = None) -> SupervisorAgent:
        """Get a supervisor agent instance.
        
        This is a convenience method for getting the supervisor specifically.
        
        Args:
            model: Optional model override
            temperature: Optional temperature override
            
        Returns:
            A SupervisorAgent instance
        """
        return self.get_agent("supervisor", model, temperature)
    
    def clear_cache(self):
        """Clear the cache of agent instances."""
        self.agents.clear()
        self.logger.info("Cleared agent cache")
