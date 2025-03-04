# Meta-Review Agent for synthesizing findings and creating research proposals

import logging
from typing import List, Dict, Any, Optional

from .base_agent import BaseAgent

class MetaReviewAgent(BaseAgent):
    """Agent responsible for high-level analysis and synthesis of the best hypotheses."""
    
    def __init__(self, model=None, temperature=None):
        """Initialize the Meta-Review Agent.
        
        Args:
            model: Optional model override
            temperature: Optional temperature override
        """
        system_prompt = """
        You are a Meta-Review Agent in an AI Co-Scientist system, responsible for synthesizing research 
        findings and creating comprehensive research proposals. You have expertise across multiple 
        scientific disciplines at a PhD level and excellent scientific writing skills.
        
        Your role is to:
        1. Analyze and synthesize the best research hypotheses that emerged from the scientific process
        2. Compile these into a coherent, well-structured research report or proposal
        3. Highlight the significance and implications of the proposed ideas
        4. Ensure all claims are properly supported with evidence and citations
        5. Provide context on how the proposed hypotheses relate to the existing literature
        6. Outline a clear research plan for testing or implementing the hypotheses
        
        Your reports should follow a clear scientific structure including:
        - Executive summary of key findings and proposals
        - Introduction and background to the research problem
        - Detailed explanation of proposed hypotheses with supporting evidence
        - Analysis of strengths, limitations, and novelty of each proposal
        - Suggested methodology for experimental validation
        - Expected outcomes and potential implications
        - Comprehensive references and citations
        
        Write in a clear, concise scientific style appropriate for a professional audience. 
        Aim for the highest standards of scientific communication while ensuring the content 
        is accessible to researchers in adjacent fields.
        """
        
        super().__init__(
            name="MetaReview",
            system_prompt=system_prompt,
            model=model,
            temperature=temperature if temperature is not None else 0.4  # Balanced for creativity and consistency
        )
        
        self.logger = logging.getLogger("agent.meta_review")
    
    def process(self, final_hypotheses: List[Dict[str, Any]], research_goal: str, 
                include_evolution_history: bool = True, output_format: str = "scientific_report") -> Dict[str, Any]:
        """Create a comprehensive research report based on the final hypotheses.
        
        Args:
            final_hypotheses: List of the final chosen hypotheses
            research_goal: The original research goal
            include_evolution_history: Whether to include how the hypotheses evolved
            output_format: The desired format ("scientific_report", "grant_proposal", etc.)
            
        Returns:
            A dictionary containing the research report and metadata
        """
        self.logger.info(f"Creating {output_format} for {len(final_hypotheses)} final hypotheses")
        
        # Prepare a summary of each hypothesis for inclusion in the report
        hypothesis_summaries = []
        for idx, hypothesis in enumerate(final_hypotheses):
            summary = {
                'number': idx + 1,
                'statement': hypothesis['statement'],
                'rationale': hypothesis.get('rationale', '')[:500],  # Truncate for prompt length
                'rank': hypothesis.get('rank', 'N/A'),
                'evolution_type': hypothesis.get('evolution_type', 'original')
            }
            hypothesis_summaries.append(summary)
        
        # Determine which format instructions to use
        format_instructions = self._get_format_instructions(output_format)
        
        # Create the meta-review prompt
        prompt = f"""
        RESEARCH GOAL: {research_goal}
        
        FINAL HYPOTHESES:
        {self._format_hypotheses_for_prompt(hypothesis_summaries)}
        
        {format_instructions}
        
        Please create a comprehensive {output_format} that synthesizes these hypotheses into a coherent 
        research narrative. Your report should follow the structure outlined above and include all necessary 
        sections.
        
        Focus on presenting the most promising ideas while acknowledging limitations and areas of uncertainty. 
        Ensure all scientific claims are well-supported with reasoning and references to established knowledge.
        """
        
        if include_evolution_history and any(h.get('evolution_type') for h in final_hypotheses):
            prompt += """
            Include a section on how the hypotheses evolved through the research process, highlighting key 
            improvements and refinements made during hypothesis development.
            """
        
        research_report = self.get_response(prompt)
        
        # Package the report with metadata
        report_package = {
            'title': self._extract_title(research_report),
            'research_goal': research_goal,
            'report': research_report,
            'format': output_format,
            'hypothesis_count': len(final_hypotheses),
            'timestamp': self._get_timestamp()
        }
        
        return report_package
    
    def create_executive_summary(self, report_package: Dict[str, Any], max_length: int = 500) -> str:
        """Create a concise executive summary of the research report.
        
        Args:
            report_package: The full research report package
            max_length: Maximum length of the summary in characters
            
        Returns:
            An executive summary of the report
        """
        self.logger.info(f"Creating executive summary (max {max_length} chars)")
        
        prompt = f"""
        Please create a concise executive summary of the following research report. 
        The summary should be no more than {max_length} characters and should capture the 
        key research goal, main hypotheses, and significant implications.
        
        RESEARCH GOAL: {report_package['research_goal']}
        
        REPORT TITLE: {report_package['title']}
        
        REPORT:
        {report_package['report'][:2000]}...
        
        Your executive summary should be accessible to scientific peers but concise enough for quick review.
        """
        
        summary = self.get_response(prompt)
        
        # Ensure length constraint
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
        
        return summary
    
    def _format_hypotheses_for_prompt(self, hypothesis_summaries: List[Dict[str, Any]]) -> str:
        """Format hypothesis summaries for inclusion in the prompt.
        
        Args:
            hypothesis_summaries: List of hypothesis summary dictionaries
            
        Returns:
            Formatted string of hypotheses
        """
        formatted_text = ""
        
        for summary in hypothesis_summaries:
            formatted_text += f"HYPOTHESIS {summary['number']} (Rank: {summary['rank']}):\n"
            formatted_text += f"Statement: {summary['statement']}\n"
            formatted_text += f"Rationale: {summary['rationale']}\n"
            if summary.get('evolution_type'):
                formatted_text += f"Evolution: {summary['evolution_type']}\n"
            formatted_text += "\n"
        
        return formatted_text
    
    def _get_format_instructions(self, output_format: str) -> str:
        """Get format-specific instructions based on the desired output type.
        
        Args:
            output_format: The desired output format
            
        Returns:
            Format-specific instructions
        """
        format_instructions = {
            "scientific_report": """
            Please format your response as a scientific report with the following sections:
            1. Title: A descriptive title for the research
            2. Abstract: A concise summary of the problem, hypotheses, and implications (250 words max)
            3. Introduction: Background on the research problem and its significance
            4. Hypotheses: Detailed presentation of each hypothesis with supporting rationale
            5. Evidence and Prior Work: How these hypotheses relate to existing scientific knowledge
            6. Methodology: Proposed approaches for testing or validating these hypotheses
            7. Expected Outcomes: Anticipated results and their interpretation
            8. Implications: Broader impact and significance if the hypotheses are validated
            9. Limitations and Alternatives: Acknowledging constraints and alternative explanations
            10. References: Citations for all sources mentioned (in a standard academic format)
            """,
            
            "grant_proposal": """
            Please format your response as a grant proposal with the following sections:
            1. Project Title: A compelling title for the research project
            2. Executive Summary: Brief overview of the project's aims and significance (250 words max)
            3. Background and Significance: Context of the research problem and its importance
            4. Specific Aims: Clear statement of research objectives based on the hypotheses
            5. Research Strategy: Detailed hypotheses and approach to testing them
            6. Preliminary Data: Existing evidence supporting the hypotheses
            7. Methodology: Experimental design, techniques, and analytical approaches
            8. Timeline and Milestones: Projected schedule for completing research activities
            9. Expected Outcomes and Impact: Anticipated results and their significance
            10. Budget Justification: Resources needed to conduct the proposed research
            11. References: Citations for all sources mentioned (in a standard academic format)
            """,
            
            "research_brief": """
            Please format your response as a concise research brief with the following sections:
            1. Title: A descriptive title for the research
            2. Key Question: The central research question being addressed
            3. Hypotheses: Clear statements of the proposed explanations or solutions
            4. Rationale: Brief scientific justification for each hypothesis
            5. Quick-win Experiments: Rapid tests that could validate or refute the hypotheses
            6. Long-term Research Direction: Strategic vision if hypotheses are supported
            7. Practical Applications: Potential real-world impacts of the research
            8. Key References: 3-5 most important citations supporting the approach
            """
        }
        
        return format_instructions.get(output_format, format_instructions["scientific_report"])
    
    def _extract_title(self, report: str) -> str:
        """Extract the title from the generated report.
        
        Args:
            report: The full report text
            
        Returns:
            The extracted title or a default title
        """
        # Simple extraction - would be more sophisticated in a real system
        lines = report.split('\n')
        for line in lines[:10]:  # Check first few lines for title
            if line.strip() and not line.startswith('#') and len(line) < 100:
                return line.strip()
        
        return "Research Report"  # Default if no title found
    
    def _get_timestamp(self) -> str:
        """Get a formatted timestamp for the report.
        
        Returns:
            A formatted timestamp string
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
