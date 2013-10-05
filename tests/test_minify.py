# encoding: utf-8

import bs4
import re
from html.parser import HTMLParser
from publicstatic import minify


test_html = """
<!DOCTYPE HTML>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Title of the document</title>
    <!--[if IE]>
    <script src="http://html5shiv.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->
    <!--[if lte IE 7]>
    <script src="js/IE8.js" type="text/javascript"></script>
    <![endif]-->
    <!--[if lt IE 7]>
    <link rel="stylesheet" type="text/css" media="all" href="css/ie6.css"/>
    <![endif]-->
    <script>
        var dataInput = document.getElementById('data'),
            output = document.getElementById('fromEvent');

        addEvent(window, 'storage', function (event) {
          if (event.key == 'storage-event-test') {
            output.innerHTML = event.newValue;
          }
        });

        addEvent(dataInput, 'keyup', function () {
          localStorage.setItem('storage-event-test', this.value);
        });
    </script>
    <style>
    body {
        padding: 10px;
    }
    a {
        color: green;
    }
    </style>
</head>
<body>

    <header id="banner" class="body">
        <h1><a href="#">Smashing HTML5! <strong>HTML5 in the year
        <del>2022</del> <ins>2009</ins></strong></a></h1>

        <nav><ul>
            <li class="active"><a href="#">home</a></li>
            <li><a href="#">portfolio</a></li>

            <li><a href="#">blog</a></li>
            <li><a href="#">contact</a></li>
        </ul></nav>

    </header>

    <section>
      <h1>WWF</h1>
      <p>The World Wide Fund for Nature (WWF) is....</p>
    </section>

    <pre class="language-python">
    # This section should remain untouched

    def hello():
        pass

    </pre>


</body>
</html>
"""

test_result = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/><title>Title of the document</title><script>
        var dataInput = document.getElementById('data'),
            output = document.getElementById('fromEvent');

        addEvent(window, 'storage', function (event) {
          if (event.key == 'storage-event-test') {
            output.innerHTML = event.newValue;
          }
        });

        addEvent(dataInput, 'keyup', function () {
          localStorage.setItem('storage-event-test', this.value);
        });
    </script><style>body { padding: 10px; } a { color: green; }</style></head><body><header class="body" id="banner"><h1><a href="#">Smashing HTML5! <strong>HTML5 in the year<del>2022</del> <ins>2009</ins></strong></a></h1><nav><ul><li class="active"><a href="#">home</a></li><li><a href="#">portfolio</a></li><li><a href="#">blog</a></li><li><a href="#">contact</a></li></ul></nav></header><section><h1>WWF</h1><p>The World Wide Fund for Nature (WWF) is....</p></section><pre class="language-python">    # This section should remain untouched

    def hello():
        pass

    </pre></body></html>"""


def test_minify():
    assert minify.minify_html(test_html) == test_result


def main():
    test_minify()


if __name__ == '__main__':
    main()
