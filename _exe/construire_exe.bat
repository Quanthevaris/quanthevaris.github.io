@echo off
rem ============================================================
rem  FISSION ARENA - fabrique FISSION_ARENA.exe a partir de FISSION_ARENA.py
rem  Mode d'emploi : double-cliquer sur ce fichier. Explications : README.md
rem ============================================================
setlocal
title FISSION ARENA - fabrication du .exe
cd /d "%~dp0"

echo ============================================================
echo   FISSION ARENA - fabrication de FISSION_ARENA.exe
echo ============================================================
echo.

rem --- 1. Trouver Python : le lanceur "py" de python.org, sinon "python"
set "PY="
py -3 --version >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if defined PY goto python_trouve
python --version >nul 2>&1
if not errorlevel 1 set "PY=python"
if defined PY goto python_trouve
echo Python est introuvable sur cet ordinateur.
echo Installe-le depuis https://www.python.org/downloads/ en cochant la case
echo "Add python.exe to PATH", puis relance ce fichier.
goto fin

:python_trouve
rem --- 2. Installer les deux outils necessaires (seulement s'ils manquent)
%PY% -c "import pygame" >nul 2>&1
if not errorlevel 1 goto pygame_pret
echo Installation de pygame (connexion Internet necessaire)...
%PY% -m pip install --quiet pygame
if not errorlevel 1 goto pygame_pret
echo pygame ne s'installe pas avec cette version de Python : essai avec pygame-ce...
%PY% -m pip install --quiet pygame-ce
if errorlevel 1 goto echec_installation

:pygame_pret
%PY% -c "import PyInstaller" >nul 2>&1
if not errorlevel 1 goto outils_prets
echo Installation de PyInstaller (connexion Internet necessaire)...
%PY% -m pip install --quiet pyinstaller
if errorlevel 1 goto echec_installation

:outils_prets
rem --- 3. Fabriquer puis tester le .exe
%PY% "%~dp0fabriquer_exe.py" %*
if errorlevel 1 goto echec_fabrication
echo.
echo C'est pret : FISSION_ARENA.exe se trouve a cote de FISSION_ARENA.py.
goto fin

:echec_installation
echo.
echo L'installation a echoue. Verifie la connexion Internet, puis relance ce fichier.
goto fin

:echec_fabrication
echo.
echo La fabrication a echoue : lis le message ci-dessus.

:fin
echo.
pause
endlocal
