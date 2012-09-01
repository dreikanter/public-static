call env.bat
if exist %sitedir% rd /s /q %sitedir%

python %pub% init -s %sitedir% -v

python %pub% page page1 -s %sitedir% -v
python %pub% page page2 -s %sitedir% -v
python %pub% page page3 -s %sitedir% -v
python %pub% page page4 -s %sitedir% -v
python %pub% page page5 -s %sitedir% -v

python %pub% post blog/post1 -s %sitedir% -v
python %pub% post blog/post2 -s %sitedir% -v
python %pub% post blog/post3 -s %sitedir% -v
python %pub% post blog/post4 -s %sitedir% -v
python %pub% post blog/post5 -s %sitedir% -v
