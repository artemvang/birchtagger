# BirchNLP

NLP swiss army knife for Russian language.

Types of tasks, which can solve this library:
* Tokenizing (word-level, sentence-level, with respect on whitespaces)
* POS-tagging
* Pattern matching
* Literals scoring

## Installation
```bash
git clone https://github.com/vangaa/birchtagger
cd birchtagger; python setup.py install
```

## Example usage

```python
In [1]: from birchnlp.birch import Birch

In [4]: doc = Birch("Я видел такое, во что вы, люди, просто не поверите. "
   ...:             "Штурмовые корабли в огне на подступах к Ориону. "
   ...:             "Я смотрел, как Си-лучи мерцают во тьме близ врат Тангейзера. "
   ...:             "Все эти мгновения исчезнут во времени, как слёзы под дождём. "
   ...:             "Пора умирать.")
   ...:             

In [5]: str(doc)[:50] # restoring tokenized document
Out[5]: 'Я видел такое, во что вы, люди, просто не поверите'

In [15]: len(doc) # tokens count
Out[15]: 50

In [10]: doc[1]
Out[10]: <Token(token=видел, pos=VERB, stem=видел, start=2, end=7)>

In [14]: doc[:3] # returns new Birch object
Out[14]: Я видел такое

In [16]: doc.bounds # start and end positions of text
Out[16]: (0, 235)

In [17]: doc[5:8].bounds # start and end positions of text's subset
Out[17]: (18, 25)

In [25]: NP_REGEX = ("(<DET>)?"
    ...:             "((<PART>? <ADJ> (<CCONJ> | <SCONJ>)?)* <ADJ>)?"
    ...:             "(<NOUN> | <PROPN>)+ <NUM>?")
    ...: BIG_NP_REGEX = f"({NP_REGEX} (<ADP>|<SCONJ>|<CCONJ>))* {NP_REGEX}"

In [29]: doc.extract_by_pattern(BIG_NP_REGEX)
Out[29]: 
[люди,
 Штурмовые корабли в огне на подступах к Ориону,
 Си-лучи ,
 тьме близ врат Тангейзера,
 эти мгновения ,
 времени,
 слёзы под дождём,
 Пора ]
```
