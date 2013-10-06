# coding: utf-8

import misaka


class CustomRenderer(misaka.HtmlRenderer):
    """Customized renderer for markdown processor
    to support Google Prettify."""
    def block_code(self, text, lang):
        lang = (' class="%s"' % lang) if lang else ''
        return '<pre%s><code>%s</code></pre>' % (lang, text)


_md = None


def md(text):
    global _md
    if _md is None:
        renderer = CustomRenderer()
        extensions = misaka.EXT_FENCED_CODE | \
                     misaka.EXT_NO_INTRA_EMPHASIS | \
                     misaka.EXT_STRIKETHROUGH
        _md = misaka.Markdown(renderer, extensions=extensions)
    return _md.render(text)
