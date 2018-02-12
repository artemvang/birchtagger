import re
import enum
import string
import typing as t

from birchnlp.schemes import Token
from birchnlp.pos_tagger.schemes import POSTag


WORD_PATTERN = rf'"[A-Za-z0-9{re.escape(string.punctuation)} ]+?\"'
OPERANDS = r"[*+?()|&]"
POS_TAGS_PATTERN = r"<[A-Z]+?>"


POS_TAGS_RE = re.compile(POS_TAGS_PATTERN)
WORDS_RE = re.compile(WORD_PATTERN)


StateType = t.TypeVar("StateType", bound="State")


class TokenTypes(enum.Enum):
    pos_tag = 0
    regex = 1
    unknown = 2


class PatternToken:

    def __init__(self, token: str):
        if POS_TAGS_RE.match(token):
            self.token_type = TokenTypes.pos_tag
            self.token = POSTag[token[1:-1]]
        elif WORDS_RE.match(token):
            self.token_type = TokenTypes.regex
            self.token = re.compile(token[1:-1])
        else:
            self.token_type = TokenTypes.unknown
            self.token = token

    def __hash__(self):
        return hash(self.token)

    def __str__(self):
        if self.token_type == TokenTypes.pos_tag:
            return f'<{self.token}>'
        elif self.token_type == TokenTypes.word:
            return f'"{self.token}"'
        else:
            return '_unknown_'

    def is_correct_token(self, token: Token):
        if self.token_type == TokenTypes.unknown:
            return True

        elif self.token_type == TokenTypes.pos_tag:
            return self.token == token.pos

        else:
            return bool(self.token.match(token.token))

        return False

    def __repr__(self):
        return (f"<PatternToken(token={str(self.token)}, "
                f"token_type={self.token_type.name})>")


class State:

    def __init__(self, epsilon: t.List[StateType]=None,
                 transitions: t.Dict[PatternToken, StateType]=None):
        self.epsilon = epsilon if epsilon else []  # epsilon-closure
        self.transitions = transitions if transitions else {}  # char : state
        self.is_end = False


StartEndPair = t.NamedTuple("NFA", [('start', StateType), ('end', StateType)])
