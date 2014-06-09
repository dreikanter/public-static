import bs4
import codecs
import re

file_name = 'D:/src/drafts.cc/pages/behavioral-economics-glossary.md'
text = codecs.open(file_name, mode='r', encoding='utf-8').read()

# soup = bs4.BeautifulSoup(html, 'html5lib')

_re_param = re.compile(r"^\s*([\w\d_-]+)\s*[:=]{1}(.*)", re.U)

result = {}
lines = text.splitlines()
num = 0
for line in lines:
    match = _re_param.match(line)
    if match:
        field = match.group(1).strip().lower()
        result[field] = match.group(2).strip()
        num += 1
    else:
        break

_re_md_markup = [
    (r"^\s*#+\s*|\*\*", ''),
    (r"\[(.*)?\]\(.*?\)", r"\g<1>"),
    (r"\[\[(.*)?\]\]", r"\g<1>"),
]

for k, v in _re_md_markup:
    print(k, v)

# def _strip_md(text):
#     """Strip markdown syntax."""
#     for pattern in _re_md_markup:
#         substitution = _re_md_markup[pattern]
#         text = re.sub(pattern, substitution, text)
#     return text

# # md = """# Behavioral Economics Glossary

# # [Source](http://quizlet.com/23020804/behavioral-economics-glossary-all-may-2013-flash-cards/) at quizlet.com.

# # **Anchoring** — A [[cognitive bias]] that describes the common human tendency to rely too heavily on the first piece of information offered (the "anchor") when making decisions.
# # """

# with codecs.open('__results.txt', mode='w', encoding='utf-8') as f:
#     f.write(_strip_md(md))


# # exit()

# MIN_DESC_LEN = 200

# desc = []
# desc_len = 0

# for line in lines[num:]:
#     line = line.strip()
#     if not line:
#         if desc_len > MIN_DESC_LEN: break
#     else:
#         desc.append(line)
#         desc_len += len(line)

# description = _strip_md('\n'.join(desc)).replace('\n', ' ')

# with codecs.open('__results.txt', mode='w', encoding='utf-8') as f:
#     for key in result:
#         f.write("%s: %s" % (key, result[key]))
#     f.write("\n---\n")
#     f.write(description)
#     f.write("\n---\n")
#     f.write('\n'.join(lines[num:]))
