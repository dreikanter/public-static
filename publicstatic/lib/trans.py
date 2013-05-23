# coding: utf8

"""
This module translates national characters into similar sounding
latin characters (transliteration).
At the moment, Czech, Greek, Latvian, Polish, Turkish, Russian, Ukrainian
and Kazakh alphabets are supported (it covers 99% of needs).

Python 3:

  >>> from trans import trans
  >>> trans('Привет, Мир!')

Python 2:

  >>> import trans
  >>> 'Привет, Мир!'.encode('trans')
  'Privet, Mir!'
  >>> trans.trans(u'Привет, Мир!')
  'Privet, Mir!'

Source and full documentations can be found here:
https://github.com/zzzsochi/trans
"""

import sys
import codecs

__version__ = '2.0'
__author__ = 'Zelenyak Aleksandr aka ZZZ <zzz.sochi@gmail.com>'

PY2 = sys.version_info[0] == 2


class Trans(object):
    '''Main class for transliteration with tables.'''
    def __init__(self, tables=None, default_table=None):
        self.tables = tables or {}
        self.default_table = default_table

    def __call__(self, input, table=None):
        '''Translate unicode string, using 'table'.
           Table may be tuple (diphthongs, other), dict (other) or string name of table.'''

        if table is None:
            if self.default_table is not None:
                table = self.default_table
            else:
                raise ValueError('Table not set.')

        if not isinstance(input, unicode if PY2 else str):
            raise TypeError(
                'trans codec support only unicode string, {0!r} given.'.format(type(input))
            )

        if isinstance(table, basestring if PY2 else str):
            try:
                table = self.tables[table]
            except KeyError:
                raise ValueError('Table "{0}" not found in tables!'.format(table))

        if isinstance(table, dict):
            table = ({}, table)

        first = input
        for diphthong, value in table[0].items():
            first = first.replace(diphthong, value)

        default = table[1].get(None, '_')

        second = ''
        for char in first:
            second += table[1].get(char, default)

        return second


latin = {
    'à': 'a',  'á': 'a',  'â': 'a', 'ã': 'a', 'ä': 'a', 'å': 'a',
    'æ': 'ae', 'ç': 'c',  'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
    'ì': 'i',  'í': 'i',  'î': 'i', 'ï': 'i', 'ð': 'd', 'ñ': 'n',
    'ò': 'o',  'ó': 'o',  'ô': 'o', 'õ': 'o', 'ö': 'o', 'ő': 'o',
    'ø': 'o',  'ù': 'u',  'ú': 'u', 'û': 'u', 'ü': 'u', 'ű': 'u',
    'ý': 'y',  'þ': 'th', 'ÿ': 'y',

    'À': 'A',  'Á': 'A',  'Â': 'A', 'Ã': 'A', 'Ä': 'A', 'Å': 'A',
    'Æ': 'AE', 'Ç': 'C',  'È': 'E', 'É': 'E', 'Ê': 'E', 'Ë': 'E',
    'Ì': 'I',  'Í': 'I',  'Î': 'I', 'Ï': 'I', 'Ð': 'D', 'Ñ': 'N',
    'Ò': 'O',  'Ó': 'O',  'Ô': 'O', 'Õ': 'O', 'Ö': 'O', 'Ő': 'O',
    'Ø': 'O',  'Ù': 'U',  'Ú': 'U', 'Û': 'U', 'Ü': 'U', 'Ű': 'U',
    'Ý': 'Y',  'Þ': 'TH', 'ß': 'ss'
}

greek = {
    'α': 'a', 'β': 'b', 'γ': 'g', 'δ': 'd', 'ε': 'e',  'ζ': 'z',
    'η': 'h', 'θ': '8', 'ι': 'i', 'κ': 'k', 'λ': 'l',  'μ': 'm',
    'ν': 'n', 'ξ': '3', 'ο': 'o', 'π': 'p', 'ρ': 'r',  'σ': 's',
    'τ': 't', 'υ': 'y', 'φ': 'f', 'χ': 'x', 'ψ': 'ps', 'ω': 'w',
    'ά': 'a', 'έ': 'e', 'ί': 'i', 'ό': 'o', 'ύ': 'y',  'ή': 'h',
    'ώ': 'w', 'ς': 's', 'ϊ': 'i', 'ΰ': 'y', 'ϋ': 'y',  'ΐ': 'i',

    'Α': 'A', 'Β': 'B', 'Γ': 'G', 'Δ': 'D', 'Ε': 'E',  'Ζ': 'Z',
    'Η': 'H', 'Θ': '8', 'Ι': 'I', 'Κ': 'K', 'Λ': 'L',  'Μ': 'M',
    'Ν': 'N', 'Ξ': '3', 'Ο': 'O', 'Π': 'P', 'Ρ': 'R',  'Σ': 'S',
    'Τ': 'T', 'Υ': 'Y', 'Φ': 'F', 'Χ': 'X', 'Ψ': 'PS', 'Ω': 'W',
    'Ά': 'A', 'Έ': 'E', 'Ί': 'I', 'Ό': 'O', 'Ύ': 'Y',  'Ή': 'H',
    'Ώ': 'W', 'Ϊ': 'I', 'Ϋ': 'Y'
}

turkish = {
    'ş': 's', 'Ş': 'S', 'ı': 'i', 'İ': 'I', 'ç': 'c', 'Ç': 'C',
    'ü': 'u', 'Ü': 'U', 'ö': 'o', 'Ö': 'O', 'ğ': 'g', 'Ğ': 'G'
}

