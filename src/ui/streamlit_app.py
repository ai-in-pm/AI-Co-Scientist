# Streamlit UI for AI Co-Scientist

import os
import sys
import json
import time
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add the project root to the system path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import directly from the main module to avoid circular imports
from src.main import AICoScientist
from src.config.config import AGENT_DEFAULT_MODEL, AGENT_DEFAULT_TEMPERATURE


def display_hypothesis_table(hypotheses: List[Dict[str, Any]]):
    """Display a table of hypotheses with scores and other metadata."""
    if not hypotheses:
        st.info("No hypotheses available.")
        return
    
    # Extract relevant fields
    data = []
    for i, h in enumerate(hypotheses):
        data.append({
            "Rank": i + 1,
            "Hypothesis": h["hypothesis"],
            "Score": h.get("score", "N/A"),
            "Confidence": h.get("confidence", "N/A"),
            "Novelty": h.get("novelty_score", "N/A"),
            "Iteration": h.get("iteration", "N/A")
        })
    
    # Create and display DataFrame
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)


def plot_hypothesis_scores(hypotheses: List[Dict[str, Any]]):
    """Plot scores of hypotheses as a bar chart."""
    if not hypotheses or len(hypotheses) < 2:
        return
    
    # Extract scores
    labels = [f"H{i+1}" for i in range(len(hypotheses))]
    scores = [h.get("score", 0) for h in hypotheses]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(labels, scores, color='skyblue')
    
    # Add labels and title
    ax.set_xlabel('Hypotheses')
    ax.set_ylabel('Score')
    ax.set_title('Hypothesis Ranking Scores')
    
    # Add score values on top of bars
    for bar, score in zip(bars, scores):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height,
                f'{score:.2f}', ha='center', va='bottom')
    
    # Display plot
    st.pyplot(fig)


