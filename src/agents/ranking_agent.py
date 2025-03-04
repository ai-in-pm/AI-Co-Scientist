# Ranking Agent for evaluating and comparing hypotheses

import logging
from typing import List, Dict, Any, Tuple

from .base_agent import BaseAgent

class RankingAgent(BaseAgent):
    """Agent responsible for comparing and ranking hypotheses based on defined criteria."""
    
    def __init__(self, model=None, temperature=None):
        """Initialize the Ranking Agent.
        
        Args:
            model: Optional model override
            temperature: Optional temperature override
        """
        system_prompt = """
        You are a Ranking Agent in an AI Co-Scientist system, responsible for comparing and ranking 
        scientific hypotheses using a tournament-style evaluation. You have expertise across multiple 
        scientific disciplines at a PhD level.
        
        Your role is to:
        1. Evaluate hypotheses against defined criteria including novelty, plausibility, and relevance
        2. Compare hypotheses in a tournament style, identifying relative strengths and weaknesses
        3. Assign scores and rankings to hypotheses based on their scientific merit
        4. Provide justification for your rankings with specific reasoning
        5. Consider tradeoffs between different evaluation criteria
        
        When comparing hypotheses, consider:
        - Novelty: Does the hypothesis represent a significant advance beyond current knowledge?
        - Plausibility: Is the hypothesis consistent with established scientific principles?
        - Relevance: How closely does the hypothesis address the original research goal?
        - Testability: How feasible is it to validate or falsify the hypothesis?
        - Potential impact: If true, how significant would the implications be?
        - Parsimony: Does the hypothesis provide a simple explanation without unnecessary complexity?
        - Breadth of explanation: How many observations or phenomena does the hypothesis explain?
        
        Your assessments should be balanced, fair, and focused on scientific merit rather than 
        personal preference. Provide clear reasoning for each comparative judgment.
        """
        
        super().__init__(
            name="Ranking",
            system_prompt=system_prompt,
            model=model,
            temperature=temperature if temperature is not None else 0.3  # Lower temperature for consistent evaluation
        )
        
        self.logger = logging.getLogger("agent.ranking")
    
    def rank_hypotheses(self, research_goal: str, hypotheses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank the hypotheses based on the research goal.
        
        Args:
            research_goal: The research goal or question
            hypotheses: List of hypothesis dictionaries to rank
            
        Returns:
            A list of ranked hypothesis dictionaries
        """
        self.logger.info(f"Ranking hypotheses for research goal: {research_goal}")
        return self.process(hypotheses, research_goal)
    
    def process(self, reviewed_hypotheses: List[Dict[str, Any]], research_goal: str) -> List[Dict[str, Any]]:
        """Rank the reviewed hypotheses based on their scientific merit.
        
        Args:
            reviewed_hypotheses: List of hypothesis dictionaries with review information
            research_goal: The original research goal for context
            
        Returns:
            A list of ranked hypothesis dictionaries with added ranking information
        """
        self.logger.info(f"Ranking {len(reviewed_hypotheses)} hypotheses")
        
        # For a small number of hypotheses, we can do pairwise comparisons
        if len(reviewed_hypotheses) <= 5:
            return self._rank_by_pairwise_comparison(reviewed_hypotheses, research_goal)
        else:
            # For larger sets, we use a scoring approach
            return self._rank_by_scoring(reviewed_hypotheses, research_goal)
    
    def _rank_by_pairwise_comparison(self, hypotheses: List[Dict[str, Any]], research_goal: str) -> List[Dict[str, Any]]:
        """Rank hypotheses using pairwise comparisons in a tournament style.
        
        Args:
            hypotheses: List of hypothesis dictionaries to rank
            research_goal: The original research goal for context
            
        Returns:
            A list of ranked hypothesis dictionaries
        """
        self.logger.info("Using pairwise comparison ranking method")
        
        # Create all possible pairs for comparison
        pairs = []
        for i in range(len(hypotheses)):
            for j in range(i+1, len(hypotheses)):
                pairs.append((i, j))
        
        # Track wins for each hypothesis
        wins = [0] * len(hypotheses)
        comparisons = []
        
        for pair in pairs:
            i, j = pair
            hyp1, hyp2 = hypotheses[i], hypotheses[j]
            
            prompt = f"""
            RESEARCH GOAL: {research_goal}
            
            HYPOTHESIS 1:
            Statement: {hyp1.get('hypothesis', hyp1.get('statement', 'No statement provided'))}
            
            HYPOTHESIS 2:
            Statement: {hyp2.get('hypothesis', hyp2.get('statement', 'No statement provided'))}
            
            Compare these two hypotheses based on the following criteria:
            1. Novelty: Does the hypothesis represent a significant advance beyond current knowledge?
            2. Plausibility: Is the hypothesis consistent with established scientific principles?
            3. Relevance: How closely does the hypothesis address the original research goal?
            4. Testability: How feasible is it to validate or falsify the hypothesis?
            5. Potential impact: If true, how significant would the implications be?
            
            Provide a detailed comparison, noting the strengths and weaknesses of each hypothesis relative 
            to the other. Then determine which hypothesis is superior overall, being explicit about 
            which hypothesis (1 or 2) is the winner.
            """
            
            comparison_result = self.get_response(prompt)
            
            # Determine the winner based on the comparison
            winner = self._determine_winner(comparison_result, 1, 2)
            
            # Record the comparison and update wins
            comparison = {
                'hypothesis1_idx': i,
                'hypothesis2_idx': j,
                'winner': winner,
                'reasoning': comparison_result
            }
            comparisons.append(comparison)
            
            if winner == 1:
                wins[i] += 1
            elif winner == 2:
                wins[j] += 1
            
            # Clear conversation history for the next comparison
            self.clear_history()
        
        # Rank hypotheses based on number of wins
        ranked_indices = sorted(range(len(wins)), key=lambda k: wins[k], reverse=True)
        
        # Create the ranked list of hypotheses
        ranked_hypotheses = []
        for rank, idx in enumerate(ranked_indices):
            ranked_hypothesis = hypotheses[idx].copy()
            ranked_hypothesis['rank'] = rank + 1
            ranked_hypothesis['wins'] = wins[idx]
            ranked_hypothesis['total_comparisons'] = len([c for c in comparisons if c['hypothesis1_idx'] == idx or c['hypothesis2_idx'] == idx])
            ranked_hypotheses.append(ranked_hypothesis)
        
        return ranked_hypotheses
    
    def _rank_by_scoring(self, hypotheses: List[Dict[str, Any]], research_goal: str) -> List[Dict[str, Any]]:
        """Rank hypotheses by assigning scores to each one individually.
        
        Args:
            hypotheses: List of hypothesis dictionaries to rank
            research_goal: The original research goal for context
            
        Returns:
            A list of ranked hypothesis dictionaries
        """
        self.logger.info("Using scoring-based ranking method")
        
        scored_hypotheses = []
        
        for idx, hypothesis in enumerate(hypotheses):
            prompt = f"""
            RESEARCH GOAL: {research_goal}
            
            HYPOTHESIS TO EVALUATE:
            Statement: {hypothesis.get('hypothesis', hypothesis.get('statement', 'No statement provided'))}
            Rationale: {hypothesis.get('rationale', 'No rationale provided')}
            Review Summary: {hypothesis.get('review', 'No review available')[:500]}...
            
            Evaluate this hypothesis on the following criteria using a scale of 1-10:
            1. Novelty (1=Well-known, 10=Revolutionary)
            2. Plausibility (1=Implausible, 10=Highly plausible)
            3. Relevance (1=Unrelated to goal, 10=Directly addresses goal)
            4. Testability (1=Untestable, 10=Easily testable)
            5. Potential impact (1=Minimal impact, 10=Field-changing)
            
            For each criterion, provide a numeric score AND a brief justification.
            Finally, calculate an overall score as the weighted average of the individual scores.
            
            Format your response as follows:
            Novelty: [score] - [justification]
            Plausibility: [score] - [justification]
            Relevance: [score] - [justification]
            Testability: [score] - [justification]
            Potential impact: [score] - [justification]
            Overall score: [weighted average score] - [brief summary]
            """
            
            evaluation = self.get_response(prompt)
            
            # Extract scores from the evaluation (simplified implementation)
            scores = self._extract_scores(evaluation)
            
            scored_hypothesis = hypothesis.copy()
            scored_hypothesis['evaluation'] = evaluation
            scored_hypothesis['scores'] = scores
            scored_hypothesis['overall_score'] = sum(scores.values()) / len(scores) if scores else 0
            
            scored_hypotheses.append(scored_hypothesis)
            
            # Clear conversation history for the next hypothesis
            self.clear_history()
        
        # Rank hypotheses based on overall score
        ranked_hypotheses = sorted(scored_hypotheses, key=lambda h: h['overall_score'], reverse=True)
        
        # Add rank
        for rank, hypothesis in enumerate(ranked_hypotheses):
            hypothesis['rank'] = rank + 1
        
        return ranked_hypotheses
    
    def _determine_winner(self, comparison_text: str, hyp1_id: int, hyp2_id: int) -> int:
        """Determine the winner of a pairwise comparison based on the comparison text.
        
        Args:
            comparison_text: The text of the comparison
            hyp1_id: The ID of the first hypothesis
            hyp2_id: The ID of the second hypothesis
            
        Returns:
            The ID of the winning hypothesis (1 or 2), or 0 if it's a tie
        """
        # Simple rule-based determination - would be more sophisticated in a real system
        lower_text = comparison_text.lower()
        
        # Look for clear statements about the winner
        if f"hypothesis {hyp1_id} is superior" in lower_text or f"hypothesis {hyp1_id} is stronger" in lower_text:
            return hyp1_id
        elif f"hypothesis {hyp2_id} is superior" in lower_text or f"hypothesis {hyp2_id} is stronger" in lower_text:
            return hyp2_id
        
        # Count mentions of strengths for each
        hyp1_strength_count = lower_text.count(f"hypothesis {hyp1_id} is more") + lower_text.count(f"hypothesis {hyp1_id} has higher")
        hyp2_strength_count = lower_text.count(f"hypothesis {hyp2_id} is more") + lower_text.count(f"hypothesis {hyp2_id} has higher")
        
        if hyp1_strength_count > hyp2_strength_count:
            return hyp1_id
        elif hyp2_strength_count > hyp1_strength_count:
            return hyp2_id
        
        # If no clear winner found, check last few sentences for conclusion
        last_sentences = '.'.join(comparison_text.split('.')[-3:])
        if f"hypothesis {hyp1_id}" in last_sentences.lower() and f"hypothesis {hyp2_id}" not in last_sentences.lower():
            return hyp1_id
        elif f"hypothesis {hyp2_id}" in last_sentences.lower() and f"hypothesis {hyp1_id}" not in last_sentences.lower():
            return hyp2_id
        
        # If still no clear winner, return a tie
        return 0
    
    def _extract_scores(self, evaluation: str) -> Dict[str, float]:
        """Extract numerical scores from the evaluation text.
        
        This is a placeholder implementation. In a real system, this would use more 
        sophisticated parsing to extract scores reliably.
        
        Args:
            evaluation: The evaluation text
            
        Returns:
            A dictionary of criterion names to scores
        """
        # Simple parsing implementation - would be more sophisticated in a real system
        scores = {}
        criteria = ['novelty', 'plausibility', 'relevance', 'testability', 'potential impact']
        
        for criterion in criteria:
            # Look for patterns like "Novelty: 8/10" or "Novelty - 8"
            patterns = [f"{criterion}: {i}" for i in range(1, 11)]
            patterns.extend([f"{criterion} - {i}" for i in range(1, 11)])
            patterns.extend([f"{criterion}: {i}/10" for i in range(1, 11)])
            
            for pattern in patterns:
                if pattern.lower() in evaluation.lower():
                    score = int(pattern.split(" ")[-1].replace("/10", ""))
                    scores[criterion] = score
                    break
        
        return scores
