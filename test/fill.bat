call env.bat

set mkpage=python -m publicstatic.publicstatic page
set mkpost=python -m publicstatic.publicstatic post
set opt=-s %sitedir% -v

%mkpage% "Understanding Creative Thinking" %opt%
%mkpage% "Designing a Better Contact Page" %opt%
%mkpage% "Understanding Typographic Hierarchy" %opt%
%mkpage% "Getting to Know GitHub Pages: Static Project Pages, Fast" %opt%
%mkpage% "Filler Content: Tools, Tips and a Dynamic Example" %opt%

%mkpage% section\page1 %opt%
%mkpage% section\page2 %opt%
%mkpage% section\section\page3 %opt%
%mkpage% section\section\page4 %opt%
%mkpage% section\section\section\page5 %opt%

%mkpost% "A Brief History of Time" %opt%
%mkpost% "The Elegant Universe" %opt%
%mkpost% "The Fabric of the Cosmos (Space, Time, and the Texture of Reality)" %opt%
%mkpost% "Surely You're Joking, Mr. Feynman! (Paperback)" %opt%
%mkpost% "QED: The Strange Theory of Light and Matter" %opt%
