@echo off
echo Starting AI Co-Scientist UI...

:: Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
) else (
    echo No virtual environment found. Proceeding with system Python.
)

:: Run the Streamlit app
streamlit run run_ui.py

:: Deactivate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\deactivate.bat
)

pause
