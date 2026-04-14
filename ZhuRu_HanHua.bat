@echo off
:: ========================================================
:: Antigravity Agent Manager HanHua Tool V5.1
:: ========================================================
title Antigravity HanHua Tool

echo.
echo [1/3] Detecting Antigravity process...
taskkill /f /im Antigravity.exe /t >nul 2>nul
timeout /t 2 /nobreak >nul

echo.
echo [2/3] Injecting Localization Core...
python "%~dp0AntigravityHanHua_GongJu.py" %*

echo.
echo [3/3] Injection Complete!
echo.
echo [Note] Please manually restart Antigravity.
echo.
pause
