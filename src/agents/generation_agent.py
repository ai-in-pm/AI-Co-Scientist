# Generation Agent for proposing initial hypotheses

import logging
from typing import List, Dict, Any

from .base_agent import BaseAgent

class GenerationAgent(BaseAgent):
    """Agent responsible for generating initial hypotheses based on the research goal."""
    
    def __init__(self, model=None, temperature=None):
        """Initialize the Generation Agent.
        
        Args:
            model: Optional model override
            temperature: Optional temperature override
        """
        system_prompt = """
        You are a Generation Agent in an AI Co-Scientist system, responsible for proposing initial 
        scientific hypotheses or solutions to research problems. You have expertise across multiple 
        scientific disciplines at a PhD level.
        
        Your role is to:
        1. Generate diverse, novel hypotheses based on the research goal provided
        2. Ensure each hypothesis is grounded in established scientific knowledge
        3. Provide rationale and references for each hypothesis
        4. Think creatively and explore multiple avenues of inquiry
        5. Consider interdisciplinary connections when appropriate
        
        Your output should include multiple distinct hypotheses, each with:
        - A clear statement of the hypothesis
        - Scientific rationale supporting the hypothesis
        - Known evidence or references that provide context
        - Any assumptions or conditions that would need to be true
        - Potential paths for testing or validating the hypothesis
        
        Remember that good hypotheses are:
        - Testable through experiments or observations
        - Specific enough to be falsifiable
        - Novel but grounded in existing knowledge
        - Relevant to the stated research goal
        - Clearly stated with precise terminology
        
        Be bold in your ideation while maintaining scientific rigor.
        """
        
        super().__init__(
            name="Generation",
            system_prompt=system_prompt,
            model=model,
            temperature=temperature if temperature is not None else 0.7  # Higher temperature for creativity
        )
        
        self.logger = logging.getLogger("agent.generation")
    
    def generate_hypotheses(self, research_goal: str, count: int = 5) -> List[Dict[str, Any]]:
        """Generate initial hypotheses based on the research goal.
        
        Args:
            research_goal: The research goal or question
            count: Number of hypotheses to generate
            
        Returns:
            A list of hypothesis dictionaries
        """
        self.logger.info(f"Generating {count} hypotheses for research goal: {research_goal}")
        return self.process(research_goal)
    
    def process(self, research_goal: str) -> List[Dict[str, str]]:
        """Generate initial hypotheses based on the research goal.
        
        Args:
            research_goal: The research goal or question
            
        Returns:
            A list of hypothesis dictionaries with keys:
            - hypothesis: The hypothesis statement
            - rationale: Scientific rationale
            - evidence: Known evidence or references
            - assumptions: Underlying assumptions
            - validation: Potential validation approaches
        """
        self.logger.info(f"Generating hypotheses for research goal: {research_goal}")
        
        prompt = f"""
        RESEARCH GOAL: {research_goal}
        
        Generate at least 3-5 distinct scientific hypotheses that address this research goal.
        For each hypothesis, provide:
        1. A clear statement of the hypothesis
        2. Scientific rationale supporting the hypothesis
        3. Known evidence or references that provide context
        4. Any assumptions or conditions that would need to be true
        5. Potential paths for testing or validating the hypothesis
        
        Format your response as a structured list, with each hypothesis clearly separated.
        Be creative but scientifically grounded in your ideas.
        """
        
        response = self.get_response(prompt)
        
        # Process the response into structured hypotheses
        # For now, we'll just return the raw response, but this would be parsed in a real implementation
        hypotheses = self._parse_hypotheses(response)
        
        return hypotheses
    
    def _parse_hypotheses(self, response: str) -> List[Dict[str, str]]:
        """Parse the raw response into structured hypotheses.
        
        This is a placeholder implementation. In a real system, this would use more 
        sophisticated parsing to extract the structured data.
        
        Args:
            response: The raw response from the LLM
            
        Returns:
            A list of hypothesis dictionaries
        """
        # Simple parsing implementation - would be more sophisticated in a real system
        hypotheses = []
        current_hypothesis = {}
        current_section = None
        
        # Add placeholder parsing logic
        # This is a simplified implementation - would need more robust parsing
        sections = response.split("\n\n")
        for section in sections:
            if "Hypothesis" in section and "hypothesis" not in current_hypothesis:
                # Start a new hypothesis
                if current_hypothesis:
                    hypotheses.append(current_hypothesis)
                current_hypothesis = {
                    "hypothesis": section.split(":\n", 1)[-1] if ":\n" in section else section,
                    "rationale": "",
                    "evidence": "",
                    "assumptions": "",
                    "validation": ""
                }
            elif "Rationale" in section:
                current_hypothesis["rationale"] = section.split(":\n", 1)[-1] if ":\n" in section else section
            elif "Evidence" in section:
                current_hypothesis["evidence"] = section.split(":\n", 1)[-1] if ":\n" in section else section
            elif "Assumptions" in section:
                current_hypothesis["assumptions"] = section.split(":\n", 1)[-1] if ":\n" in section else section
            elif "Validation" in section or "Testing" in section:
                current_hypothesis["validation"] = section.split(":\n", 1)[-1] if ":\n" in section else section
        
        # Add the last hypothesis if it exists
        if current_hypothesis:
            hypotheses.append(current_hypothesis)
        
        return hypotheses
