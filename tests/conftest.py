import pytest

from birchnlp.pos_tagger import POSTagger
from birchnlp.tokenizer import get_tokenizer


TEST_TEXT = ("Секретарша ставила сургучные печати на пакет, ",
             "посетители ожидали своей очереди, "
             "радио играло сентиментальный вальс.")


@pytest.fixture
def tagger():
    return POSTagger()


@pytest.fixture
def tokenizer():
    return get_tokenizer()
