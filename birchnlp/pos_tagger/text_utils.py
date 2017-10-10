# coding: utf-8

import re


PUNCT_RE = re.compile(r"([?!.,\[\]\(\)\\\/;:\{\}+$%\^&*<>])", re.UNICODE)
QUOTES_RE = re.compile(r"([«“‘'\"])", re.UNICODE)
DOUBLE_DASHES = re.compile(r"(-{2,3})", re.UNICODE)

SENT_RE = re.compile(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)(\s|[A-Z].*)")


def word_tokenize(text):
    text = QUOTES_RE.sub(' " ', text)
    text = PUNCT_RE.sub(' \\1 ', text)
    text = DOUBLE_DASHES.sub(' - ', text)
    return text.split()


def tokenize_word_sent(text):
    sents_words = []
    for sent in tokenize_sent(text):
        sents_words.append(word_tokenize(sent))

    return sents_words


def tokenize_sent(text):
    return SENT_RE.split(text)
