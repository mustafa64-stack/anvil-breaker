@echo off
TITLE Anvil Breaker - GitHub & Render Deployer
echo ============================================================
echo   ANVIL BREAKER [TM] - 1-CLICK DEPLOYMENT ENGINE
echo   Author: Mustafa Marjani ^<founder@anvilbreaker.dev^>
echo ============================================================
echo.

IF "%~1"=="" (
    echo Usage: deploy_to_github.bat ^<GITHUB_REPO_OR_TOKEN_URL^>
    echo.
    echo Example 1 (Standard):
    echo   deploy_to_github.bat https://github.com/mustafa64-stack/anvil-breaker.git
    echo.
    echo Example 2 (With GitHub Personal Access Token):
    echo   deploy_to_github.bat https://ghp_YOUR_TOKEN@github.com/mustafa64-stack/anvil-breaker.git
    echo.
    set /p REPO_URL="Enter your GitHub Repository URL or PAT URL: "
) ELSE (
    set REPO_URL=%~1
)

IF "%REPO_URL%"=="" (
    echo [ERROR] No URL provided. Aborting.
    pause
    exit /b 1
)

python push_to_git.py "%REPO_URL%"

echo.
echo ============================================================
echo   NEXT STEP: LAUNCH ON RENDER.COM
echo ============================================================
echo   1. Open: https://render.com/deploy?repo=https://github.com/mustafa64-stack/anvil-breaker
echo   2. Click "Apply" to build and launch!
echo   3. Your live link will be: https://anvil-breaker.onrender.com
echo ============================================================
pause
