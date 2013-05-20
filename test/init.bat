call env.bat
if exist %sitedir% rd /s /q %sitedir%
python -m publicstatic.publicstatic init -s %sitedir% -v
