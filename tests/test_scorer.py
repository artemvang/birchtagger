from birchnlp.scorer import LiteralScorer


def test_scorer(habra_article):
    scorer = LiteralScorer()
    literals = habra_article.extract_by_pattern("<ADJ>*<NOUN>+")
    scored_literals = scorer.assign_scores(literals)[:10]

    top_literals = [str(lit[0]) for lit in scored_literals]

    assert top_literals == ['типы данных',
                            'системной интеграции',
                            'научных вычислений ',
                            'данными ',
                            'стандартных интерфейсов',
                            'язык ',
                            'кодом',
                            'других языках',
                            'тип',
                            'массивов ']


def test_on_empty_text():
    scorer = LiteralScorer()
    assert scorer.assign_scores([]) == []
