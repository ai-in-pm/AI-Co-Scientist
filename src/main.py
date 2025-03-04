# Main application entry point for AI Co-Scientist

import os
import argparse
import logging
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from .agents.agent_factory import AgentFactory
from .tools.search_tool import SearchTool
from .tools.reasoning_tool import ReasoningTool
from .tools.citation_tool import CitationTool
from .utils.logger import setup_logging
from .utils.validators import validate_research_goal, validate_hypothesis
from .utils.exceptions import ConfigError, ValidationError

from .config.config import (
    AGENT_DEFAULT_MODEL,
    AGENT_DEFAULT_TEMPERATURE,
    LOG_LEVEL,
    LOG_TO_FILE,
    MAX_ITERATIONS,
    MAX_TOKENS
)

class AICoScientist:
    """Main class for the AI Co-Scientist system.
    
    This class coordinates the multi-agent scientific research workflow,
    managing the interactions between different specialized agents to generate
    and refine scientific hypotheses.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the AI Co-Scientist system.
        
        Args:
            config: Optional configuration dictionary to override defaults
        """
        # Initialize logger
        self.logger = setup_logging(log_level=LOG_LEVEL, log_to_file=LOG_TO_FILE)
        self.logger.info("Initializing AI Co-Scientist system")
        
        # Load configuration
        self.config = {
            "model": AGENT_DEFAULT_MODEL,
            "temperature": AGENT_DEFAULT_TEMPERATURE,
            "max_iterations": MAX_ITERATIONS,
            "max_tokens": MAX_TOKENS,
        }
        
        # Override with provided config
        if config:
            # Ensure model is never None
            if config.get("model") is None:
                config["model"] = AGENT_DEFAULT_MODEL
                
            self.config.update(config)
            self.logger.info(f"Configuration overridden with custom values")
        
        self.logger.info(f"Using model: {self.config['model']}")
        
        # Initialize agent factory
        self.agent_factory = AgentFactory()
        
        # Initialize tools
        self.tools = {
            "search": SearchTool(),
            "reasoning": ReasoningTool(),
            "citation": CitationTool()
        }
        
        # Create supervisor agent
        self.supervisor = self.agent_factory.get_supervisor(
            model=self.config["model"],
            temperature=self.config["temperature"]
        )
        
        # Initialize research state
        self.research_goal = None
        self.hypotheses = []
        self.ranked_hypotheses = []
        self.final_report = None
    
    def set_research_goal(self, goal: str) -> bool:
        """Set the research goal for the system.
        
        Args:
            goal: The research goal to pursue
            
        Returns:
            True if the goal was successfully set, False otherwise
            
        Raises:
            ValidationError: If the goal is invalid
        """
        self.logger.info(f"Setting research goal: {goal}")
        
        # Validate the research goal
        is_valid, issues = validate_research_goal(goal)
        
        if not is_valid:
            error_msg = f"Invalid research goal: {', '.join(issues)}"
            self.logger.error(error_msg)
            raise ValidationError(error_msg)
        
        self.research_goal = goal
        self.logger.info(f"Research goal set successfully")
        return True
    
    def generate_hypotheses(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate scientific hypotheses based on the research goal.
        
        Args:
            count: Number of hypotheses to generate
            
        Returns:
            List of generated hypotheses with metadata
            
        Raises:
            ValueError: If research goal is not set
        """
        if not self.research_goal:
            raise ValueError("Research goal must be set before generating hypotheses")
        
        self.logger.info(f"Generating {count} hypotheses for research goal: {self.research_goal}")
        
        # Get generation agent
        generation_agent = self.agent_factory.get_agent(
            "generation",
            model=self.config["model"],
            temperature=self.config["temperature"] + 0.2  # Slightly higher temperature for creativity
        )
        
        # Generate hypotheses
        hypotheses = generation_agent.generate_hypotheses(self.research_goal, count=count)
        
        # Validate hypotheses
        valid_hypotheses = []
        for h in hypotheses:
            is_valid, issues = validate_hypothesis(h["hypothesis"])
            h["validation"] = {
                "is_valid": is_valid,
                "issues": issues
            }
            if is_valid:
                valid_hypotheses.append(h)
            else:
                self.logger.warning(f"Invalid hypothesis: {h['hypothesis']}\nIssues: {', '.join(issues)}")
        
        self.hypotheses = valid_hypotheses
        self.logger.info(f"Generated {len(valid_hypotheses)} valid hypotheses")
        
        return valid_hypotheses
    
    def rank_hypotheses(self) -> List[Dict[str, Any]]:
        """Rank the generated hypotheses by quality and relevance.
        
        Returns:
            List of ranked hypotheses with scores
            
        Raises:
            ValueError: If no hypotheses have been generated
        """
        if not self.hypotheses:
            raise ValueError("No hypotheses have been generated to rank")
        
        self.logger.info(f"Ranking {len(self.hypotheses)} hypotheses")
        
        # Get ranking agent
        ranking_agent = self.agent_factory.get_agent("ranking")
        
        # Rank hypotheses
        ranked_hypotheses = ranking_agent.rank_hypotheses(
            self.research_goal,
            self.hypotheses
        )
        
        self.ranked_hypotheses = ranked_hypotheses
        self.logger.info(f"Ranked {len(ranked_hypotheses)} hypotheses")
        
        return ranked_hypotheses
    
    def refine_hypotheses(self, iterations: int = 3) -> List[Dict[str, Any]]:
        """Refine the top hypotheses through multiple iterations.
        
        Args:
            iterations: Number of refinement iterations
            
        Returns:
            List of refined hypotheses
            
        Raises:
            ValueError: If no ranked hypotheses are available
        """
        if not self.ranked_hypotheses:
            raise ValueError("No ranked hypotheses are available for refinement")
        
        # Get top 3 hypotheses for refinement
        top_hypotheses = self.ranked_hypotheses[:3]
        self.logger.info(f"Refining top {len(top_hypotheses)} hypotheses through {iterations} iterations")
        
        # Get agents for refinement
        reflection_agent = self.agent_factory.get_agent("reflection")
        evolution_agent = self.agent_factory.get_agent("evolution")
        proximity_agent = self.agent_factory.get_agent("proximity")
        
        refined_hypotheses = top_hypotheses.copy()
        
        for i in range(iterations):
            self.logger.info(f"Refinement iteration {i+1}/{iterations}")
            
            for j, hypothesis in enumerate(refined_hypotheses):
                # Get feedback from reflection agent
                feedback = reflection_agent.review_hypothesis(
                    hypothesis["hypothesis"],
                    self.research_goal
                )
                
                # Evolve hypothesis based on feedback
                evolved = evolution_agent.evolve_hypothesis(
                    hypothesis["hypothesis"],
                    feedback,
                    self.research_goal
                )
                
                # Check proximity to research goal
                proximity_result = proximity_agent.evaluate_proximity(
                    evolved["hypothesis"],
                    self.research_goal
                )
                
                # Update hypothesis with refined version if it's relevant
                if proximity_result["proximity_score"] >= 0.7:  # Threshold for relevance
                    refined_hypotheses[j] = evolved
                    refined_hypotheses[j]["proximity"] = proximity_result
                    refined_hypotheses[j]["feedback"] = feedback
                    refined_hypotheses[j]["iteration"] = i + 1
                    self.logger.info(f"Refined hypothesis {j+1}: {evolved['hypothesis'][:100]}...")
                else:
                    self.logger.warning(f"Refined hypothesis {j+1} was too far from research goal (score: {proximity_result['proximity_score']})")
        
        # Update ranked hypotheses with refined versions
        for i, refined in enumerate(refined_hypotheses):
            self.ranked_hypotheses[i] = refined
        
        return refined_hypotheses
    
    def generate_research_report(self) -> Dict[str, Any]:
        """Generate a comprehensive research report with the findings.
        
        Returns:
            A dictionary containing the complete research report
            
        Raises:
            ValueError: If no hypotheses have been processed
        """
        if not self.ranked_hypotheses:
            raise ValueError("No hypotheses have been processed for report generation")
        
        self.logger.info("Generating comprehensive research report")
        
        # Get meta-review agent
        meta_review_agent = self.agent_factory.get_agent("metareview")
        
        # Generate report
        report = meta_review_agent.generate_report(
            self.research_goal,
            self.ranked_hypotheses,
            max_hypotheses=5  # Include top 5 hypotheses in report
        )
        
        self.final_report = report
        self.logger.info(f"Generated research report with {len(report['hypotheses'])} hypotheses")
        
        return report
    
    def save_results(self, output_dir: Optional[str] = None) -> str:
        """Save the research results to disk.
        
        Args:
            output_dir: Optional directory to save results. If None, saves to 'results'
                directory in the project root.
                
        Returns:
            Path to the saved results file
            
        Raises:
            ValueError: If no final report is available
        """
        if not self.final_report:
            raise ValueError("No final report available to save")
        
        # Import dependencies here to avoid circular imports
        import time
        from datetime import datetime
        
        # Determine output directory
        if output_dir is None:
            # Get the project root directory (assuming this file is in src/)
            project_root = Path(__file__).parent.parent  # Go up one level from this file
            output_dir = project_root / "results"
        else:
            output_dir = Path(output_dir)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Create results dictionary
        results = {
            "research_goal": self.research_goal,
            "configuration": self.config,
            "hypotheses": {
                "initial": self.hypotheses,
                "ranked": self.ranked_hypotheses
            },
            "final_report": self.final_report,
            "meta": {
                "model": self.config["model"],
                "timestamp": str(datetime.now().isoformat())
            }
        }
        
        # Save results to file
        results_file = output_dir / f"research_results_{time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        self.logger.info(f"Saved research results to {results_file}")
        return str(results_file)
    
    def run_full_workflow(self, research_goal: str, iterations: int = 3, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Run the complete research workflow from goal to final report.
        
        Args:
            research_goal: The research goal to pursue
            iterations: Number of refinement iterations
            output_dir: Optional directory to save results
            
        Returns:
            The complete research results dictionary
            
        Raises:
            ValidationError: If research goal is invalid
        """
        self.logger.info(f"Starting full research workflow for goal: {research_goal}")
        
        try:
            # Set research goal
            self.set_research_goal(research_goal)
            
            # Generate hypotheses
            self.generate_hypotheses(count=7)  # Generate 7 initial hypotheses
            
            # Rank hypotheses
            self.rank_hypotheses()
            
            # Refine hypotheses
            self.refine_hypotheses(iterations=iterations)
            
            # Generate report
            self.generate_research_report()
            
            # Save results if output directory is specified
            if output_dir:
                self.save_results(output_dir)
            
            self.logger.info("Research workflow completed successfully")
            
            # Return final results
            return {
                "research_goal": self.research_goal,
                "hypotheses": self.ranked_hypotheses,
                "report": self.final_report
            }
            
        except Exception as e:
            self.logger.error(f"Error in research workflow: {str(e)}")
            raise


def main():
    """Main entry point for the AI Co-Scientist application."""
    # For imports that may cause circular dependencies, import here
    import time
    from datetime import datetime
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="AI Co-Scientist: Multi-agent system for scientific hypothesis generation")
    parser.add_argument("--goal", "-g", type=str, help="Research goal to pursue")
    parser.add_argument("--model", "-m", type=str, default=AGENT_DEFAULT_MODEL, help="LLM model to use")
    parser.add_argument("--temp", "-t", type=float, default=AGENT_DEFAULT_TEMPERATURE, help="Temperature for LLM generation")
    parser.add_argument("--iterations", "-i", type=int, default=3, help="Number of refinement iterations")
    parser.add_argument("--output", "-o", type=str, help="Output directory for results")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging level
    log_level = "DEBUG" if args.verbose else LOG_LEVEL
    logger = setup_logging(log_level=log_level, log_to_file=LOG_TO_FILE)
    
    # Initialize configuration
    config = {
        "model": args.model,
        "temperature": args.temp,
        "max_iterations": MAX_ITERATIONS,
        "max_tokens": MAX_TOKENS
    }
    
    # Initialize AI Co-Scientist
    acs = AICoScientist(config=config)
    
    # Run workflow if goal is provided
    if args.goal:
        try:
            results = acs.run_full_workflow(
                research_goal=args.goal,
                iterations=args.iterations,
                output_dir=args.output
            )
            
            # Print summary results
            print("\n" + "=" * 80)
            print(f"RESEARCH GOAL: {args.goal}")
            print("=" * 80)
            print("\nTOP HYPOTHESES:")
            for i, h in enumerate(results["hypotheses"][:3]):
                print(f"\n{i+1}. {h['hypothesis']}")
                print(f"   Score: {h.get('score', 'N/A')}")
            
            print("\n" + "=" * 80)
            print("EXECUTIVE SUMMARY:")
            print(results["report"]["executive_summary"])
            print("=" * 80 + "\n")
            
            # Print path to full results if saved
            if args.output:
                print(f"Complete results saved to: {args.output}")
                
        except Exception as e:
            logger.error(f"Error in workflow execution: {str(e)}")
            print(f"\nError: {str(e)}")
            return 1
    else:
        parser.print_help()
    
    return 0


if __name__ == "__main__":
    main()
