# Validator functions for hypothesis and research goals

import re
from typing import Dict, List, Tuple, Union, Optional

def validate_hypothesis(hypothesis: str) -> Tuple[bool, List[str]]:
    """Validate a scientific hypothesis for basic quality criteria.
    
    Args:
        hypothesis: The hypothesis text to validate
        
    Returns:
        A tuple containing (is_valid, list_of_issues)
    """
    issues = []
    
    # Check for minimum length
    if len(hypothesis) < 10:
        issues.append("Hypothesis is too short")
    
    # Check for maximum length
    if len(hypothesis) > 1000:
        issues.append("Hypothesis is too long (>1000 characters)")
    
    # Check if it's a statement, not a question
    if hypothesis.strip().endswith("?"):
        issues.append("Hypothesis should be a statement, not a question")
    
    # Check for testability indicators
    testability_terms = ["increase", "decrease", "affect", "change", "cause", 
                        "lead to", "result in", "correlate", "association", 
                        "relationship"]
                        
    has_testability_term = any(term in hypothesis.lower() for term in testability_terms)
    if not has_testability_term:
        issues.append("Hypothesis may not be testable - consider including terms that describe relationships, effects, or changes")
    
    # Check for vague terms
    vague_terms = ["very", "extremely", "many", "most", "few", "several", "a lot", 
                  "better", "worse", "good", "bad", "significant"]
                  
    found_vague_terms = [term for term in vague_terms if f" {term} " in f" {hypothesis.lower()} "]
    if found_vague_terms:
        issues.append(f"Hypothesis contains vague terms: {', '.join(found_vague_terms)}")
    
    # Check if it appears to have variables/factors to test
    if not re.search(r"\b(if|when|as|while)\b", hypothesis.lower()) and \
       not re.search(r"\b(causes|affects|influences|impacts|changes|increases|decreases)\b", hypothesis.lower()):
        issues.append("Hypothesis may not clearly specify variables or relationships to test")
    
    # Determine overall validity
    is_valid = len(issues) <= 1  # Allow one minor issue
    
    return is_valid, issues

def validate_research_goal(goal: str) -> Tuple[bool, List[str]]:
    """Validate a research goal for basic quality criteria.
    
    Args:
        goal: The research goal text to validate
        
    Returns:
        A tuple containing (is_valid, list_of_issues)
    """
    issues = []
    
    # Check for minimum length
    if len(goal) < 10:
        issues.append("Research goal is too short")
    
    # Check for maximum length
    if len(goal) > 500:
        issues.append("Research goal is too long (>500 characters)")
    
    # Check if it starts with an appropriate verb
    appropriate_starts = ["to ", "the goal is to ", "this research aims to ", 
                         "we aim to ", "this study seeks to ", "the purpose is to "]
                         
    has_appropriate_start = any(goal.lower().startswith(start) for start in appropriate_starts)
    if not has_appropriate_start:
        issues.append("Research goal should typically start with 'To...' or similar phrase")
    
    # Check for specific research action verbs
    research_verbs = ["investigate", "explore", "analyze", "determine", "identify", 
                     "examine", "understand", "evaluate", "assess", "develop", 
                     "discover", "explain", "test", "validate", "characterize"]
                     
    has_research_verb = any(f" {verb} " in f" {goal.lower()} " for verb in research_verbs)
    if not has_research_verb:
        issues.append("Research goal should include specific research action verbs")
    
    # Check if it's a question instead of a goal statement
    if goal.strip().endswith("?"):
        issues.append("Research goal should be a statement, not a question")
    
    # Determine overall validity
    is_valid = len(issues) <= 1  # Allow one minor issue
    
    return is_valid, issues
