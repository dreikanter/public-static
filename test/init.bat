call env.bat
if exist %sitedir% rd /s /q %sitedir%

python %pub% init -s %sitedir% -v

python %pub% page page1 -s %sitedir% -v
python %pub% page page2 -s %sitedir% -v
python %pub% page page3 -s %sitedir% -v
python %pub% page page4 -s %sitedir% -v
python %pub% page page5 -s %sitedir% -v

python %pub% page section\page1 -s %sitedir% -v
python %pub% page section\page2 -s %sitedir% -v
python %pub% page section\section\page3 -s %sitedir% -v
python %pub% page section\section\page4 -s %sitedir% -v
python %pub% page section\section\section\page5 -s %sitedir% -v

python %pub% post issue1 -s %sitedir% -v
python %pub% post issue2 -s %sitedir% -v
python %pub% post issue3 -s %sitedir% -v
python %pub% post issue4 -s %sitedir% -v
python %pub% post issue5 -s %sitedir% -v

python %pub% post secondary-blog/post1 -s %sitedir% -v
python %pub% post secondary-blog/post2 -s %sitedir% -v
python %pub% post secondary-blog/post3 -s %sitedir% -v
python %pub% post secondary-blog/post4 -s %sitedir% -v
python %pub% post secondary-blog/post5 -s %sitedir% -v
