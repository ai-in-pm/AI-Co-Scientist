# Configuration settings for the AI Co-Scientist system

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Agent Configuration
AGENT_DEFAULT_TEMPERATURE = 0.2
AGENT_DEFAULT_MODEL = os.getenv("MODEL_NAME", "gpt-3.5-turbo")  # Default to a well-known model if not specified

# System Configuration
MAX_ITERATIONS = 5
MAX_TOKENS = 4000

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_TO_FILE = True
LOG_FILE = "ai_coscientist.log"

# Database Configuration for results
DATABASE_PATH = "results_db.sqlite"

# Web search configuration
WEB_SEARCH_ENABLED = True
MAX_SEARCH_RESULTS = 5

# Tool integrations
TOOL_TIMEOUT = 30  # seconds
