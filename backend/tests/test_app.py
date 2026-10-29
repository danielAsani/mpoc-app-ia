from fastapi.testclient import TestClient
import pytest

from backend.app.main import app
from backend.app import service, rag, documents

client = TestClient(app)
PASSAGE = dict(id=1, title='Document test', section='Symptômes', document='test.md',
               page=2, url='https://example.org', text='La MPOC peut entraîner une toux chronique.', score=.8)


def fake_generation(question, passages, baseline=False):
    return dict(answer='Une toux chronique est possible.', source_ids=[1], sufficient=True), dict(input_tokens=20, output_tokens=10)


def test_health_and_frontend():
    assert client.get('/health').json()['status'] == 'ok'
    assert 'souffle' in client.get('/').text
    assert client.get('/favicon.ico').status_code == 200
    assert client.get('/favicon.svg').status_code == 200
    assert 'private-note' not in client.get('/').text


@pytest.mark.parametrize('body', [{}, {'question': ''}, {'question': '   '}, {'question': 'a' * 1001}, {'question': 5}, {'question': []}, {'question': 'MPOC', 'extra': 1}])
def test_validation(body):
    assert client.post('/ask', json=body).status_code == 422


def test_malformed_json():
    assert client.post('/ask', content='{', headers={'Content-Type': 'application/json'}).status_code == 422


def test_answer_and_sources(monkeypatch):
    monkeypatch.setattr(service.rag, 'search', lambda q: [PASSAGE])
    monkeypatch.setattr(service.llm, 'generate', fake_generation)
    data = client.post('/ask', json={'question': 'Quels symptômes de la MPOC ?'}).json()
    assert data['status'] == 'answered'
    assert data['sources'][0]['page'] == 2
    assert data['metrics']['sources_used'] == 1


@pytest.mark.parametrize('question', ['Quel médicament dois-je prendre ?', 'Est-ce que j’ai la MPOC ?', 'J’ai du mal à respirer, que dois-je faire ?', 'Quel traitement pour mon cas personnel ?', 'Ai-je la BPCO ?', 'Quelle dose prendre pour ma BPCO ?', 'Dis-moi si j’ai la MPOC'])
def test_personal_medical_refusal(question, monkeypatch):
    monkeypatch.setattr(service.rag, 'search', lambda q: pytest.fail('Le RAG ne doit pas être appelé'))
    data = client.post('/ask', json={'question': question}).json()
    assert data['status'] == 'medical'
    assert data['sources'] == []


def test_off_topic():
    assert client.post('/ask', json={'question': 'Qui a gagné le match ?'}).json()['status'] == 'off_topic'


@pytest.mark.parametrize('question', [
    'Qu’est-ce que la MPOC ?', "Qu'est-ce que la MPOC ?",
    'Est-ce que la MPOC est une maladie chronique ?',
    'Quels sont les symptômes de la MPOC ?',
    'Quels sont les facteurs de risque de la BPCO ?',
    'Comment prévenir la MPOC ?',
    'Je veux comprendre les traitements de la MPOC.',
    'J’ai la MPOC, quels sont les symptômes fréquents de cette maladie ?',
    'Mon père a la BPCO, qu’est-ce que la réadaptation pulmonaire ?',
    'Je voudrais comprendre comment le diagnostic de la MPOC est établi en général.',
    'J’ai entendu parler de la MPOC, que signifie ce terme ?',
    'Quels médicaments sont utilisés en général pour la MPOC ?',
    'Est-ce que la MPOC est contagieuse ?',
])
def test_general_questions_reach_rag(question, monkeypatch):
    monkeypatch.setattr(service.rag, 'search', lambda q: [PASSAGE])
    monkeypatch.setattr(service.llm, 'generate', fake_generation)
    response = client.post('/ask', json={'question': question})
    assert response.status_code == 200
    assert response.json()['status'] == 'answered'
    assert response.json()['sources']


def test_no_passage(monkeypatch):
    monkeypatch.setattr(service.rag, 'search', lambda q: [])
    monkeypatch.setattr(service.llm, 'generate', lambda *a: pytest.fail('Pas de génération sans contexte'))
    assert service.answer_question('MPOC et voyage spatial ?')['status'] == 'insufficient'


@pytest.mark.parametrize('ids,sufficient', [([999], True), ([], True), ([1], False), (['1'], True)])
def test_untrusted_citations(monkeypatch, ids, sufficient):
    monkeypatch.setattr(service.rag, 'search', lambda q: [PASSAGE])
    monkeypatch.setattr(service.llm, 'generate', lambda *a: (dict(answer='Invention', source_ids=ids, sufficient=sufficient), {}))
    assert service.answer_question('MPOC ?')['status'] == 'insufficient'


def test_vector_retrieval(monkeypatch, tmp_path):
    import json
    path = tmp_path / 'index.json'
    path.write_text(json.dumps(dict(model=rag.config.EMBEDDING_MODEL, fingerprint=documents.corpus_fingerprint(), chunks=[PASSAGE, {**PASSAGE, 'id': 2}], vectors=[[1, 0], [0, 1]])), encoding='utf-8')
    monkeypatch.setattr(rag.config, 'INDEX', path)
    monkeypatch.setattr(rag.llm, 'embed', lambda texts: [[1, 0]])
    rag.read_index.cache_clear()
    assert [p['id'] for p in rag.search('symptômes MPOC')] == [1]
    monkeypatch.setattr(rag.llm, 'embed', lambda texts: [[-1, -1]])
    assert rag.search('sans rapport') == []


