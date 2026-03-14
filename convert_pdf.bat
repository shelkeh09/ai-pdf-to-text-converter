@echo off
setlocal

set "PYTHON_EXE=C:\Users\shelk\AppData\Local\Python\pythoncore-3.14-64\python.exe"

if not exist "%PYTHON_EXE%" (
    echo Python was not found at:
    echo %PYTHON_EXE%
    echo.
    pause
    exit /b 1
)

if "%~1"=="" (
    set /p PDF_PATH=Enter the full path of your PDF file: 
) else (
    set "PDF_PATH=%~1"
)

if not exist "%PDF_PATH%" (
    echo.
    echo File not found:
    echo %PDF_PATH%
    echo.
    pause
    exit /b 1
)

echo.
echo Converting PDF to TXT...
echo.
"%PYTHON_EXE%" -m pdf_to_txt_converter "%PDF_PATH%" --page-markers

echo.
echo Finished. The TXT file was created next to your PDF.
echo.
pause
