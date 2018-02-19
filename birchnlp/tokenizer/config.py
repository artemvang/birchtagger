import re
import sys
import unicodedata


ALL_DASH_MARKS = r''.join([
    chr(i) for i in range(sys.maxunicode)
    if unicodedata.category(chr(i)) == 'Pd'
])

ALL_DASH_MARKS = re.escape(ALL_DASH_MARKS)

ALL_QUOTATION_MARKS = r''.join([
    chr(i) for i in range(sys.maxunicode)
    if unicodedata.category(chr(i)) in ('Pi', 'Pf')
])

ALL_QUOTATION_MARKS += "'\""
ALL_QUOTATION_MARKS = re.escape(ALL_QUOTATION_MARKS)

PUNCT = re.escape("\/[]()~:;_&*=^{<>}+%$#@!?.,′") + r"\s"
INFIX_PUNCT = re.escape("!?&()[]+{}=<>~*%$#") + r"\s"


class BasicTokenizingConfig:
    SPECIFIC_TOKEN_RE = re.compile(r'~~specific_token_\d+~~')
    SPACES_RE = re.compile(r"[ \t]+")


class TokenizingConfig(BasicTokenizingConfig):
    PREFIX_RE = re.compile(rf"^[{ALL_DASH_MARKS}{ALL_QUOTATION_MARKS}{PUNCT}]")
    SUFFIX_RE = re.compile(rf"[{ALL_DASH_MARKS}{ALL_QUOTATION_MARKS}{PUNCT}]$")
    SUFFIX_SPACE_RE = re.compile(r"\s")
    INFIX_RE = re.compile(rf"[{INFIX_PUNCT}]")

    TOKENS_RE = None
    SKIP_TOKENS_RE = None
