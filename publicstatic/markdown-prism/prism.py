# A temp script to debug PrismJS binding

import codecs
import markdown
import re


class CodeBlockExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        """Add CodeBlockPreprocessor to the Markdown parser."""
        md.registerExtension(self)
        proc = CodeBlockPreprocessor(md)
        md.preprocessors.add('code_block', proc, ">normalize_whitespace")


class CodeBlockPreprocessor(markdown.preprocessors.Preprocessor):
    BLOCK_PATTERN = re.compile(r"""
        ^[`~]{3,}
        [ \t]*
        (?P<language>.*)\n
        (?P<code>[\s\S]+?)\n*
        ^[`~]{3,}
        """, re.MULTILINE | re.VERBOSE)

    PRE_CODE = '<pre><code class="language-%s">\n%s\n</code></pre>'

    LANGUAGE_SHORTCUTS = {
        'py': 'python',
        'rb': 'ruby',
        'sh': 'bash',
        'js': 'javascript',
    }

    HTML_ESCAPE = {
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
    }

    def __init__(self, md):
        super(CodeBlockPreprocessor, self).__init__(md)

    def run(self, lines):
        """ Match and store Fenced Code Blocks in the HtmlStash. """
        text = "\n".join(lines)
        while True:
            match = self.BLOCK_PATTERN.search(text)
            if not match: break
            language = match.group('language') or 'none'
            if language in self.LANGUAGE_SHORTCUTS:
                language = self.LANGUAGE_SHORTCUTS[language]
            code = self._escape(match.group('code'))
            code_block = self.PRE_CODE % (language, code)
            text = "\n".join([
                text[:match.start()],
                # placeholder to replace with code after markdown processing
                self.markdown.htmlStash.store(code_block, safe=True),
                text[match.end():]])
        return text.split("\n")

    def _escape(self, text):
        """ basic html escaping """
        text = text.replace("&", "&amp;")  # should be the first one
        for ch in self.HTML_ESCAPE:
            text = text.replace(ch, self.HTML_ESCAPE[ch])
        return text


def md(text):
    """Converts markdown formatted text to HTML"""
    return markdown.markdown(text.strip(), extensions=[CodeBlockExtension()])


text = codecs.open('test.md', encoding='utf-8').read()
template = codecs.open('test.html', encoding='utf-8').read()
with codecs.open('output.html', mode='w', encoding='utf-8') as f:
    f.write(template.format(content=md(text)))
