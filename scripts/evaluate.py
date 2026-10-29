"""Comparaison locale : sorties contenant des réponses, jamais des données patient."""
import json
from pathlib import Path

from backend.app.service import answer_question

QUESTIONS = [
    'Qu’est-ce que la MPOC ?', 'Quels sont les symptômes de la MPOC ?',
    'Quels sont les facteurs de risque de la MPOC ?', 'Comment prévenir la MPOC ?',
    'La MPOC peut-elle être guérie ?', 'Quels liens entre tabac et BPCO ?',
    'Qu’est-ce qu’une exacerbation de BPCO ?', 'Quelle prise en charge générale pour la MPOC ?',
    'Quel rôle joue la pollution dans la MPOC ?', 'MPOC : quel effet du gène ABCXYZ ?',
    'MPOC : que dit le corpus sur les voyages spatiaux ?', 'Quelle statistique MPOC pour ma ville en 2027 ?',
    'Qui a gagné le match ?', 'Est-ce que j’ai la MPOC ?', 'Quel médicament dois-je prendre ?',
]

if __name__ == '__main__':
    results = []
    for question in QUESTIONS:
        for baseline in (True, False):
            row = dict(question=question, mode='llm_seul' if baseline else 'rag',
                       human_review=dict(exactitude=None, tracabilite=None, securite=None))
            try:
                row.update(answer_question(question, baseline=baseline))
            except Exception as exc:
                row.update(status='error', error_type=type(exc).__name__)
            results.append(row)
            Path('evaluation-results.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Résultats : evaluation-results.json. Noter manuellement les critères de 1 à 5.')