russian = (
    {
        'юй': 'yuy', 'ей': 'yay',
        'Юй': 'Yuy', 'Ей': 'Yay'
    },
    {
    'а': 'a',  'б': 'b',  'в': 'v',  'г': 'g', 'д': 'd', 'е': 'e',
    'ё': 'yo', 'ж': 'zh', 'з': 'z',  'и': 'i', 'й': 'y', 'к': 'k',
    'л': 'l',  'м': 'm',  'н': 'n',  'о': 'o', 'п': 'p', 'р': 'r',
    'с': 's',  'т': 't',  'у': 'u',  'ф': 'f', 'х': 'h', 'ц': 'c',
    'ч': 'ch', 'ш': 'sh', 'щ': 'sh', 'ъ': '',  'ы': 'y', 'ь': '',
    'э': 'e',  'ю': 'yu', 'я': 'ya',

    'А': 'A',  'Б': 'B',  'В': 'V',  'Г': 'G', 'Д': 'D', 'Е': 'E',
    'Ё': 'Yo', 'Ж': 'Zh', 'З': 'Z',  'И': 'I', 'Й': 'Y', 'К': 'K',
    'Л': 'L',  'М': 'M',  'Н': 'N',  'О': 'O', 'П': 'P', 'Р': 'R',
    'С': 'S',  'Т': 'T',  'У': 'U',  'Ф': 'F', 'Х': 'H', 'Ц': 'C',
    'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sh', 'Ъ': '',  'Ы': 'Y', 'Ь': '',
    'Э': 'E',  'Ю': 'Yu', 'Я': 'Ya'
})

ukrainian = (russian[0].copy(), {
    'Є': 'Ye', 'І': 'I', 'Ї': 'Yi', 'Ґ': 'G',
    'є': 'ye', 'і': 'i', 'ї': 'yi', 'ґ': 'g'
})
ukrainian[1].update(russian[1])

czech = {
    'č': 'c', 'ď': 'd', 'ě': 'e', 'ň': 'n', 'ř': 'r', 'š': 's',
    'ť': 't', 'ů': 'u', 'ž': 'z',
    'Č': 'C', 'Ď': 'D', 'Ě': 'E', 'Ň': 'N', 'Ř': 'R', 'Š': 'S',
    'Ť': 'T', 'Ů': 'U', 'Ž': 'Z'
}

polish = {
    'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o',
    'ś': 's', 'ź': 'z', 'ż': 'z',
    'Ą': 'A', 'Ć': 'C', 'Ę': 'e', 'Ł': 'L', 'Ń': 'N', 'Ó': 'o',
    'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
}

latvian = {
    'ā': 'a', 'č': 'c', 'ē': 'e', 'ģ': 'g', 'ī': 'i', 'ķ': 'k',
    'ļ': 'l', 'ņ': 'n', 'š': 's', 'ū': 'u', 'ž': 'z',
    'Ā': 'A', 'Č': 'C', 'Ē': 'E', 'Ģ': 'G', 'Ī': 'i', 'Ķ': 'k',
    'Ļ': 'L', 'Ņ': 'N', 'Š': 'S', 'Ū': 'u', 'Ž': 'Z'
}

kazakh = (russian[0].copy(), {
    'ә': 'a', 'ғ': 'g', 'қ': 'k', 'ң': 'n', 'ө': 'o', 'ұ': 'u',
    'ү': 'u', 'һ': 'h', 'і': 'i',
    'Ә': 'A', 'Ғ': 'G', 'Қ': 'K', 'Ң': 'N', 'Ө': 'O', 'Ұ': 'U',
    'Ү': 'U', 'Һ': 'H', 'І': 'I'
})
kazakh[1].update(russian[1])

ascii_str = '''_0123456789
abcdefghijklmnopqrstuvwxyz
ABCDEFGHIJKLMNOPQRSTUVWXYZ
!"#$%&'()*+,_-./:;<=>?@[\\]^`{|}~ \t\n\r\x0b\x0c'''

ascii = ({}, dict(zip(ascii_str, ascii_str)))
for t in [latin, greek, turkish, russian, ukrainian, czech, polish, latvian, kazakh]:
    if isinstance(t, dict):
        t = ({}, t)

    ascii[0].update(t[0])
    ascii[1].update(t[1])

del t
ascii[1][None] = '_'


slug = (ascii[0].copy(), ascii[1].copy())
for c in '''!"#$%&'()*+,_-./:;<=>?@[\\]^`{|}~ \t\n\r\x0b\x0c''':
    del slug[1][c]

tables = {'ascii': ascii, 'text': ascii, 'slug': slug, 'id': slug}

# Main Trans with default tales
# It uses for str.encode('trans')
trans = Trans(tables=tables, default_table='ascii')


# trans codec work only with python 2
if PY2:
    def encode(input, errors='strict', table_name='ascii'):
        try:
            table = trans.tables[table_name]
        except KeyError:
            raise ValueError('Table "{0}" not found in tables!'.format(table_name))
        else:
            data = trans(input, table)
            return data, len(data)

    def no_decode(input, errors='strict'):
        raise TypeError('trans codec does not support decode.')

    def trans_codec(enc):
        if enc == 'trans':
            return codecs.CodecInfo(encode, no_decode)

        try:
            enc_name, table_name = enc.split('/', 1)
        except ValueError:
            return None

        if enc_name != 'trans':
            return None

        if table_name not in trans.tables:
            raise ValueError('Table "{0}" not found in tables!').format(table_name)

        return codecs.CodecInfo(lambda i, e='strict': encode(i, e, table_name), no_decode)

    codecs.register(trans_codec)
