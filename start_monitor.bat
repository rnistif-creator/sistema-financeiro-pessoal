@echo off
echo ==================================================
echo   Sistema Financeiro - Servidor com Auto-Restart
echo ==================================================
echo.

set PORT=8001
set CHECK_INTERVAL=20

:START
echo [%TIME%] Iniciando servidor...

REM Matar processos existentes na porta
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%PORT%') do (
    taskkill /F /PID %%a 2>nul
)

timeout /t 2 /nobreak >nul

REM Iniciar servidor em background
start /B "" ".venv\Scripts\python.exe" -m uvicorn app.main:app --reload --port %PORT%

echo [%TIME%] Servidor iniciado na porta %PORT%
echo [%TIME%] URL: http://localhost:%PORT%
echo.

:MONITOR
timeout /t %CHECK_INTERVAL% /nobreak >nul

REM Verificar se o servidor está respondendo
curl -s http://localhost:%PORT%/health >nul 2>&1

if errorlevel 1 (
    echo [%TIME%] ERRO: Servidor nao responde! Reiniciando...
    echo.
    
    REM Matar processos Python
    taskkill /F /IM python.exe 2>nul
    timeout /t 2 /nobreak >nul
    
    goto START
) else (
    echo [%TIME%] Servidor OK
    goto MONITOR
)
