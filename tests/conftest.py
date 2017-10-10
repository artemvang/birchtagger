import pytest

from birchnlp.pos_tagger import POSTagger


@pytest.fixture
def tagger():
    return POSTagger()
