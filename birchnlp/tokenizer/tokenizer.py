import typing as t
import itertools

from birchnlp.tokenizer.config import TokenizingConfig


def tokenize(sentence: str, key2equation: t.Dict[str, str],
             config) -> t.List[str]:
    tokenized = []
    spaces = []

    for tok in config.SPACES_RE.split(sentence):
        last_pos = 0
        if config.SPECIFIC_TOKEN_RE.search(tok):
            for iter_tok in config.SPECIFIC_TOKEN_RE.finditer(tok):
                start, end = iter_tok.span()
                if start != last_pos:
                    sub_tokens = prepare_token(tok[last_pos: start], config)
                    tokenized += sub_tokens
                    spaces += [False] * len(sub_tokens)

                last_pos = end

                tokenized.append(iter_tok.group())
                spaces.append(False)

            if last_pos != len(tok):
                sub_tokens = prepare_token(tok[last_pos:], config)
                tokenized += sub_tokens
                spaces += [False] * len(sub_tokens)

        else:
            sub_tokens = prepare_token(tok, config)
            tokenized += sub_tokens
            spaces += [False] * len(sub_tokens)
        spaces[-1] = True

    words = [key2equation.get(word, word) for word in tokenized]
    spaces[-1] = False
    return words, spaces


def prepare_token(token: str, config) -> t.List[str]:
    tokenized = []
    suffixes = []
    while True:
        pref_match = config.PREFIX_RE.search(token)
        if pref_match and pref_match.span()[0] == 0:
            tokenized.append(pref_match.group())
            token = token[pref_match.span()[1]:]

        if token and config.SUFFIX_SPACE_RE.match(token[-1]):
            suffixes.append(token[-1])
            token = token[:-1]
            continue

        suff_match = config.SUFFIX_RE.search(token)
        if suff_match and suff_match.span()[1] == len(token):
            suffixes.append(suff_match.group())
            token = token[:suff_match.span()[0]]

        if not token or ((not pref_match) and (not suff_match)):
            break

    if not token:
        tokenized += suffixes[::-1]
        return tokenized

    last_index = 0
    if len(token) > 2:
        delimiters = config.INFIX_RE.finditer(token)
        for delimiter in delimiters:
            if last_index != delimiter.span()[0]:
                sub_tok = token[last_index: delimiter.span()[0]]
                tokenized += prepare_token(sub_tok, config)
            tokenized.append(delimiter.group())
            last_index = delimiter.span()[1]

    if last_index > 0:
        tokenized += prepare_token(token[last_index: len(token)], config)
    else:
        tokenized.append(token)

    tokenized += suffixes[::-1]

    return tokenized


def get_tokenizer(config: TokenizingConfig=None) -> t.Callable:
    if config is None:
        config = TokenizingConfig()

    def tokenize_text(text: str) -> t.Tuple[t.List[str], t.List[bool]]:
        if not text.strip():
            return [], []

        key2equation = {}
        if config.TOKENS_RE:
            for i, eq in enumerate(config.TOKENS_RE.finditer(text)):
                eq = eq.group(0)
                key = f"~~specific_token_{i}~~"
                text = text.replace(eq, key)
                key2equation[key.strip()] = eq

        tokens, spaces = tokenize(text, key2equation, config)
        if config.SKIP_TOKENS_RE:
            new_tokens, new_spaces = [], []
            for tok, sp in zip(tokens, spaces):
                if config.SKIP_TOKENS_RE.match(tok):
                    continue
                new_tokens.append(tok)
                new_spaces.append(sp)
            return new_tokens, new_spaces

        return tokens, spaces

    return tokenize_text
