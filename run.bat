@echo off
echo Starting Student Study Assistant...

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)

echo.
echo IMPORTANT: Make sure you have added your OPENAI_API_KEY to the .env file!
echo.

start "" "frontend\index.html"
echo Starting Backend Server...
uvicorn backend.main:app --reload
