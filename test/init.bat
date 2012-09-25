call env.bat
if exist %sitedir% rd /s /q %sitedir%

python %pub% init -s %sitedir% -v
