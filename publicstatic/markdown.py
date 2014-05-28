# coding: utf-8

import csv
import markdown
import re
from publicstatic import templates


PREFIX = '--- data:'


class DataPreprocessor(markdown.preprocessors.Preprocessor):
    def run(self, lines):
        new_lines = []
        for line in lines:
            if line.startswith(PREFIX):
                data_file, template = self._parse_args(line)
                new_lines.append(templates.render_data(data_file, template))
            else:
                new_lines.append(line)
        return new_lines

    def _parse_args(self, line):
        try:
            reader = csv.reader([line[len(PREFIX):]], skipinitialspace=True)
            for row in reader:
                data_file, template = row[0], row[1]
            return data_file, template
        except:
            return None, None


class DataExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add('data', DataPreprocessor(md), '_begin')


EXTENSIONS = [
    'def_list',
    'fenced_code',
    'grid',
    'nl2br',
    'smarty',
    DataExtension(),
]


def md(text):
    """Converts markdown formatted text to HTML"""
    return markdown.markdown(text.strip(), extensions=EXTENSIONS)
