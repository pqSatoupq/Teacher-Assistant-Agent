@echo off
echo ==============================================
echo       Starting Teacher Assistant Agent
echo ==============================================
echo.
echo Installing requirements (if not already installed)...
pip install -r requirements.txt
echo.
echo Launching the application in your browser...
streamlit run app.py
pause