def run_app():
    """Run the Streamlit application."""
    st.set_page_config(
        page_title="AI Co-Scientist",
        page_icon="🧬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🧬 AI Co-Scientist")
    st.subheader("Multi-Agent Scientific Research Framework")
    
    # Sidebar configuration
    st.sidebar.header("Configuration")
    
    model = st.sidebar.selectbox(
        "LLM Model",
        options=[
            "gpt-4o",
            "gpt-4o-mini", 
            "gpt-4-turbo", 
            "gpt-4", 
            "gpt-3.5-turbo", 
            "gpt-3.5-turbo-16k"
        ],
        index=0,
        help="Select the OpenAI model to use. More powerful models provide better results but may be more expensive."
    )
    
    temperature = st.sidebar.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=AGENT_DEFAULT_TEMPERATURE,
        step=0.1,
        help="Higher values (closer to 1) make output more random, while lower values make it more deterministic."
    )
    
    iterations = st.sidebar.slider(
        "Refinement Iterations",
        min_value=1,
        max_value=5,
        value=3,
        step=1
    )
    
    # Initialize state
    if "acs" not in st.session_state:
        st.session_state.acs = None
    
    if "results" not in st.session_state:
        st.session_state.results = None
    
    if "progress" not in st.session_state:
        st.session_state.progress = 0
    
    if "status" not in st.session_state:
        st.session_state.status = ""
    
    # Input section
    st.header("Research Goal")
    research_goal = st.text_area(
        "Enter your research goal:",
        value="To investigate the relationship between microbiome diversity and autoimmune disorders in urban populations",
        height=100
    )
    
    col1, col2 = st.columns([1, 3])
    
    # Run button
    if col1.button("Generate Hypotheses", type="primary", use_container_width=True):
        # Initialize AI Co-Scientist
        config = {
            "model": model if model else "gpt-3.5-turbo",  # Ensure we never pass None as the model
            "temperature": temperature,
            "max_iterations": iterations
        }
        
        st.session_state.acs = AICoScientist(config=config)
        st.session_state.results = None
        st.session_state.progress = 0
        st.session_state.status = "initializing"
        
        # Run in chunks with progress bar
        progress_bar = st.progress(0, "Initializing...")
        
        try:
            # 1. Set research goal and update progress
            st.session_state.status = "setting_goal"
            progress_bar.progress(10, "Setting research goal...")
            st.session_state.acs.set_research_goal(research_goal)
            st.session_state.progress = 10
            
            # 2. Generate hypotheses
            st.session_state.status = "generating"
            progress_bar.progress(25, "Generating initial hypotheses...")
            hypotheses = st.session_state.acs.generate_hypotheses(count=7)
            st.session_state.progress = 25
            
            # 3. Rank hypotheses
            st.session_state.status = "ranking"
            progress_bar.progress(40, "Ranking hypotheses...")
            ranked = st.session_state.acs.rank_hypotheses()
            st.session_state.progress = 40
            
            # 4. Refine hypotheses with progress updates per iteration
            st.session_state.status = "refining"
            progress_per_iteration = 30 / iterations  # 30% of progress bar for refinement
            
            for i in range(iterations):
                progress_value = 40 + ((i + 1) * progress_per_iteration)
                progress_bar.progress(int(progress_value), f"Refining hypotheses (iteration {i+1}/{iterations})...")
                if i == iterations - 1:
                    refined = st.session_state.acs.refine_hypotheses(iterations=1)
                time.sleep(0.5)  # Simulate processing time
                st.session_state.progress = progress_value
            
            # 5. Generate report
            st.session_state.status = "reporting"
            progress_bar.progress(80, "Generating research report...")
            report = st.session_state.acs.generate_research_report()
            st.session_state.progress = 80
            
            # 6. Store results
            st.session_state.results = {
                "research_goal": research_goal,
                "hypotheses": ranked,
                "report": report
            }
            st.session_state.status = "completed"
            progress_bar.progress(100, "Research workflow completed!")
            st.session_state.progress = 100
            
            # Trigger rerun to update UI
            st.rerun()
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.session_state.status = "error"
            progress_bar.progress(100, "Error occurred!")
    
    # Reset button
    if col2.button("Reset", use_container_width=True):
        st.session_state.acs = None
        st.session_state.results = None
        st.session_state.progress = 0
        st.session_state.status = ""
        st.rerun()
    
    # Display results if available
    if st.session_state.results is not None:
        # Results tabs
        tab1, tab2, tab3 = st.tabs(["Top Hypotheses", "Report", "All Hypotheses"])
        
        with tab1:
            st.header("Top Hypotheses")
            top_hypotheses = st.session_state.results["hypotheses"][:3] if st.session_state.results["hypotheses"] else []
            
            if top_hypotheses:
                for i, h in enumerate(top_hypotheses):
                    with st.expander(f"Hypothesis {i+1}: Score {h.get('score', 'N/A')}", expanded=i==0):
                        st.markdown(f"""**Hypothesis**: {h['hypothesis']}""")
                        
                        if "feedback" in h:
                            st.markdown("**Feedback**:")
                            st.markdown(h["feedback"]["critique"])
                        
                        cols = st.columns(4)
                        cols[0].metric("Score", f"{h.get('score', 'N/A')}")
                        cols[1].metric("Novelty", f"{h.get('novelty_score', 'N/A')}")
                        cols[2].metric("Testability", f"{h.get('testability', 'N/A')}")
                        cols[3].metric("Proximity", f"{h.get('proximity', {}).get('proximity_score', 'N/A')}")
                
                # Plot scores
                st.subheader("Hypothesis Scores")
                plot_hypothesis_scores(st.session_state.results["hypotheses"])
            else:
                st.info("No hypotheses available.")
        
        with tab2:
            st.header("Research Report")
            
            if "report" in st.session_state.results and st.session_state.results["report"]:
                report = st.session_state.results["report"]
                
                st.subheader("Executive Summary")
                st.markdown(report.get("executive_summary", "No summary available."))
                
                st.subheader("Key Findings")
                for i, finding in enumerate(report.get("key_findings", [])):
                    st.markdown(f"**{i+1}.** {finding}")
                
                st.subheader("Future Directions")
                for i, direction in enumerate(report.get("future_directions", [])):
                    st.markdown(f"**{i+1}.** {direction}")
                
                if "limitations" in report:
                    st.subheader("Limitations")
                    st.markdown(report["limitations"])
            else:
                st.info("No report available.")
        
        with tab3:
            st.header("All Hypotheses")
            all_hypotheses = st.session_state.results["hypotheses"] if st.session_state.results["hypotheses"] else []
            display_hypothesis_table(all_hypotheses)
    
    # Display system status if in progress
    elif st.session_state.status and st.session_state.status != "completed" and st.session_state.status != "error":
        st.info(f"Status: {st.session_state.status} (Progress: {st.session_state.progress}%)")
        
        # Show placeholder content
        st.header("Generating Research Results...")
        st.markdown("""The AI Co-Scientist system is analyzing your research goal and generating hypotheses. This process involves:
        
        1. **Generation**: Creating diverse initial hypotheses
        2. **Ranking**: Evaluating and ranking hypotheses by quality
        3. **Refinement**: Iteratively improving promising hypotheses
        4. **Reporting**: Synthesizing findings into a comprehensive report
        
        Please wait while the system completes this process.""")
    else:
        # Instructions for first-time users
        st.info("Enter your research goal and click 'Generate Hypotheses' to start the research workflow.")
        
        # Sample research goals to help users get started
        with st.expander("Sample Research Goals"):
            st.markdown("""Click on any sample to use it:
            
            - To investigate the impact of intermittent fasting on cognitive performance in healthy adults
            - To examine the relationship between urban green space exposure and mental health outcomes
            - To explore the effectiveness of different machine learning algorithms in predicting stock market trends
            - To analyze the effects of microplastics on marine ecosystem biodiversity
            - To determine how social media usage patterns correlate with adolescent depression rates
            """)
            
            if st.button("Use Sample", key="sample_button"):
                # This would typically set the textarea value, but Streamlit doesn't allow direct manipulation
                # Instead, we rely on the default value in the text_area
                pass
    
    # Footer
    st.markdown("---")
    st.markdown("AI Co-Scientist: Multi-Agent Scientific Research Framework | v0.1.0")


if __name__ == "__main__":
    run_app()
