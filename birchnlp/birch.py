import typing as t

from birchnlp.tokenizer import get_tokenizer
from birchnlp.tokenizer.config import TokenizingConfig
from birchnlp.pos_tagger import POSTagger
from birchnlp.pattern_matcher import PatternMatcher
from birchnlp.schemes import Token
from birchnlp.utils import get_stem_func


BirchType = t.TypeVar("BirchType", bound="Birch")


class Birch:

    tokens = None

    def __init__(self, text: str, tok_config: TokenizingConfig=None,
                 tagger=POSTagger(), stemmer=get_stem_func()):
        tokenize = get_tokenizer(tok_config)

        tokens, spaces = tokenize(text)
        stems = [stemmer(tok.lower()) for tok in tokens]
        if tagger:
            tags = tagger.tag(tokens)
        else:
            tags = [None] * len(tokens)

        self.tokens = []
        offset = 0
        tok_pos = 0
        for tok, tag, stem, space in zip(tokens, tags, stems, spaces):
            token = Token(tok, tag, stem, space, offset, tok_pos)
            self.tokens.append(token)
            offset += len(tok) + int(space)
            tok_pos += 1

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

    def __hash__(self):
        return hash(tuple(self.tokens))

    def __eq__(self, doc2):
        return (hash(self) == hash(doc2) and
                len(self) == len(doc2) and
                all(t1 == t2 for t1, t2 in zip(self, doc)))

    def __ne__(self, doc2):
        return (hash(self) != hash(doc2) or
                len(self) != len(doc2) or
                any(t1 != t2 for t1, t2 in zip(self, doc)))

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "".join([f"{tok.token}{' ' * tok.space}"
                        for tok in self.tokens])


def get_sentences_offsets(tokens: t.List[Token]) -> t.List[int]:
    sentences_offsets = []

    find_line_break = False
    for i, tok in enumerate(tokens):
        if tok.token in '.!?' and tok.space:
            sentences_offsets.append(i + 1)
        elif tok.token == '\n':
            find_line_break = True
        elif find_line_break:
            sentences_offsets.append(i)
            find_line_break = False

    return sentences_offsets
