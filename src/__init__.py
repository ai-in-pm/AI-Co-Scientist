# AI Co-Scientist package initialization

__version__ = "0.1.0"
__author__ = "AI Co-Scientist Team"

# Import AICoScientist class after all dependencies are loaded
from .main import AICoScientist as _AICoScientist

# Export AICoScientist
AICoScientist = _AICoScientist

__all__ = ['AICoScientist']
