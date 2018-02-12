import typing as t

from birchnlp.tokenizer import get_tokenizer
from birchnlp.tokenizer.config import TokenizingConfig
from birchnlp.pos_tagger import POSTagger
from birchnlp.pattern_matcher import PatternMatcher
from birchnlp.schemes import Token


BirchType = t.TypeVar("BirchType", bound="Birch")


class Birch:

    tokens = None

    def __init__(self, text: str, tok_config: TokenizingConfig=None):
        tokenize = get_tokenizer(tok_config)
        tagger = POSTagger()

        tokens, spaces = tokenize(text)
        tags = tagger.tag(tokens)

        self.tokens = []
        offset = 0
        for tok, tag, space in zip(tokens, tags, spaces):
            token = Token(tok, tag, space, offset)
            self.tokens.append(token)
            offset += len(tok) + int(space)

        self.sentences_offsets_ = get_sentences_offsets(self.tokens)

    def __iter__(self):
        yield from iter(self.tokens)

    def __len__(self):
        return len(self.tokens)

    def __getitem__(self, index):
        if isinstance(index, int):
            return self.tokens[index]
        elif isinstance(index, slice):
            toks = self.tokens[index.start: index.stop: index.step]
            return Birch.build_from_tokens(toks)

        raise ValueError("Invalid index value, expected int or slice")

    @classmethod
    def build_from_tokens(cls, tokens: t.List[Token]) -> BirchType:
        birch = object.__new__(Birch)
        birch.tokens = tokens
        return birch

    @property
    def bounds(self):
        return self.tokens[0].start, self.tokens[-1].end

    @property
    def sentences(self):
        last_offset = 0
        for offset in self.sentences_offsets_:
            yield Birch.build_from_tokens(self.tokens[last_offset: offset])
            last_offset = offset

        yield Birch.build_from_tokens(self.tokens[last_offset:])

    def extract_by_pattern(self, pattern: str) -> t.List[BirchType]:
        matcher = PatternMatcher(pattern)

        matches = []

        for sent in self.sentences:
            for start, fin in matcher.findall(sent):
                matches.append(Birch.build_from_tokens(sent[start: fin]))

        return matches

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "".join([f"{tok.token}{' ' * tok.space}"
                        for tok in self.tokens])


def get_sentences_offsets(tokens: t.List[Token]) -> t.List[int]:
    sentences_offsets = []

    for i, tok in enumerate(tokens):
        if tok.token in '.!?' and tok.space:
            sentences_offsets.append(i + 1)

    return sentences_offsets
