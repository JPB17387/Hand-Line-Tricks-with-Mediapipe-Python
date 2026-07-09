@echo off
REM Hand Tricks - Launch Script for Windows Command Prompt
REM This script activates the virtual environment and runs the application

cd /d "%~dp0"

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Starting Hand Tricks...
echo.

python main.py

pause
