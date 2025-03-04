# Base Agent class for the AI Co-Scientist system

import os
import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

from ..config.config import (
    OPENAI_API_KEY, 
    AGENT_DEFAULT_TEMPERATURE, 
    AGENT_DEFAULT_MODEL,
    MAX_TOKENS
)

class BaseAgent(ABC):
    """Base class for all agents in the AI Co-Scientist system."""
    
    def __init__(self, 
                 name: str,
                 system_prompt: str,
                 model: str = AGENT_DEFAULT_MODEL,
                 temperature: float = AGENT_DEFAULT_TEMPERATURE):
        """Initialize the base agent.
        
        Args:
            name: The name of the agent
            system_prompt: The system prompt that defines the agent's role
            model: The LLM model to use
            temperature: The temperature parameter for generation
        """
        self.name = name
        self.system_prompt = system_prompt
        
        # Ensure model is never None
        self.model = model if model is not None else AGENT_DEFAULT_MODEL
        self.temperature = temperature
        self.conversation_history = []
        
        # Initialize the LLM
        self.llm = ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            api_key=OPENAI_API_KEY,
            max_tokens=MAX_TOKENS
        )
        
        # Add system prompt to conversation history
        self.conversation_history.append(
            SystemMessage(content=system_prompt)
        )
        
        self.logger = logging.getLogger(f"agent.{name}")
    
    def add_message(self, message: str, is_human: bool = True) -> None:
        """Add a message to the conversation history.
        
        Args:
            message: The message content
            is_human: Whether the message is from a human (True) or AI (False)
        """
        if is_human:
            self.conversation_history.append(HumanMessage(content=message))
        else:
            self.conversation_history.append(AIMessage(content=message))
    
    def get_response(self, query: str) -> str:
        """Get a response from the agent based on the query.
        
        Args:
            query: The query to send to the agent
            
        Returns:
            The agent's response as a string
        """
        # Add the query to conversation history
        self.add_message(query, is_human=True)
        
        # Get response from the LLM
        response = self.llm.invoke(self.conversation_history)
        
        # Add the response to conversation history
        self.add_message(response.content, is_human=False)
        
        return response.content
    
    def clear_history(self) -> None:
        """Clear the conversation history, keeping only the system prompt."""
        system_prompt = self.conversation_history[0]
        self.conversation_history = [system_prompt]
    
    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """Process the input data and return a result.
        
        This method must be implemented by all subclasses.
        
        Args:
            input_data: The input data to process
            
        Returns:
            The processing result
        """
        pass
