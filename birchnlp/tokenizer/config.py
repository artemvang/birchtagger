import re
import sys
import unicodedata


ALL_DASHES = r''.join(chr(i) for i in range(sys.maxunicode)
                      if unicodedata.category(chr(i)) == 'Pd')

ALL_DASHES = re.escape(ALL_DASHES)

ALL_BRACKETS = r''.join(chr(i) for i in range(sys.maxunicode)
                        if unicodedata.category(chr(i)) in ('Pi', 'Pf'))
ALL_BRACKETS += "'\""
ALL_BRACKETS = re.escape(ALL_BRACKETS)

PUNCT = re.escape("\/[]()~:;_&*=^{<>}+%$#@!?.,′") + r"\s"
INFIX_PUNCT = re.escape("!?&()[]+{}=<>~*%$#") + r"\s"


class BasicTokenizingConfig:
    SPECIFIC_TOKEN_RE = re.compile(r'~~specific_token_\d+~~')
    SPACES_RE = re.compile(r"[ \t]+")


class TokenizingConfig(BasicTokenizingConfig):
    PREFIX_RE = re.compile(rf"^[{ALL_BRACKETS}{ALL_DASHES}{PUNCT}]")
    SUFFIX_RE = re.compile(rf"[{ALL_BRACKETS}{ALL_DASHES}{PUNCT}]$")
    SUFFIX_SPACE_RE = re.compile(r"\s")
    INFIX_RE = re.compile(rf"[{INFIX_PUNCT}]")

    TOKENS_RE = None
    SKIP_TOKENS_RE = None
