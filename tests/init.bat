call env.bat
if exist %sitedir% rd /s /q %sitedir%
python -m publicstatic init -s %sitedir%
