"""Ajoute uniquement une notice au texte initial conservé dans le dépôt."""
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'PROMPT_INITIAL_GENERATION_CODE.md'
text = path.read_text(encoding='utf-8-sig')
heading = '# Consigne initiale de conception et de génération du code'
if not text.startswith(heading):
    notice = '''# Consigne initiale de conception et de génération du code

Ce fichier conserve la demande initiale utilisée pour cadrer et construire Souffle.
Le texte ci-dessous est reproduit sans réécriture. Les choix techniques et les
corrections ultérieures sont décrits dans le README et le rapport universitaire.
Cette consigne de développement est distincte du prompt système de l’application,
qui se trouve dans `backend/app/llm.py`.

---

'''
    path.write_text(notice + text, encoding='utf-8')
