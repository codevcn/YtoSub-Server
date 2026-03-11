@echo off
setlocal

REM ============================================================
REM Upload all .env files to Ubuntu VPS
REM ============================================================

REM Tối ưu 1: Sử dụng cú pháp set "TÊN=GIÁ_TRỊ" để ngăn chặn lỗi khoảng trắng thừa ở cuối dòng
set "SSH_KEY=D:\D-Documents\Credentials\ytosub\gcp-deploy-user"
set "VPS_USER=deploy"
set "VPS_HOST=34.124.219.246"
set "VPS_TARGET=/var/www/ytosub/shared/"

echo ============================================================
echo [i-upload] Uploading .env files to VPS
echo ============================================================
echo.
echo Target: %VPS_USER%@%VPS_HOST%:%VPS_TARGET%
echo SSH Key: %SSH_KEY%
echo.

REM Kiểm tra xem có tệp tin .env nào không
if not exist "*.env" (
    echo [WARNING] No .env files found in current directory.
    echo Please create .env files first, then run this script again.
    pause
    exit /b 1
)

echo [1/2] Found .env files:
dir /b *.env
echo.

echo [2/2] Uploading via scp...
REM Tải lên từng tệp đích danh để tránh lỗi wildcard của Windows
scp -i "%SSH_KEY%" .env "%VPS_USER%@%VPS_HOST%:%VPS_TARGET%"
scp -i "%SSH_KEY%" .gemini_key.env "%VPS_USER%@%VPS_HOST%:%VPS_TARGET%"
scp -i "%SSH_KEY%" deploy-data.env "%VPS_USER%@%VPS_HOST%:%VPS_TARGET%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo ✅ [SUCCESS] All .env files uploaded successfully!
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo ❌ [ERROR] Upload failed. Check SSH key, network connection, or folder permissions.
    echo ============================================================
    pause
    exit /b 1
)

endlocal
pause