import re as regex

from . import BasePreparator


class CommentsPreparator(BasePreparator):

    multi_line_re = regex.compile(r'/\*((.|\n)*?)\*/')
    single_line_re = regex.compile(r'//.*')

    def prepare(self, text: str):
        trimmed = self.multi_line_re.sub('', text)
        trimmed = self.single_line_re.sub('', trimmed)
        return trimmed
