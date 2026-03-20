@echo off
echo ===================================================
echo   Build de Pyflight 2D pour Windows (.exe)
echo ===================================================

:: Vérification de Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python n'est pas installe ou n'est pas dans le PATH.
    pause
    exit /b
)

:: Création de l'environnement virtuel
echo Creation de l'environnement virtuel (venv)...
python -m venv venv_win

:: Activation et installation
echo Installation des dependances...
call venv_win\Scripts\activate.bat
pip install --upgrade pip
pip install pygame customtkinter pillow pyinstaller pyinstaller-hooks-contrib

:: Build avec PyInstaller
echo Compilation en cours (cela peut prendre quelques minutes)...
pyinstaller --onefile --windowed menu.spec

echo.
if exist "dist\menu.exe" (
    echo ===================================================
    echo   BUILD REUSSI ! 
    echo   L'executable se trouve dans le dossier 'dist'
    echo ===================================================
) else (
    echo Erreur lors de la compilation. Verifiez les logs ci-dessus.
)

pause
