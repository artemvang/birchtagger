def test_tagger(tagger, tokenizer):
    sample_text = ('Секретарша (Петрова-Водкина) ставила '
                   'сургучные- печати на пакет, '
                   'посетители ожидали своей очереди, '
                   'радио играло сентиментальный python вальс...')

    tokens, _ = tokenizer(sample_text)
    tags = (t.name for t in tagger.tag(tokens))

    assert list(zip(tokens, tags)) == [('Секретарша', 'NOUN'),
                                       ('(', 'PUNCT'),
                                       ('Петрова-Водкина', 'PROPN'),
                                       (')', 'PUNCT'),
                                       ('ставила', 'VERB'),
                                       ('сургучные', 'ADJ'),
                                       ('-', 'PUNCT'),
                                       ('печати', 'NOUN'),
                                       ('на', 'ADP'),
                                       ('пакет', 'NOUN'),
                                       (',', 'PUNCT'),
                                       ('посетители', 'NOUN'),
                                       ('ожидали', 'VERB'),
                                       ('своей', 'DET'),
                                       ('очереди', 'NOUN'),
                                       (',', 'PUNCT'),
                                       ('радио', 'NOUN'),
                                       ('играло', 'VERB'),
                                       ('сентиментальный', 'ADJ'),
                                       ('python', 'NOUN'),
                                       ('вальс', 'NOUN'),
                                       ('.', 'PUNCT'),
                                       ('.', 'PUNCT'),
                                       ('.', 'PUNCT')]
