# *=* coding=utf-8 *=*

test_text = u"""Секретарша ставила сургучные печати на пакет,
посетители ожидали своей очереди , радио играло сентиментальный вальс ."""

result = [(u'Секретарша', 'NOUN'),
          (u'ставила', 'VERB'),
          (u'сургучные', 'ADJ'),
          (u'печати', 'NOUN'),
          (u'на', 'ADP'),
          (u'пакет', 'NOUN'),
          (u',', 'PUNCT'),
          (u'посетители', 'NOUN'),
          (u'ожидали', 'VERB'),
          (u'своей', 'DET'),
          (u'очереди', 'NOUN'),
          (u',', 'PUNCT'),
          (u'радио', 'NOUN'),
          (u'играло', 'VERB'),
          (u'сентиментальный', 'ADJ'),
          (u'вальс', 'NOUN'),
          (u'.', 'PUNCT')]


def test_tagger(tagger):
    prediction = tagger.tag(test_text)

    assert prediction == result
