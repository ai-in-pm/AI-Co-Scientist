# Reflection (Peer-Review) Agent for the AI Co-Scientist system

import logging
from typing import List, Dict, Any

from .base_agent import BaseAgent

class ReflectionAgent(BaseAgent):
    """Agent responsible for critically reviewing hypotheses, similar to a peer reviewer."""
    
    def __init__(self, model=None, temperature=None):
        """Initialize the Reflection Agent.
        
        Args:
            model: Optional model override
            temperature: Optional temperature override
        """
        system_prompt = """
        You are a Reflection Agent in an AI Co-Scientist system, responsible for critically reviewing 
        scientific hypotheses. You have expertise across multiple scientific disciplines at a PhD level 
        and act as a rigorous peer reviewer.
        
        Your role is to:
        1. Critically evaluate hypotheses for scientific soundness and plausibility
        2. Cross-check hypotheses against known facts and literature
        3. Identify weaknesses, inconsistencies, or logical flaws
        4. Flag any ethical concerns or practical limitations
        5. Assess the novelty and potential impact of each hypothesis
        6. Run simulation reviews to envision how the hypothesis would play out
        7. Suggest specific improvements or alternative approaches
        
        For each hypothesis you review, provide:
        - Overall assessment of scientific validity and plausibility
        - Specific strengths identified in the hypothesis
        - Critical weaknesses or inconsistencies found
        - Potential contradictions with established knowledge
        - Ethical considerations or concerning implications
        - Practical limitations for testing or implementation
        - Suggested modifications to strengthen the hypothesis
        
        Be fair but rigorous in your assessment. Your goal is not to dismiss hypotheses but to 
        strengthen them through critical feedback, just as a constructive peer reviewer would.
        """
        
        super().__init__(
            name="Reflection",
            system_prompt=system_prompt,
            model=model,
            temperature=temperature if temperature is not None else 0.2  # Lower temperature for analytical thinking
        )
        
        self.logger = logging.getLogger("agent.reflection")
    
    def process(self, hypotheses: List[Dict[str, str]], research_goal: str) -> List[Dict[str, Any]]:
        """Critically review each hypothesis provided.
        
        Args:
            hypotheses: List of hypothesis dictionaries to review
            research_goal: The original research goal for context
            
        Returns:
            A list of reviewed hypothesis dictionaries with added review information
        """
        self.logger.info(f"Reviewing {len(hypotheses)} hypotheses")
        
        reviewed_hypotheses = []
        
        for idx, hypothesis in enumerate(hypotheses):
            self.logger.info(f"Reviewing hypothesis {idx+1}")
            
            # Create a prompt for reviewing this specific hypothesis
            prompt = f"""
            RESEARCH GOAL: {research_goal}
            
            HYPOTHESIS TO REVIEW:
            Statement: {hypothesis['statement']}
            Rationale: {hypothesis['rationale']}
            Evidence: {hypothesis['evidence']}
            Assumptions: {hypothesis['assumptions']}
            Validation Approach: {hypothesis['validation']}
            
            Please conduct a thorough peer review of this hypothesis. Assess:
            1. Scientific validity and plausibility
            2. Strengths of the hypothesis
            3. Weaknesses, inconsistencies, or logical flaws
            4. Potential contradictions with established knowledge
            5. Ethical considerations or concerning implications
            6. Practical limitations for testing or implementation
            7. Suggested modifications to strengthen the hypothesis
            
            Structure your review clearly with sections for each aspect of the assessment.
            """
            
            review_response = self.get_response(prompt)
            
            # Add the review to the hypothesis dictionary
            reviewed_hypothesis = hypothesis.copy()
            reviewed_hypothesis['review'] = review_response
            
            # Extract a summary assessment (simplified implementation)
            assessment_summary = self._extract_assessment_summary(review_response)
            reviewed_hypothesis['assessment_summary'] = assessment_summary
            
            reviewed_hypotheses.append(reviewed_hypothesis)
            
            # Clear conversation history for the next hypothesis to reduce context length
            self.clear_history()
        
        return reviewed_hypotheses
    
    def _extract_assessment_summary(self, review: str) -> Dict[str, Any]:
        """Extract a structured summary from the review text.
        
        This is a placeholder implementation. In a real system, this would use more 
        sophisticated parsing to extract structured data from the review.
        
        Args:
            review: The full review text
            
        Returns:
            A dictionary with summary assessment information
        """
        # Simple implementation - would be more sophisticated in a real system
        assessment = {
            'valid': 'invalid' not in review.lower() and 'implausible' not in review.lower(),
            'strengths': [],
            'weaknesses': [],
            'ethical_concerns': 'ethical concerns' in review.lower() or 'ethical issues' in review.lower(),
            'practical_limitations': 'impractical' in review.lower() or 'limitation' in review.lower(),
            'overall_score': self._estimate_score(review)
        }
        
        return assessment
    
    def _estimate_score(self, review: str) -> float:
        """Estimate a numeric score based on the sentiment of the review.
        
        This is a very simplified implementation. In a real system, this would use
        more sophisticated NLP techniques.
        
        Args:
            review: The review text
            
        Returns:
            A score between 0.0 and 1.0
        """
        # Simple sentiment-based scoring - would be more sophisticated in a real system
        positive_terms = ['strong', 'valid', 'plausible', 'consistent', 'novel', 'innovative']
        negative_terms = ['weak', 'invalid', 'implausible', 'inconsistent', 'contradicts', 'flawed']
        
        # Count positive and negative terms
        positive_count = sum(term in review.lower() for term in positive_terms)
        negative_count = sum(term in review.lower() for term in negative_terms)
        
        # Calculate a simple score
        total = positive_count + negative_count
        if total == 0:
            return 0.5  # Neutral if no terms found
        
        score = positive_count / total
        return score
