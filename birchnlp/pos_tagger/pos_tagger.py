import typing as t
import os
import sys
import itertools

import xxhash
import numpy as np
import scipy.sparse as sprs

from birchnlp.pos_tagger.schemes import POSTag
from birchnlp.utils import get_stem_func


SEED = 1337
FEATURES_COUNT = 2**22

def get_hash(feat):
    feat = feat.encode("utf-8")
    return xxhash.xxh64(feat, seed=SEED).intdigest() % FEATURES_COUNT


FEATURE_SENT_START_HASH = get_hash("sentence_start")
FEATURE_SENT_END_HASH = get_hash("sentence_end")
START_TOKEN = "$START$"
END_TOKEN = "$END$"
WORD_FEATURE_PATTERN = "%d_word_%s"
BASIC_FEATURE_PATTERN = "%d_basic_%s"
SUFFIX_FEATURE_PATTERN = "%d_suffix_%s"
PREFIX_FEATURE_PATTERN = "%d_prefix_%s"

MIN_CHARS = 2
MAX_CHARS = 5
MIN_WORD_LEN = 4


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

    def _get_features_words_window(self, words_window: t.List[str]
                                   ) -> t.List[int]:

        features = set()

        if words_window[1] == START_TOKEN:
            features.add(FEATURE_SENT_START_HASH)
        elif words_window[3] == END_TOKEN:
            features.add(FEATURE_SENT_END_HASH)

        for i, word in enumerate(words_window):
            if word in {START_TOKEN, END_TOKEN}:
                features.add(get_hash(WORD_FEATURE_PATTERN % (i, word)))
                continue

            for ind, feat in enumerate(get_basic_features(word)):
                features.add(get_hash(BASIC_FEATURE_PATTERN % (i, feat)))

            word = word.lower()

            for c in range(MIN_CHARS, MAX_CHARS):
                features.add(get_hash(SUFFIX_FEATURE_PATTERN % (i, word[-c:])))
                features.add(get_hash(PREFIX_FEATURE_PATTERN % (i, word[:c])))

            if len(word) >= MIN_WORD_LEN:
                word = self.stemmer(word)

            features.add(get_hash(WORD_FEATURE_PATTERN % (i, word)))

        return features

    def _get_features_sent(self, sent):
        sent_new = [START_TOKEN, START_TOKEN] + sent + [END_TOKEN, END_TOKEN]

        hashes_matrix = []
        for i in range(len(sent_new) - 4):
            feats_hashes = self._get_features_words_window(sent_new[i:i + 5])
            hashes_matrix.append(feats_hashes)

        return hashes_matrix

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


def get_basic_features(word):
    features = [
        "is_upper_%s" % word.isupper(),
        "is_number_%s" % is_number(word),
        "is_title_%s" % word.istitle(),
        "has_score_%s" % ("-" in word),
        "has_dot_%s" % ("." in word),
        "word_len_%d" % len(word),
    ]

    return features


def is_number(x):
    try:
        float(x)
        return True
    except ValueError:
        return False
