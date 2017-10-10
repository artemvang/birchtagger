import os
import sys
import itertools

import Stemmer as stemmer
import xxhash
import numpy as np
import scipy.sparse as sprs

from .text_utils import tokenize_word_sent

END_TOKEN = u"$END$"
START_TOKEN = u"$START$"

FEATURE_SENT_START = u"sentence_start"
FEATURE_SENT_END = u"sentence_end"
WORD_FEATURE_PATTERN = u"{}_word_{}"
BASIC_FEATURE_PATTERN = u"{}_basic_{}"
SUFFIX_FEATURE_PATTERN = u"{}_suffix_{}"
PREFIX_FEATURE_PATTERN = u"{}_prefix_{}"

MIN_CHARS = 2
MAX_CHARS = 5
MIN_WORD_LEN = 4

FEATURES_COUNT = 2**22

SEED = 1337

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
COEF_FILE = "coef.npz"
INTERCEPT_FILE = "intercept.npy"
CLASSES_FILE = "classes.txt"


class POSTagger(object):

    def __init__(self, data_dir=DATA_DIR):
        self.coef_, self.intercept_ = self.__load_weights(data_dir)

        self.classes_ = self.__load_classes(data_dir)
        self.stemmer = stemmer.Stemmer("russian")

    def __load_weights(self, data_dir):
        coef = sprs.load_npz(os.path.join(data_dir, COEF_FILE))
        intercept = np.load(os.path.join(data_dir, INTERCEPT_FILE))

        return coef, intercept

    def __load_classes(self, data_dir):
        with open(os.path.join(data_dir, CLASSES_FILE)) as f:
            classes = [l.strip() for l in f]

        return classes

    def __get_features_words_window(self, words_window):
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
                word = self.stemmer.stemWord(word)

            yield WORD_FEATURE_PATTERN.format(i, word)

    def __get_features_sent(self, sent):
        sent_new = [START_TOKEN, START_TOKEN] + sent + [END_TOKEN, END_TOKEN]

        for i in range(len(sent_new) - 4):
            feats_gen = self.__get_features_words_window(sent_new[i:i + 5])
            hashes = set(get_hash(feat)for feat in feats_gen)
            yield hashes

    def __get_features_matrix(self, sents_words):
        words_ids, feat_ids = [], []
        words_counter = 0
        for sent in sents_words:
            for feats_ids in self.__get_features_sent(sent):
                for feat_id in feats_ids:
                    words_ids.append(words_counter)
                    feat_ids.append(feat_id)
                words_counter += 1

        data = np.ones((len(words_ids),))
        features_matrix = sprs.coo_matrix(
            (data, (words_ids, feat_ids)),
            shape=(words_counter, FEATURES_COUNT)).tocsr()

        return features_matrix

    def tag(self, text):
        if sys.version_info[0] < 3 and not isinstance(text, unicode):
            text = unicode(text, 'utf-8')

        sents_words = tokenize_word_sent(text)

        features_matrix = self.__get_features_matrix(sents_words)
        predictions = features_matrix.dot(self.coef_) + self.intercept_

        predictions = np.asarray(predictions)
        tags = [self.classes_[i] for i in predictions.argmax(axis=1)]

        return list(zip(itertools.chain.from_iterable(sents_words), tags))


def get_hash(feat):
    feat = feat.encode("utf-8")
    return xxhash.xxh64(feat, seed=SEED).intdigest() % FEATURES_COUNT


def get_basic_features(word):
    for key, func in FEATURE_PREDICATES.items():
        yield "{}_{}".format(key, func(word))


def is_number(x):
    try:
        float(x) if "." in x else int(x)
        return True
    except ValueError:
        return False


FEATURE_PREDICATES = {
    "is_upper": lambda x: str(x.isupper()),
    "is_number": is_number,
    "is_title": lambda x: str(x.istitle()),
    "has_score": lambda x: str("-" in x),
    "has_dot": lambda x: str("." in x),
    "word_len": lambda x: str(len(x)),
}
