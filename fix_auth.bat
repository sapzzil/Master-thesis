@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo   GitHub Authentication Reset
echo ==========================================
echo.

set "GIT="
where git >nul 2>&1
if not errorlevel 1 set "GIT=git"
if not defined GIT if exist "%ProgramFiles%\Git\cmd\git.exe" set "GIT=%ProgramFiles%\Git\cmd\git.exe"
if not defined GIT (
    echo   ERROR: git not found.
    goto END
)

echo [1/3] Removing cached GitHub credentials...
cmdkey /delete:git:https://github.com  >nul 2>&1
cmdkey /delete:LegacyGeneric:target=git:https://github.com >nul 2>&1
echo   done.
echo.

echo [2/3] Enabling Git Credential Manager (browser login)...
"%GIT%" config --global credential.helper manager
"%GIT%" config --global credential.https://github.com.provider github
echo   done.
echo.

echo [3/3] Pushing - a BROWSER WINDOW should open. Sign in there.
echo.
"%GIT%" push -u origin main
if errorlevel 1 goto FAILED

echo.
echo   SUCCESS  ^>^>  https://github.com/sapzzil/Master-thesis
goto END

:FAILED
echo.
echo   Still failing. Use a Personal Access Token instead:
echo.
echo     1. Open  https://github.com/settings/tokens
echo     2. Generate new token (classic)
echo     3. Check the "repo" scope, then generate and COPY the token
echo     4. Run push.bat again
echo        Username: sapzzil
echo        Password: paste the token (not your GitHub password)
echo.

:END
echo.
pause
