@echo off
setlocal

:: 2. Tên nhánh Git (thường là main hoặc master)
set "GIT_BRANCH=main"

:: 3. Nội dung commit tự động
set "COMMIT_MSG=Auto deploy update"

echo ==========================================
echo 3. DANG DAY CODE LEN GIT (FORCE PUSH)...
echo ==========================================
:: Thêm tất cả file
git add .

:: Commit với thời gian hiện tại
git commit -m "%COMMIT_MSG% - %date% %time%"

:: Force Push lên nhánh chính
git push origin %GIT_BRANCH% --force
if errorlevel 1 (
    echo [LOI] Git Push that bai! Kiem tra lai mang hoac quyen truy cap.
    pause
    exit /b 1
)
pause