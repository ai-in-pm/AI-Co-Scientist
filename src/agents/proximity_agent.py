# Proximity (Relevance) Agent for ensuring hypotheses remain on-topic

import logging
from typing import List, Dict, Any

from .base_agent import BaseAgent

class ProximityAgent(BaseAgent):
    """Agent responsible for ensuring hypotheses remain on-topic and relevant to research goals."""
    
    def __init__(self, model=None, temperature=None):
        """Initialize the Proximity Agent.
        
        Args:
            model: Optional model override
            temperature: Optional temperature override
        """
        system_prompt = """
        You are a Proximity Agent in an AI Co-Scientist system, responsible for evaluating how closely 
        scientific hypotheses align with the original research goals. You have expertise across 
        multiple scientific disciplines at a PhD level.
        
        Your role is to:
        1. Assess the semantic and conceptual relatedness of hypotheses to the research objectives
        2. Identify and filter out tangential or irrelevant suggestions
        3. Ensure that hypotheses address the core questions posed in the research goal
        4. Evaluate whether hypotheses maintain appropriate scope (neither too broad nor too narrow)
        5. Provide specific feedback on how to increase relevance when needed
        
        When evaluating proximity, consider:
        - Conceptual alignment: Does the hypothesis address the same fundamental concepts as the research goal?
        - Problem-solution fit: Does the hypothesis potentially solve the problem outlined in the goal?
        - Scope appropriateness: Is the hypothesis at the right level of specificity for the goal?
        - Scientific domain match: Does the hypothesis stay within the relevant scientific domains?
        - Practical applicability: Would findings based on this hypothesis be useful for the stated objective?
        
        Your evaluations should be precise and constructive, focusing on relevance rather than 
        scientific validity (which is handled by other agents).
        """
        
        super().__init__(
            name="Proximity",
            system_prompt=system_prompt,
            model=model,
            temperature=temperature if temperature is not None else 0.2  # Lower temperature for consistency
        )
        
        self.logger = logging.getLogger("agent.proximity")
    
    def process(self, hypotheses: List[Dict[str, Any]], research_goal: str) -> List[Dict[str, Any]]:
        """Evaluate how closely each hypothesis aligns with the research goal.
        
        Args:
            hypotheses: List of hypothesis dictionaries to evaluate
            research_goal: The original research goal for context
            
        Returns:
            A list of hypothesis dictionaries with added proximity evaluation
        """
        self.logger.info(f"Evaluating proximity of {len(hypotheses)} hypotheses to research goal")
        
        evaluated_hypotheses = []
        
        for idx, hypothesis in enumerate(hypotheses):
            self.logger.info(f"Evaluating proximity of hypothesis {idx+1}")
            
            # Prepare a concise version of the hypothesis for evaluation
            hypothesis_statement = hypothesis['statement']
            hypothesis_rationale = hypothesis.get('rationale', '')[:300] + "..." if len(hypothesis.get('rationale', '')) > 300 else hypothesis.get('rationale', '')
            
            prompt = f"""
            RESEARCH GOAL: {research_goal}
            
            HYPOTHESIS TO EVALUATE:
            Statement: {hypothesis_statement}
            Rationale: {hypothesis_rationale}
            
            Please evaluate how closely this hypothesis aligns with the research goal.
            Focus specifically on:
            
            1. Conceptual alignment: Does the hypothesis address the same fundamental concepts as the research goal?
            2. Problem-solution fit: Does the hypothesis potentially solve the problem outlined in the goal?
            3. Scope appropriateness: Is the hypothesis at the right level of specificity for the goal?
            4. Scientific domain match: Does the hypothesis stay within the relevant scientific domains?
            5. Practical applicability: Would findings based on this hypothesis be useful for the stated objective?
            
            For each criterion, provide a score from 1-10 and brief justification.
            Then provide an overall proximity score (1-10) and a summary assessment of relevance.
            
            Finally, offer specific suggestions for how the hypothesis could be modified to increase its 
            relevance to the research goal, if needed.
            """
            
            proximity_evaluation = self.get_response(prompt)
            
            # Add the evaluation to the hypothesis
            evaluated_hypothesis = hypothesis.copy()
            evaluated_hypothesis['proximity_evaluation'] = proximity_evaluation
            
            # Extract proximity score and determine if hypothesis passes relevance threshold
            proximity_score, is_relevant = self._extract_proximity_info(proximity_evaluation)
            evaluated_hypothesis['proximity_score'] = proximity_score
            evaluated_hypothesis['is_relevant'] = is_relevant
            
            evaluated_hypotheses.append(evaluated_hypothesis)
            
            # Clear conversation history for the next hypothesis
            self.clear_history()
        
        # Filter out irrelevant hypotheses if specified
        return evaluated_hypotheses
    
    def filter_relevant_hypotheses(self, evaluated_hypotheses: List[Dict[str, Any]], threshold: float = 5.0) -> List[Dict[str, Any]]:
        """Filter hypotheses to keep only those above the relevance threshold.
        
        Args:
            evaluated_hypotheses: List of hypotheses with proximity evaluations
            threshold: Minimum proximity score to be considered relevant (1-10 scale)
            
        Returns:
            A filtered list of relevant hypotheses
        """
        self.logger.info(f"Filtering hypotheses with proximity threshold {threshold}")
        
        relevant_hypotheses = [h for h in evaluated_hypotheses if h.get('proximity_score', 0) >= threshold]
        self.logger.info(f"Kept {len(relevant_hypotheses)} out of {len(evaluated_hypotheses)} hypotheses")
        
        return relevant_hypotheses
    
    def _extract_proximity_info(self, evaluation: str) -> tuple[float, bool]:
        """Extract proximity score and relevance decision from evaluation text.
        
        This is a placeholder implementation. In a real system, this would use more 
        sophisticated parsing to extract structured data reliably.
        
        Args:
            evaluation: The proximity evaluation text
            
        Returns:
            A tuple of (proximity_score, is_relevant)
        """
        # Simple parsing implementation - would be more sophisticated in a real system
        proximity_score = 5.0  # Default middle score
        
        # Look for overall proximity score patterns
        score_patterns = [
            "overall proximity score: {}",
            "overall proximity score of {}",
            "proximity score: {}",
            "overall score: {}"
        ]
        
        for pattern in score_patterns:
            for i in range(1, 11):
                search_pattern = pattern.format(i)
                if search_pattern.lower() in evaluation.lower():
                    proximity_score = float(i)
                    break
        
        # Determine relevance based on score and keywords
        is_relevant = proximity_score >= 6.0
        
        # Override based on explicit statements in text
        if "not relevant" in evaluation.lower() or "irrelevant" in evaluation.lower():
            is_relevant = False
        if "highly relevant" in evaluation.lower() or "very relevant" in evaluation.lower():
            is_relevant = True
        
        return proximity_score, is_relevant
