@echo off
setlocal
cd /d "%~dp0"

echo ===========================================
echo    EIA Q2 ULTIMATE SYNC TOOL (EIAQ3 AUTO)
echo ===========================================

:: [1/4] Run Data Extraction
echo [1/4] Extracting Data from Local Excel...
python update_dashboard.py

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Data Extraction Failed.
    exit /b 1
)

echo Generating Static Team Detailed Tables...
python gen_tables.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Table Generation Failed.
    exit /b 1
)

echo Injecting Tables into Root Dashboard...
cd ..
python sync.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Sync Failed.
    exit /b 1
)
cd EIAQ3

:: [2/4] Mirror to Root for Deployment
echo [2/4] Mirroring UI to Project Root...
if not exist "..\assets" mkdir "..\assets"
xcopy /S /Y /I "assets" "..\assets"
copy /Y "data.js" "..\data.js"

:: [3/4] Selective Git Update
echo [3/4] Staging Approved Dashboard Files...
cd ..
git add index.html
git add data.js
git add assets/
git add EIAQ3/update_dashboard.py
git add EIAQ3/run_sync.bat
git add EIAQ3/run_sync_auto.bat
git add .gitignore

:: [4/4] Commit and Push
echo [4/4] Pushing to GitHub...
git commit -m "Auto Sync: UI & Data Update"
git push origin main

echo ===========================================
echo    DASHBOARD UPDATED SUCCESSFULLY!
echo ===========================================
cd EIAQ3
exit /b 0
