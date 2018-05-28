
from birchnlp.pos_tagger.schemes import POSTag


class Token:

    def __init__(self, token: str, pos: POSTag, stem: str,
                 space: bool, start: int, tok_pos: int):
        self.token = token
        self.pos = pos
        self.stem = stem
        self.space = space
        self.start = start
        self.end = start + len(token)
        self.tok_pos = tok_pos
        self._hash = hash(token)

    def __copy__(self):
        return Token(self.token, self.pos, self.stem,
                     self.space, self.start, self.tok_pos)

    def __len__(self):
        return len(self.token)

    def __hash__(self):
        return self._hash

    def __eq__(self, tok2):
        return self._hash == tok2._hash and self.token == tok2.token

    def __ne__(self, tok2):
        return self._hash != tok2._hash or self.token != tok2.token

    def __repr__(self):
        return (f"<Token(token={self.token}, pos={self.pos.name}, "
                f"stem={self.stem}, start={self.start}, end={self.end})>")

    def __str__(self):
        return self.token
