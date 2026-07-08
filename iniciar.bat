@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo    Corretor de Redacao ENEM
echo.
echo    Abra no navegador:  http://localhost:3005
echo    Para PARAR: feche esta janela
echo ============================================
echo.
call npm start
echo.
echo O servidor parou. Se houve erro, ele aparece acima.
pause
