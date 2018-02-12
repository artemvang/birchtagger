
from birchnlp.pos_tagger.schemes import POSTag


class Token:

    def __init__(self, token: str, pos: POSTag, space: bool, start: int):
        self.token = token
        self.pos = pos
        self.space = space
        self.start = start
        self.end = start + len(token)

    def __repr__(self):
        return (f"<Token(token={self.token}, pos={self.pos.name}, "
                f"start={self.start}, end={self.end})>")
