import re
import itertools
import typing as t

from birchnlp.pattern_matcher.recursive_descent_parser import Parser
from birchnlp.pattern_matcher.schemes import (
    State, StartEndPair, PatternToken,
    OPERANDS, WORD_PATTERN, POS_TAGS_PATTERN)
from birchnlp.pos_tagger.schemes import POSTag
from birchnlp.schemes import Token

VARS_RE = re.compile(r"({}|{}|\.)".format(
    POS_TAGS_PATTERN, WORD_PATTERN))

TOKENS_RE = re.compile(r"({}|{}|{}|\.)".format(
    POS_TAGS_PATTERN, WORD_PATTERN, OPERANDS))


class PatternMatcher:

    def __init__(self, pattern: str):
        self.pattern = pattern
        tokens = tokenize_pattern(pattern)
        reverse_polish_tokens = Parser(tokens).parse()
        self.start_state = build_nfa(reverse_polish_tokens)

    def findall(self, words: t.Iterable[Token]) -> t.List[t.Tuple[int, int]]:
        """
            Works well on sentences, not on whole big text corpuses.
        """
        coords = []

        counter = 0
        while counter < len(words):
            best_match = self.extract_best_match(words[counter:])
            if best_match != 0:
                coords.append((counter, counter + best_match))
            counter += 1

        return coords

    def addstate(self, state: State, states: t.Set[State]):
        if state in states:
            return
        states.add(state)
        for eps in state.epsilon:
            self.addstate(eps, states)

    def extract_best_match(self, words: t.Iterable[Token]) -> int:
        best_match = 0

        current_states = set()
        self.addstate(self.start_state, current_states)

        for token_ind, token in enumerate(words):
            next_states = set()
            for state in current_states:
                for trans in state.transitions:
                    if trans.is_correct_token(token):
                        trans_state = state.transitions[trans]
                        self.addstate(trans_state, next_states)

            if not next_states:
                break
            current_states = next_states

            for state in current_states:
                if state.is_end:
                    best_match = max(token_ind + 1, best_match)
                    break

        return best_match

    def __str__(self):
        return self.pattern


def build_nfa(tokens: t.List[str]) -> State:
    """
    Build Non-Deterministic Automata (NFA) using Thompson's algorithm. Explanations:
    https://en.wikipedia.org/wiki/Thompson%27s_construction
    https://xysun.github.io/posts/regex-parsing-thompsons-algorithm.html
    """

    stack = []

    for token in tokens:
        if token == "&":
            n2 = stack.pop()
            n1 = stack.pop()
            n1.end.is_end = False
            n1.end.epsilon.append(n2.start)
            n2.end.is_end = True
            nfa = StartEndPair(n1.start, n2.end)
            stack.append(nfa)

        elif token == "|":
            n2 = stack.pop()
            n1 = stack.pop()
            s0 = State(epsilon=[n1.start, n2.start])
            s3 = State()
            n1.end.epsilon.append(s3)
            n2.end.epsilon.append(s3)
            n1.end.is_end = False
            n2.end.is_end = False
            s3.is_end = True
            nfa = StartEndPair(s0, s3)
            stack.append(nfa)

        elif token in ("*", "+"):
            n1 = stack.pop()
            s0 = State(epsilon=[n1.start])
            s1 = State()
            if token == "*":
                s0.epsilon.append(s1)
            n1.end.epsilon.extend([s1, n1.start])
            n1.end.is_end = False
            s1.is_end = True
            nfa = StartEndPair(s0, s1)
            stack.append(nfa)

        elif token == "?":
            n1 = stack.pop()
            n1.start.epsilon.append(n1.end)
            stack.append(n1)

        else:
            s1 = State()
            s0 = State(transitions={PatternToken(token): s1})
            s1.is_end = True
            nfa = StartEndPair(s0, s1)
            stack.append(nfa)

    if len(stack) != 1:
        raise ValueError(
            "Stack size must equals 1, got size {}".format(len(stack)))
    return stack[-1].start


def tokenize_pattern(regexp: str) -> t.List[str]:
    tokens1, tokens2 = itertools.tee(TOKENS_RE.findall(regexp))
    tokens = [next(tokens2)]
    for t1, t2 in zip(tokens1, tokens2):
        if ((VARS_RE.match(t1) or t1 in ")*+?") and
                (VARS_RE.match(t2) or t2 == "(")):
            tokens.append("&")
        tokens.append(t2)
    return tokens
