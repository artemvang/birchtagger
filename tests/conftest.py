import pytest

from birchnlp.birch import Birch
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


@pytest.fixture(scope='session')
def habra_article():
    with open("tests/test_data/habrahabr_article.txt") as f:
        return Birch(f.read())


@pytest.fixture
def empty_text():
    return Birch('')
