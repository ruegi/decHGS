@echo off
rem Make-Datei 
rem -------------------------------------
set NAME=pdfdec
set ICON=ic_lock_open_128_28434.ico
pyuic6 -x frm_%NAME%.ui -o frm_%NAME%.py
pyuic6 -x AusgabeDialogUI.ui -o AusgabeDialogUI.py


if "%1%"=="full" goto COMP
if "%1%"=="Full" goto COMP
if "%1%"=="FULL" goto COMP
goto Ende

:COMP
rmdir /s /q .\dist\%NAME%
set LD_LIBRARY_PATH=d:\DEV\Py\decHGS\.venv\Lib\site-packages\
rem set DLL=D:\DEV\Py\decHGS\.venv\Lib\site-packages\pypdfium2_raw\pdfium.dll
rem pyinstaller -w -y --clean -i %ICON%  -p . --hidden-import %DLL% --debug=imports -n %NAME% %NAME%.py
pyinstaller pdfdec.spec
rem if exist .\%NAME%.ico copy .\%NAME%.ico .\dist\%NAME%

:Ende
echo Fertig!

