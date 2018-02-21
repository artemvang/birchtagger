import re
import itertools
import typing as t
from collections import defaultdict, Counter

import numpy as np

from birchnlp.birch import Birch
from birchnlp.schemes import Token
from birchnlp.scorer.schemes import LiteralWrapper
from birchnlp.pos_tagger.schemes import POSTag


IMPORTANT_PUNCT_RE = re.compile(r"-/\\")
DEFAULT_PERCENTILE = 20

VALID_POS_TAGS = {POSTag.NOUN, POSTag.ADJ, POSTag.NUM, POSTag.VERB, POSTag.AUX}


class LiteralScorer:

    def __init__(self, percentile: int=DEFAULT_PERCENTILE, topn: int=0):
        self.percentile = percentile
        self.topn = topn

    def assign_scores(self, literals: t.List[Birch]
                      ) -> t.List[t.Tuple[Birch, float]]:
        if not literals:
            return []

        if len(literals) == 1:
            return [(lit, 1.) for lit in literals]

        wrapped_literals = [LiteralWrapper(l) for l in literals]

        literals_freq = Counter(wrapped_literals)

        token_scores = self.get_token_scores(set(wrapped_literals))

        literals_scores = {}
        for literal, literal_freq in literals_freq.items():
            scores = 0.
            for token in literal:
                scores += token_scores.get(token.stem, 0.)
            literals_scores[literal] = scores * np.log(literal_freq)

        score_values = list(literals_scores.values())
        min_score = abs(min(score_values))

        sorted_by_score = sorted(literals_scores.items(),
                                 key=lambda x: x[1], reverse=True)

        if self.topn > 0:
            return [(lit.literal, sc + min_score)
                    for lit, sc in sorted_by_score[:self.topn]]

        try:
            percentile_value = np.percentile(score_values, self.percentile)
        except IndexError:
            percentile_value = -1e10

        return [(lit.literal, sc + min_score)
                for lit, sc in sorted_by_score
                if sc > percentile_value]

    def get_token_scores(self, literals: t.Set[LiteralWrapper]
                         ) -> t.Dict[str, float]:
        all_tokens = itertools.chain.from_iterable(literals)
        filtered_tokens = (tok.stem for tok in all_tokens
                           if tok.pos in VALID_POS_TAGS)

        tokens_freqs = Counter(filtered_tokens)
        tokens_degree = defaultdict(int)
        for literal in literals:
            degree = len(literal) - 1

            for token in literal:
                tokens_degree[token.stem] += degree

        token_scores = {}
        total_tokens_count = len(list(tokens_freqs.elements()))
        for token, token_freq in tokens_freqs.items():
            token_scores[token] = (
                token_freq + tokens_degree[token]) / token_freq

        return token_scores
