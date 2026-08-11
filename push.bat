@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo   Master-thesis  ^>^>  GitHub
echo ==========================================
echo.

echo [0/4] Checking git...
set "GIT="
where git >nul 2>&1
if not errorlevel 1 (
    set "GIT=git"
    goto GITOK
)
if exist "%ProgramFiles%\Git\cmd\git.exe"       set "GIT=%ProgramFiles%\Git\cmd\git.exe"
if exist "%ProgramFiles(x86)%\Git\cmd\git.exe"  set "GIT=%ProgramFiles(x86)%\Git\cmd\git.exe"
if exist "%LocalAppData%\Programs\Git\cmd\git.exe" set "GIT=%LocalAppData%\Programs\Git\cmd\git.exe"
if exist "C:\Git\cmd\git.exe"                   set "GIT=C:\Git\cmd\git.exe"
if not defined GIT goto NOGIT
echo   Found git outside PATH: %GIT%
:GITOK
"%GIT%" --version
echo.

echo [1/4] Cleaning stale lock files...
if exist ".git\HEAD.lock"               del /f /q ".git\HEAD.lock"
if exist ".git\index.lock"              del /f /q ".git\index.lock"
if exist ".git\config.lock"             del /f /q ".git\config.lock"
if exist ".git\objects\maintenance.lock" del /f /q ".git\objects\maintenance.lock"
for /r ".git\objects" %%f in (tmp_obj_*) do del /f /q "%%f" 2>nul
for /r ".git\refs" %%f in (*.lock) do del /f /q "%%f" 2>nul
echo   done.
echo.

echo [2/4] Registering repo as safe...
"%GIT%" config --global --add safe.directory "%CD:\=/%"
"%GIT%" config --global --add safe.directory "%CD%"
echo   done.
echo.

echo [3/4] Repo status
"%GIT%" status --short
echo.
"%GIT%" log --oneline -1
echo.

echo [4/4] Commit and push
"%GIT%" add -A
"%GIT%" diff --cached --quiet
if errorlevel 1 goto DOCOMMIT
echo   Nothing new to commit.
goto DOPUSH

:DOCOMMIT
set "MSG="
set /p "MSG=Commit message (Enter = default): "
if not defined MSG set "MSG=work session checkpoint"
"%GIT%" commit -m "%MSG%"
echo.

:DOPUSH
"%GIT%" push -u origin main
if errorlevel 1 goto PUSHFAIL
echo.
echo   SUCCESS  ^>^>  https://github.com/sapzzil/Master-thesis
goto END

:PUSHFAIL
echo.
echo   PUSH FAILED - see the git message above.
echo   Common causes:
echo     1. Repo not created yet  -^> https://github.com/new  name: Master-thesis  (no README)
echo     2. Login window appeared -^> sign in, then run this again
echo     3. Auth rejected         -^> need a Personal Access Token
goto END

:NOGIT
echo.
echo   ERROR: Git is not installed on this PC.
echo   Download: https://git-scm.com/download/win
echo   Install with default options, then run this file again.
goto END

:END
echo.
pause
