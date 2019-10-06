import re as regex
from os.path import isfile

from . import BasePreparator
from .errors import PreparationError


class IncludePreparator(BasePreparator):

    helper_pattern = ">include \"(.*)\""

    def prepare(self, text: str) -> str:
        while True:
            match = regex.search(self.helper_pattern, text)
            if match is None:
                break

            file_name = match.groups()[0]
            if not isfile(file_name):
                raise PreparationError(f'File to include {file_name} is not found')

            with open(file_name) as f:
                file_content = ''.join(f.readlines())
                (start, end) = match.span()
                text = text[0: start] + file_content + text[end:]

        return text
