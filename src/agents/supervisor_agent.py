# Supervisor Agent for coordinating the multi-agent system

import logging
from typing import List, Dict, Any, Optional
import json

from .base_agent import BaseAgent

class SupervisorAgent(BaseAgent):
    """Agent responsible for coordinating all other agents in the system."""
    
    def __init__(self, model=None, temperature=None):
        """Initialize the Supervisor Agent.
        
        Args:
            model: Optional model override
            temperature: Optional temperature override
        """
        system_prompt = """
        You are a Supervisor Agent in an AI Co-Scientist system, responsible for coordinating 
        the entire research workflow across multiple specialized agents. You have expertise across 
        multiple scientific disciplines at a PhD level and exceptional project management skills.
        
        Your role is to:
        1. Parse and understand research goals from human researchers
        2. Break down complex research problems into manageable components
        3. Determine which agents to deploy for each task and in what sequence
        4. Allocate computational resources efficiently across the agent system
        5. Track progress, identify bottlenecks, and adjust the workflow as needed
        6. Ensure the final output meets the researcher's expectations
        
        You will direct the following specialized agents:
        - Generation Agent: Creates initial hypotheses based on research goals
        - Reflection Agent: Critically reviews hypotheses for scientific soundness
        - Ranking Agent: Compares and evaluates hypotheses against defined criteria
        - Evolution Agent: Refines promising hypotheses based on feedback
        - Proximity Agent: Ensures hypotheses remain relevant to research goals
        - Meta-Review Agent: Synthesizes findings into coherent research reports
        
        Your decisions should optimize for both thoroughness and efficiency in the scientific process.
        You are the conductor of this research orchestra - ensure all agents work in harmony toward 
        generating high-quality scientific output.
        """
        
        super().__init__(
            name="Supervisor",
            system_prompt=system_prompt,
            model=model,
            temperature=temperature if temperature is not None else 0.3  # Lower temperature for consistent planning
        )
        
        self.logger = logging.getLogger("agent.supervisor")
        self.task_history = []  # Track completed tasks
    
    def process(self, research_query: str, session_config: Optional[Dict] = None) -> Dict[str, Any]:
        """Process a research query by creating and executing a research plan.
        
        Args:
            research_query: The research query or goal from the human researcher
            session_config: Optional configuration for the session
            
        Returns:
            A dictionary containing the research plan, execution status, and results
        """
        self.logger.info(f"Processing research query: {research_query}")
        
        # Analyze the research query
        query_analysis = self._analyze_research_query(research_query)
        
        # Create a research plan
        research_plan = self._create_research_plan(research_query, query_analysis, session_config)
        
        # Return the plan for execution by the main system
        return {
            'research_query': research_query,
            'query_analysis': query_analysis,
            'research_plan': research_plan,
            'status': 'ready_for_execution'
        }
    
    def update_plan(self, current_plan: Dict, execution_status: Dict, user_feedback: Optional[str] = None) -> Dict:
        """Update the research plan based on execution status and user feedback.
        
        Args:
            current_plan: The current research plan
            execution_status: Status of executed steps
            user_feedback: Optional feedback from the human researcher
            
        Returns:
            Updated research plan
        """
        self.logger.info("Updating research plan based on execution status and feedback")
        
        # Record the completed steps
        self.task_history.extend(execution_status.get('completed_steps', []))
        
        # Create a prompt to update the plan
        prompt = f"""
        CURRENT RESEARCH PLAN:
        {json.dumps(current_plan, indent=2)}
        
        EXECUTION STATUS:
        Completed steps: {len(execution_status.get('completed_steps', []))}
        Current step: {execution_status.get('current_step', 'unknown')}
        Issues encountered: {execution_status.get('issues', 'none')}
        """
        
        if user_feedback:
            prompt += f"""
            
            USER FEEDBACK:
            {user_feedback}
            """
        
        prompt += """
        
        Based on this information, please update the research plan. You may:
        1. Continue with the existing plan if it's progressing well
        2. Modify upcoming steps to address issues or incorporate feedback
        3. Add new steps if additional tasks are required
        4. Remove planned steps that are no longer necessary
        
        Provide your updated plan in a structured format with clear reasoning for any changes.
        """
        
        response = self.get_response(prompt)
        
        # Extract the updated plan (simplified implementation)
        updated_plan = self._extract_updated_plan(response, current_plan)
        
        # Mark the plan as updated
        updated_plan['last_updated'] = self._get_timestamp()
        updated_plan['update_reason'] = 'execution_status_and_feedback' if user_feedback else 'execution_status'
        
        return updated_plan
    
    def _analyze_research_query(self, research_query: str) -> Dict[str, Any]:
        """Analyze the research query to determine its characteristics.
        
        Args:
            research_query: The research query from the human researcher
            
        Returns:
            A dictionary with analysis of the query
        """
        self.logger.info("Analyzing research query")
        
        prompt = f"""
        RESEARCH QUERY: {research_query}
        
        Please analyze this research query to help develop an effective research plan.
        Specifically:
        
        1. Identify the primary scientific domain(s) this query relates to (e.g., biology, physics, etc.)
        2. Determine the type of research goal (e.g., explanation, prediction, design, discovery)
        3. Assess the scope and complexity of the query (narrow/focused vs. broad/complex)
        4. Identify key concepts, variables, or entities that will be central to this research
        5. Note any constraints or special requirements mentioned in the query
        6. Suggest what background knowledge might be most relevant to address this query
        
        Provide your analysis in a structured format that can guide the research planning process.
        """
        
        analysis_response = self.get_response(prompt)
        
        # Process the response into a structured analysis (simplified implementation)
        analysis = self._extract_query_analysis(analysis_response)
        
        return analysis
    
    def _create_research_plan(self, research_query: str, query_analysis: Dict[str, Any], 
                              session_config: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a detailed research plan based on the query and its analysis.
        
        Args:
            research_query: The original research query
            query_analysis: Analysis of the research query
            session_config: Optional configuration for the session
            
        Returns:
            A dictionary containing the research plan
        """
        self.logger.info("Creating research plan")
        
        # Extract configuration parameters or use defaults
        config = session_config or {}
        hypothesis_count = config.get('hypothesis_count', 3)
        iteration_limit = config.get('iteration_limit', 2)
        output_format = config.get('output_format', 'scientific_report')
        
        # Default agent sequence for a typical research workflow
        default_sequence = [
            {"agent": "Generation", "task": "generate_initial_hypotheses", "params": {"count": hypothesis_count}},
            {"agent": "Reflection", "task": "review_hypotheses", "params": {}},
            {"agent": "Proximity", "task": "evaluate_relevance", "params": {"threshold": 6.0}},
            {"agent": "Ranking", "task": "rank_hypotheses", "params": {}},
            {"agent": "Evolution", "task": "improve_hypotheses", "params": {"iterations": iteration_limit}},
            {"agent": "Ranking", "task": "rank_final_hypotheses", "params": {}},
            {"agent": "MetaReview", "task": "create_research_report", "params": {"format": output_format}}
        ]
        
        # Create a plan tailored to this specific query
        prompt = f"""
        RESEARCH QUERY: {research_query}
        
        QUERY ANALYSIS:
        {json.dumps(query_analysis, indent=2)}
        
        SESSION CONFIGURATION:
        {json.dumps(config, indent=2)}
        
        Based on this research query and analysis, please create a detailed research plan utilizing our 
        multi-agent system. The default sequence of agent tasks is:
        
        {json.dumps(default_sequence, indent=2)}
        
        You may modify this sequence if warranted by the specific research query. Consider:
        - Adding additional steps for complex queries
        - Removing unnecessary steps for simpler queries
        - Adjusting parameters for each agent based on the query characteristics
        - Adding iteration loops if appropriate for this type of research
        
        Provide a justified research plan that will achieve the researcher's goals efficiently.
        """
        
        plan_response = self.get_response(prompt)
        
        # Extract the research plan (simplified implementation)
        research_plan = self._extract_research_plan(plan_response, default_sequence)
        
        # Add metadata to the plan
        research_plan['research_query'] = research_query
        research_plan['created_at'] = self._get_timestamp()
        research_plan['configuration'] = config
        
        return research_plan
    
    def _extract_query_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Extract structured analysis from the text response.
        
        This is a placeholder implementation. In a real system, this would use more 
        sophisticated parsing to extract structured data reliably.
        
        Args:
            analysis_text: The raw analysis text
            
        Returns:
            A structured analysis dictionary
        """
        # Simple parsing implementation - would be more sophisticated in a real system
        analysis = {
            'domains': [],
            'research_type': '',
            'scope': '',
            'key_concepts': [],
            'constraints': [],
            'relevant_background': []
        }
        
        # Extract domains
        if 'domain' in analysis_text.lower():
            domain_section = self._extract_section(analysis_text, 'domain', 200)
            domains = [d.strip() for d in domain_section.split(',')]
            analysis['domains'] = [d for d in domains if d]
        
        # Extract research type
        research_types = ['explanation', 'prediction', 'design', 'discovery', 'exploration', 'validation']
        for r_type in research_types:
            if r_type in analysis_text.lower():
                analysis['research_type'] = r_type
                break
        
        # Extract scope
        scope_terms = {'narrow': 'narrow', 'focused': 'narrow', 'specific': 'narrow', 
                      'broad': 'broad', 'complex': 'broad', 'wide': 'broad'}
        for term, scope in scope_terms.items():
            if term in analysis_text.lower():
                analysis['scope'] = scope
                break
        
        # Extract key concepts
        if 'concept' in analysis_text.lower() or 'key' in analysis_text.lower():
            concept_section = self._extract_section(analysis_text, 'concept', 300)
            concepts = [c.strip() for c in concept_section.split(',')] 
            analysis['key_concepts'] = [c for c in concepts if c and len(c) > 2]
        
        return analysis
    
    def _extract_section(self, text: str, keyword: str, max_chars: int = 200) -> str:
        """Extract a section of text containing a keyword.
        
        Args:
            text: The full text
            keyword: Keyword to search for
            max_chars: Maximum characters to extract
            
        Returns:
            The extracted section
        """
        keyword_index = text.lower().find(keyword.lower())
        if keyword_index == -1:
            return ""
        
        start = max(0, keyword_index - 20)
        end = min(len(text), keyword_index + max_chars)
        
        section = text[start:end]
        
        # Try to find sentence or paragraph boundaries
        if '.' in section:
            last_period = section.rindex('.')
            if last_period > len(section) // 2:
                section = section[:last_period + 1]
        
        return section
    
    def _extract_research_plan(self, plan_text: str, default_sequence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract a structured research plan from the text response.
        
        This is a placeholder implementation. In a real system, this would use more 
        sophisticated parsing to extract structured data reliably.
        
        Args:
            plan_text: The raw plan text
            default_sequence: The default sequence to fall back on
            
        Returns:
            A structured research plan dictionary
        """
        # For simplicity, we'll just use the default sequence with any detected modifications
        # In a real implementation, this would parse the plan_text to extract a custom sequence
        
        # Simple checks for modifications to the default plan
        sequence = default_sequence.copy()
        
        # Check if any steps should be removed
        if 'skip proximity evaluation' in plan_text.lower() or 'omit proximity' in plan_text.lower():
            sequence = [step for step in sequence if step['agent'] != 'Proximity']
        
        # Check if iterations should be adjusted for Evolution
        for step in sequence:
            if step['agent'] == 'Evolution':
                if 'additional iterations' in plan_text.lower() or 'more iterations' in plan_text.lower():
                    step['params']['iterations'] += 1
                elif 'fewer iterations' in plan_text.lower() or 'reduce iterations' in plan_text.lower():
                    step['params']['iterations'] = max(1, step['params']['iterations'] - 1)
        
        return {
            'steps': sequence,
            'reasoning': plan_text[:500],  # Store part of the reasoning
            'status': 'planned'
        }
    
    def _extract_updated_plan(self, update_text: str, current_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Extract an updated research plan from the text response.
        
        This is a placeholder implementation. In a real system, this would use more 
        sophisticated parsing to extract structured data reliably.
        
        Args:
            update_text: The raw update text
            current_plan: The current plan to update
            
        Returns:
            The updated research plan dictionary
        """
        # For simplicity, we'll just look for simple update indicators
        # In a real implementation, this would parse the update_text to extract specific changes
        
        updated_plan = current_plan.copy()
        updated_plan['update_notes'] = update_text[:500]  # Store part of the update reasoning
        
        # Check for step additions or removals (simplified implementation)
        if 'add step' in update_text.lower() or 'additional step' in update_text.lower():
            updated_plan['steps'].append({"agent": "MetaReview", "task": "create_executive_summary", "params": {}})
        
        if 'remove step' in update_text.lower() or 'skip step' in update_text.lower():
            # For simplicity, just remove the last step that hasn't been executed yet
            executed_count = len(current_plan.get('executed_steps', []))
            if executed_count < len(updated_plan['steps']):
                updated_plan['steps'].pop(-1)
        
        return updated_plan
    
    def _get_timestamp(self) -> str:
        """Get a formatted timestamp.
        
        Returns:
            A formatted timestamp string
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
