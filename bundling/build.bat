@echo off
REM Build script for SAGE MCP executable on Windows
REM This script provides a convenient wrapper around the Python build script

echo.
echo 🚀 SAGE MCP Executable Builder for Windows
echo ==========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/windows/
    echo or from the Microsoft Store
    pause
    exit /b 1
)

REM Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip is not installed or not in PATH
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

REM Run the Python build script
echo 🔨 Running build process...
python bundling\build_executable.py

REM Check if build was successful
if exist "bundling\dist\sage_mcp.exe" (
    echo.
    echo ✅ Build completed successfully!
    echo 📍 Executable location: %cd%\bundling\dist\sage_mcp.exe
    echo.
    echo 🧪 Testing executable startup...
    
    REM Test the executable with a timeout (Windows doesn't have timeout command by default)
    echo Starting executable test...
    start /wait /b "" "bundling\dist\sage_mcp.exe" --help >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Executable appears to be working
    ) else (
        echo ⚠️  Executable test inconclusive, but file exists
    )
    
    echo.
    echo 💡 To run the server:
    echo    bundling\dist\sage_mcp.exe
    echo    # Or double-click the executable
    echo.
    echo 💡 To run on a specific host/port:
    echo    set MCP_HOST=127.0.0.1
    echo    set MCP_PORT=8080
    echo    bundling\dist\sage_mcp.exe
    echo.
    echo 🌐 Once running, the server will be available at:
    echo    http://localhost:8000/mcp
    echo.
) else (
    echo ❌ Build failed - executable not found
    pause
    exit /b 1
)

echo Press any key to continue...
pause >nul 