def test_document_metadata_and_approval(tmp_path):
    import json
    path = tmp_path / 'source.md'
    path.write_text('# Symptômes\nUne longue description documentaire sur la toux chronique.', encoding='utf-8')
    with pytest.raises(ValueError):
        documents.load_chunks(tmp_path)
    path.with_suffix('.md.json').write_text(json.dumps(dict(approved=True, title='Source vérifiée')), encoding='utf-8')
    assert documents.load_chunks(tmp_path)[0]['section'] == 'Symptômes'


def test_index_build_and_stale_corpus(monkeypatch, tmp_path):
    monkeypatch.setattr(rag.config, 'INDEX', tmp_path / 'index.json')
    monkeypatch.setattr(rag.documents, 'load_chunks', lambda: [PASSAGE])
    monkeypatch.setattr(rag.llm, 'embed', lambda texts: [[1, 0] for text in texts])
    assert rag.build_index() == 1
    assert rag.search('MPOC')[0]['id'] == 1
    monkeypatch.setattr(rag.documents, 'corpus_fingerprint', lambda: 'modified')
    with pytest.raises(ValueError, match='changé'):
        rag.search('MPOC')


def test_suggested_question_does_not_call_embedding_api(monkeypatch, tmp_path):
    import json
    path = tmp_path / 'index.json'
    path.write_text(json.dumps(dict(
        model=rag.config.EMBEDDING_MODEL, fingerprint=documents.corpus_fingerprint(),
        chunks=[PASSAGE], vectors=[[1, 0]],
        suggested_vectors={rag.question_key('Qu’est-ce que la MPOC ?'): [1, 0]},
    )), encoding='utf-8')
    monkeypatch.setattr(rag.config, 'INDEX', path)
    monkeypatch.setattr(rag.llm, 'embed', lambda texts: pytest.fail('Aucun appel réseau pour les suggestions'))
    rag.read_index.cache_clear()
    assert rag.search("Qu'est-ce que la MPOC ?")[0]['id'] == 1


def test_configuration_error(monkeypatch):
    monkeypatch.setattr(service.rag, 'search', lambda q: (_ for _ in ()).throw(ValueError('secret')))
    response = client.post('/ask', json={'question': 'Définition MPOC ?'})
    assert response.status_code == 503
    assert 'secret' not in response.text


def test_provider_and_server_errors(monkeypatch):
    from openai import APIConnectionError
    import httpx
    for error, code in [(APIConnectionError(request=httpx.Request('POST', 'https://example.org')), 502), (RuntimeError('secret'), 500)]:
        def fail(q):
            raise error
        monkeypatch.setattr(service.rag, 'search', fail)
        response = client.post('/ask', json={'question': 'MPOC ?'})
        assert response.status_code == code
        assert 'secret' not in response.text


def test_missing_index_message(monkeypatch, tmp_path):
    monkeypatch.setattr(rag.config, 'INDEX', tmp_path / 'absent.json')
    response = client.post('/ask', json={'question': 'Définition MPOC ?'})
    assert response.status_code == 503
    assert 'scripts.build_index' in response.json()['detail']


def test_quota_and_connection_messages(monkeypatch):
    from openai import RateLimitError, APIConnectionError
    import httpx
    request = httpx.Request('POST', 'https://api.openai.com/v1/embeddings')
    errors = [
        (RateLimitError('secret', response=httpx.Response(429, request=request), body=None), 'quota'),
        (APIConnectionError(request=request), 'Connexion'),
    ]
    for error, expected in errors:
        def fail(question):
            raise error
        monkeypatch.setattr(service.rag, 'search', fail)
        response = client.post('/ask', json={'question': 'MPOC ?'})
        assert response.status_code == 502
        assert expected in response.json()['detail']
        assert 'secret' not in response.text


def test_generation_uses_low_reasoning_and_compact_context(monkeypatch):
    import json
    from types import SimpleNamespace
    from backend.app import llm

    def create(**kwargs):
        assert kwargs['reasoning'] == {'effort': 'low'}
        assert json.loads(kwargs['input'])['passages'] == [{'id': 1, 'text': PASSAGE['text']}]
        return SimpleNamespace(output_text='{"answer":"Texte", "source_ids":[1], "sufficient":true}',
                               usage=SimpleNamespace(input_tokens=10, output_tokens=10))

    monkeypatch.setattr(llm.config, 'LLM_MODEL', 'gpt-6-astra')
    monkeypatch.setattr(llm.config, 'LLM_REASONING_EFFORT', 'low')
    monkeypatch.setattr(llm, 'client', lambda: SimpleNamespace(responses=SimpleNamespace(create=create)))
    assert llm.generate('Définition MPOC ?', [PASSAGE])[0]['source_ids'] == [1]
