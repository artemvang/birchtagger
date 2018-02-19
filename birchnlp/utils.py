import Stemmer as stemmer


def get_stem_func():
    return stemmer.Stemmer('russian').stemWord
