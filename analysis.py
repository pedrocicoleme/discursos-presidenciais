#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

import dataset
import unicodedata

import regex
import nltk
import gensim

db = dataset.connect('sqlite:///data/discursos_db')
dbt = db['discurso']

stopwords = nltk.corpus.stopwords.words('portuguese')
stok = nltk.data.load('tokenizers/punkt/portuguese.pickle')

# http://stackoverflow.com/questions/8694815/removing-accent-and-special-characters
def remove_accents(data):
    return unicodedata.normalize('NFKD', data).encode('ASCII', 'ignore').lower()

def print_from_presidents():
    res = db.query("""SELECT presidente, GROUP_CONCAT(texto, ' ; ') AS texto
      FROM discurso GROUP BY presidente""")

    for row in res:
        if len(row['texto'].strip()) < 1000:
            #print row['presidente'], row['texto'].strip()
            continue

        presidente = row['presidente']
        texto_punkt = remove_accents(row['texto'])
        texto = regex.sub(ur'[^a-z^0-9^\s^.]+', u'', texto_punkt, \
          flags=regex.VERSION1|regex.IGNORECASE|regex.MULTILINE)

        print '='*20
        print presidente
        print '='*20

        sentences = [unicode(x).split() for x in stok.tokenize(texto)]

        bigram_transformer = gensim.models.Phrases(sentences)

        model_path = './data/w2v_models/%s' % presidente

        try:
            model = gensim.models.Word2Vec.load(model_path)
        except:
            model = gensim.models.Word2Vec(bigram_transformer[sentences], \
              window=10, sg=1, size=200, batch_words=200, workers=8)
            model.save(model_path)

        import pdb; pdb.set_trace()

        fd = nltk.FreqDist(w for w in texto.split() if w not in stopwords and len(w)>2)

        for word, freq in fd.most_common(20):
            print word, freq

if __name__ == u'__main__':
    print_from_presidents()
