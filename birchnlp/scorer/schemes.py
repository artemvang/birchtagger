import typing as t

from birchnlp.birch import Birch


class LiteralWrapper:

    def __init__(self, literal: Birch):
        self.literal = literal
        self.stem = ' '.join([tok.stem for tok in literal])
        self._hash = hash(self.stem)

    def __iter__(self):
        for tok in self.literal:
            yield tok

    def __len__(self):
        return len(self.literal)

    def __hash__(self):
        return self._hash

    def __eq__(self, lit):
        return hash(self) == hash(lit) and self.stem == lit.stem

    def __ne__(self, kw):
        return hash(self) != hash(lit) or self.stem != lit.stem

    def __repr__(self):
        return f"<LiteralWrapper(stem={self.stem})>"

    def __str__(self):
        return self.stem
