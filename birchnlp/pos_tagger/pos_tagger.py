import typing as t
import os
import sys
import itertools

import xxhash
import numpy as np
import scipy.sparse as sprs

from birchnlp.pos_tagger.schemes import POSTag
from birchnlp.utils import get_stem_func

END_TOKEN = "$END$"
START_TOKEN = "$START$"

FEATURE_SENT_START = "sentence_start"
FEATURE_SENT_END = "sentence_end"
WORD_FEATURE_PATTERN = "{}_word_{}"
BASIC_FEATURE_PATTERN = "{}_basic_{}"
SUFFIX_FEATURE_PATTERN = "{}_suffix_{}"
PREFIX_FEATURE_PATTERN = "{}_prefix_{}"

MIN_CHARS = 2
MAX_CHARS = 5
MIN_WORD_LEN = 4

FEATURES_COUNT = 2**22

SEED = 1337

DATA_DIR = os.path.join(os.path.dirname(__file__), 'weights')
COEF_FILE = "coef.npz"
INTERCEPT_FILE = "intercept.npy"


class POSTagger(object):

    def __init__(self, data_dir=DATA_DIR):
        self.coef_, self.intercept_ = self._load_weights(data_dir)

        self.stemmer = get_stem_func()

    def _load_weights(self, data_dir):
        coef = sprs.load_npz(os.path.join(data_dir, COEF_FILE))
        intercept = np.load(os.path.join(data_dir, INTERCEPT_FILE))

        return coef, intercept

    def _get_features_words_window(self, words_window):
        if words_window[1] == START_TOKEN:
            yield FEATURE_SENT_START
        elif words_window[3] == END_TOKEN:
            yield FEATURE_SENT_END

        for i, word in enumerate(words_window):
            if word in {START_TOKEN, END_TOKEN}:
                yield WORD_FEATURE_PATTERN.format(i, word)
                continue

            for ind, feat in enumerate(get_basic_features(word)):
                yield BASIC_FEATURE_PATTERN.format(i, feat)

            word = word.lower()

            for c in range(MIN_CHARS, MAX_CHARS):
                yield SUFFIX_FEATURE_PATTERN.format(i, word[-c:])
                yield PREFIX_FEATURE_PATTERN.format(i, word[:c])

            if len(word) >= MIN_WORD_LEN:
                word = self.stemmer(word)

            yield WORD_FEATURE_PATTERN.format(i, word)

    def _get_features_sent(self, sent):
        sent_new = [START_TOKEN, START_TOKEN] + sent + [END_TOKEN, END_TOKEN]

        for i in range(len(sent_new) - 4):
            feats_gen = self._get_features_words_window(sent_new[i:i + 5])
            hashes = set(get_hash(feat) for feat in feats_gen)
            yield hashes

    def _get_features_matrix(self, words: t.List[str]):
        indptr, indices = [0], []
        data = []
        words_counter = 0
        for feats_ids in self._get_features_sent(words):
            for feat_id in feats_ids:
                indices.append(feat_id)
                data.append(1)
            indptr.append(len(indices))

        features_matrix = sprs.csr_matrix((data, indices, indptr),
                                          shape=(len(words), FEATURES_COUNT))

        return features_matrix

    def tag(self, words: t.List[str]) -> t.List[POSTag]:
        features_matrix = self._get_features_matrix(words)
        predictions = features_matrix.dot(self.coef_) + self.intercept_

        predictions = np.asarray(predictions)
        tags = [POSTag(i) for i in predictions.argmax(axis=1)]

        return tags


def get_hash(feat):
    feat = feat.encode("utf-8")
    return xxhash.xxh64(feat, seed=SEED).intdigest() % FEATURES_COUNT


def get_basic_features(word):
    for key, func in FEATURE_PREDICATES.items():
        yield f"{key}_{func(word)}"


def is_number(x):
    try:
        float(x)
        return True
    except ValueError:
        return False


FEATURE_PREDICATES = {
    "is_upper": lambda x: x.isupper(),
    "is_number": is_number,
    "is_title": lambda x: x.istitle(),
    "has_score": lambda x: "-" in x,
    "has_dot": lambda x: "." in x,
    "word_len": len,
}
