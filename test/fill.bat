call env.bat

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
python %pub% post issue -s %sitedir% -v
python %pub% post issue -s %sitedir% -v
