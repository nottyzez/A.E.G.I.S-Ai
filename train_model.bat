@echo off
title HydroSync - AI Multimodal Ensemble Training
cd /d "%~dp0"
echo ============================================================================
echo   [HydroSync] Starting AI Multimodal Ensemble Training...
echo ============================================================================
echo.
"%~dp0ai-env312\Scripts\python.exe" "%~dp0update_and_retrain.py" --train
echo.
echo ============================================================================
echo   [HydroSync] Training Finished! Models and reports updated.
echo ============================================================================
pause
