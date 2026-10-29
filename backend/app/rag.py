import json
import os
from functools import lru_cache

import numpy as np

from . import config, documents, llm
from .errors import ConfigurationError
from .safety import simplify

SUGGESTED_QUESTIONS = [
    'Qu’est-ce que la MPOC ?',
    'Quels sont les symptômes de la MPOC ?',
    'Quels sont les facteurs de risque de la BPCO ?',
    'Comment prévenir la MPOC ?',
]


def question_key(question):
    return ' '.join(simplify(question).strip(' ?.!').split())


def normalize(vectors):
    values = np.asarray(vectors, dtype=float)
    if not np.isfinite(values).all():
        raise ValueError('Vecteurs invalides.')
    norms = np.linalg.norm(values, axis=-1, keepdims=True)
    return values / np.maximum(norms, 1e-12)


def build_index():
    chunks = documents.load_chunks()
    if not chunks:
        raise ValueError('Aucun texte exploitable dans le corpus. Les PDF numérisés nécessitent un OCR préalable.')
    vectors = []
    for start in range(0, len(chunks), 64):
        vectors.extend(llm.embed([c['text'] for c in chunks[start:start + 64]]))
    payload = dict(model=config.EMBEDDING_MODEL, fingerprint=documents.corpus_fingerprint(),
                   chunks=chunks, vectors=normalize(vectors).tolist())
    # Questions publiques de l’interface uniquement : aucun texte utilisateur conservé.
    suggested_vectors = llm.embed(SUGGESTED_QUESTIONS)
    payload['suggested_vectors'] = dict(zip(map(question_key, SUGGESTED_QUESTIONS), normalize(suggested_vectors).tolist()))
    config.INDEX.parent.mkdir(parents=True, exist_ok=True)
    temporary = config.INDEX.with_suffix('.tmp')
    temporary.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
    os.replace(temporary, config.INDEX)
    read_index.cache_clear()
    return len(chunks)


@lru_cache(maxsize=1)
def read_index(stamp):
    data = json.loads(config.INDEX.read_text(encoding='utf-8'))
    if data['model'] != config.EMBEDDING_MODEL or data['fingerprint'] != documents.corpus_fingerprint():
        raise ConfigurationError('Le corpus ou le modèle a changé. Exécutez python -m scripts.build_index puis redémarrez le serveur.')
    return data


def search(question):
    if not config.INDEX.exists():
        raise ConfigurationError('L’index documentaire n’a pas encore été créé. Exécutez python -m scripts.build_index dans le dossier du projet. Si la connexion échoue, lancez python -m scripts.check_connection.')
    data = read_index(config.INDEX.stat().st_mtime_ns)
    # Vérification légère pour ne jamais servir un corpus modifié sans réindexation.
    if data['fingerprint'] != documents.corpus_fingerprint():
        raise ConfigurationError('Le corpus a changé. Exécutez python -m scripts.build_index puis redémarrez le serveur.')
    query = data.get('suggested_vectors', {}).get(question_key(question))
    if query is None:
        query = normalize(llm.embed([question]))[0]
    else:
        query = np.asarray(query)
    scores = np.asarray(data['vectors']) @ query
    order = np.argsort(scores)[::-1][:config.TOP_K]
    return [{**data['chunks'][i], 'score': float(scores[i])} for i in order if scores[i] >= config.THRESHOLD]
