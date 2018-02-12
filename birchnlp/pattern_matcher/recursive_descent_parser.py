import re
import typing as t

from birchnlp.pattern_matcher.schemes import (
    POS_TAGS_PATTERN, WORD_PATTERN)


WORD_POS_TAGS_RE = re.compile(rf"({POS_TAGS_PATTERN}|{WORD_PATTERN}|\.)")


class Parser:
    """
        Use for transforming input tokens into reverse polish form
    """

    def __init__(self, tokens: t.List[str]):
        self.reverse_polish_tokens = []
        self.tokens = iter(tokens + ["##NONE##"])
        self.current_token = next(self.tokens)

    def parse(self):
        self._exp()
        return self.reverse_polish_tokens

    def _exp(self):
        self._term()
        if self.current_token == "|":
            t = self.current_token
            self.current_token = next(self.tokens)
            self._exp()
            self.reverse_polish_tokens.append(t)

    def _term(self):
        self._factor()
        if self.current_token == "&":
            t = self.current_token
            self.current_token = next(self.tokens)
            self._term()
            self.reverse_polish_tokens.append(t)

    def _factor(self):
        self._primary()
        if self.current_token in "?*+":
            self.reverse_polish_tokens.append(self.current_token)
            self.current_token = next(self.tokens)

    def _primary(self):
        if self.current_token == "(":
            self.current_token = next(self.tokens)
            self._exp()
            if self.current_token == ")":
                self.current_token = next(self.tokens)
            else:
                err = f"Expected ')', got '{self.current_token}'"
                raise ValueError(err)
        else:
            if not WORD_POS_TAGS_RE.match(self.current_token):
                err = f"Expected pos_tag or word, got '{self.current_token}'"
                raise ValueError(err)
            self.reverse_polish_tokens.append(self.current_token)
            self.current_token = next(self.tokens)
