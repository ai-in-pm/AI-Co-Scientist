# Evolution Agent for improving promising hypotheses

import logging
from typing import List, Dict, Any

from .base_agent import BaseAgent

class EvolutionAgent(BaseAgent):
    """Agent responsible for iteratively improving promising hypotheses."""
    
    def __init__(self, model=None, temperature=None):
        """Initialize the Evolution Agent.
        
        Args:
            model: Optional model override
            temperature: Optional temperature override
        """
        system_prompt = """
        You are an Evolution Agent in an AI Co-Scientist system, responsible for refining and improving 
        promising scientific hypotheses. You have expertise across multiple scientific disciplines at a PhD level.
        
        Your role is to:
        1. Take promising hypotheses and enhance them based on feedback and critical evaluation
        2. Incorporate elements from different hypotheses to create stronger variants
        3. Address specific weaknesses identified in the peer review process
        4. Simplify overly complex hypotheses while maintaining their core insights
        5. Extend hypotheses into new directions when appropriate
        6. Ensure all improvements maintain scientific rigor and testability
        
        When evolving a hypothesis, consider:
        - How can contradictions or inconsistencies be resolved?
        - Can elements of other hypotheses be integrated to strengthen this one?
        - Is there a simpler way to express the core idea without losing explanatory power?
        - Are there aspects of the hypothesis that could be made more specific or testable?
        - How can the hypothesis better address the original research goal?
        - What additional evidence or context could make the hypothesis more compelling?
        
        Your output should be a significantly improved hypothesis that maintains the core insight of the 
        original while addressing its weaknesses and limitations.
        """
        
        super().__init__(
            name="Evolution",
            system_prompt=system_prompt,
            model=model,
            temperature=temperature if temperature is not None else 0.5  # Balanced temperature for creativity and focus
        )
        
        self.logger = logging.getLogger("agent.evolution")
    
    def process(self, ranked_hypotheses: List[Dict[str, Any]], research_goal: str) -> List[Dict[str, Any]]:
        """Improve top-ranked hypotheses based on their reviews and rankings.
        
        Args:
            ranked_hypotheses: List of hypothesis dictionaries with ranking information
            research_goal: The original research goal for context
            
        Returns:
            A list of improved hypothesis dictionaries
        """
        self.logger.info("Beginning hypothesis evolution process")
        
        # Sort hypotheses by rank if not already sorted
        sorted_hypotheses = sorted(ranked_hypotheses, key=lambda h: h.get('rank', float('inf')))
        
        # Take the top hypotheses to evolve (usually top 2-3)
        top_k = min(3, len(sorted_hypotheses))
        top_hypotheses = sorted_hypotheses[:top_k]
        
        evolved_hypotheses = []
        
        # First, evolve each top hypothesis individually
        for idx, hypothesis in enumerate(top_hypotheses):
            self.logger.info(f"Evolving hypothesis {idx+1} (rank {hypothesis.get('rank', 'unknown')})")
            
            # Extract review feedback if available
            review_feedback = hypothesis.get('review', '')
            if len(review_feedback) > 1000:  # Truncate long reviews
                review_feedback = review_feedback[:1000] + "..."
            
            prompt = f"""
            RESEARCH GOAL: {research_goal}
            
            HYPOTHESIS TO EVOLVE:
            Statement: {hypothesis['statement']}
            Rationale: {hypothesis['rationale']}
            Evidence: {hypothesis['evidence']}
            Assumptions: {hypothesis['assumptions']}
            Validation Approach: {hypothesis['validation']}
            
            REVIEW FEEDBACK:
            {review_feedback}
            
            Please evolve this hypothesis to address its weaknesses while maintaining its core strengths.
            Specifically:
            1. Refine the hypothesis statement to be more precise and testable
            2. Address any inconsistencies or logical flaws identified in the review
            3. Strengthen the rationale with additional scientific context if needed
            4. Reconsider any problematic assumptions
            5. Improve the validation approach to be more feasible and conclusive
            
            Provide the evolved hypothesis with the same structure as the original (statement, rationale, 
            evidence, assumptions, validation).
            """
            
            evolution_response = self.get_response(prompt)
            
            # Process the response into a structured evolved hypothesis
            evolved_hypothesis = self._parse_evolved_hypothesis(evolution_response, hypothesis)
            evolved_hypothesis['original_rank'] = hypothesis.get('rank')
            evolved_hypothesis['evolution_type'] = 'individual_refinement'
            
            evolved_hypotheses.append(evolved_hypothesis)
            
            # Clear conversation history for the next hypothesis
            self.clear_history()
        
        # Then, try to combine elements from top 2 hypotheses if available
        if len(top_hypotheses) >= 2:
            self.logger.info("Attempting to combine elements from top hypotheses")
            
            hyp1, hyp2 = top_hypotheses[0], top_hypotheses[1]
            
            prompt = f"""
            RESEARCH GOAL: {research_goal}
            
            HYPOTHESIS 1 (Rank {hyp1.get('rank', 1)}):
            Statement: {hyp1['statement']}
            Rationale: {hyp1['rationale'][:300]}...
            
            HYPOTHESIS 2 (Rank {hyp2.get('rank', 2)}):
            Statement: {hyp2['statement']}
            Rationale: {hyp2['rationale'][:300]}...
            
            These are the top two hypotheses addressing the research goal. Each has strengths and weaknesses.
            Your task is to create a new hybrid hypothesis that combines the strongest elements of both.
            
            Consider:
            - Is there a way to integrate the core insights of both hypotheses?
            - Can complementary aspects of each be combined into a stronger whole?
            - Does one hypothesis address weaknesses in the other?
            - Is there a more general framework that could encompass both ideas?
            
            Create a new hybrid hypothesis with the standard structure (statement, rationale, evidence, 
            assumptions, validation). This should not simply be a list of both hypotheses, but a true 
            integration that could potentially be stronger than either original hypothesis.
            """
            
            hybrid_response = self.get_response(prompt)
            
            # Process the response into a structured hybrid hypothesis
            hybrid_hypothesis = self._parse_evolved_hypothesis(hybrid_response)
            hybrid_hypothesis['original_ranks'] = [hyp1.get('rank'), hyp2.get('rank')]
            hybrid_hypothesis['evolution_type'] = 'hypothesis_combination'
            hybrid_hypothesis['parent_hypotheses'] = [hyp1['statement'], hyp2['statement']]
            
            evolved_hypotheses.append(hybrid_hypothesis)
        
        return evolved_hypotheses
    
    def _parse_evolved_hypothesis(self, evolution_text: str, original_hypothesis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Parse the evolution text into a structured hypothesis.
        
        This is a placeholder implementation. In a real system, this would use more 
        sophisticated parsing to extract structured data reliably.
        
        Args:
            evolution_text: The raw text containing the evolved hypothesis
            original_hypothesis: The original hypothesis dictionary (optional)
            
        Returns:
            A structured hypothesis dictionary
        """
        # Simple parsing implementation - would be more sophisticated in a real system
        evolved_hypothesis = {
            'statement': '',
            'rationale': '',
            'evidence': '',
            'assumptions': '',
            'validation': '',
            'evolution_text': evolution_text  # Store the full text for reference
        }
        
        # Initialize with original values if provided
        if original_hypothesis:
            evolved_hypothesis = {**original_hypothesis.copy(), **evolved_hypothesis}
            # Remove review and scoring info from the original
            for key in ['review', 'assessment_summary', 'rank', 'scores', 'evaluation', 'overall_score', 'wins']:
                if key in evolved_hypothesis:
                    del evolved_hypothesis[key]
        
        # Extract sections based on keywords
        sections = evolution_text.split('\n\n')
        current_section = None
        
        for section in sections:
            lower_section = section.lower()
            
            if 'statement' in lower_section and ':' in section:
                evolved_hypothesis['statement'] = section.split(':', 1)[1].strip()
            elif 'rationale' in lower_section and ':' in section:
                evolved_hypothesis['rationale'] = section.split(':', 1)[1].strip()
            elif 'evidence' in lower_section and ':' in section:
                evolved_hypothesis['evidence'] = section.split(':', 1)[1].strip()
            elif 'assumptions' in lower_section and ':' in section:
                evolved_hypothesis['assumptions'] = section.split(':', 1)[1].strip()
            elif 'validation' in lower_section and ':' in section:
                evolved_hypothesis['validation'] = section.split(':', 1)[1].strip()
        
        return evolved_hypothesis
