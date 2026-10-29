# Souffle — Assistant documentaire MPOC/BPCO

Prototype universitaire francophone : question → embeddings → passages pertinents → LLM → réponse et sources. L’interface est responsive, accessible au clavier et ne nécessite ni compte ni compilation. Aucun historique de questions n’est conservé par l’application.

## Démarrage 

**Commencez par le [guide d’installation pas à pas](GUIDE_INSTALLATION.md).**

1. Installez Python stable 3.13 et téléchargez ce dépôt avec **Code → Download ZIP**, puis **Extraire tout**.
2. Double-cliquez sur **INSTALLER_SOUFFLE.bat** : les composants sont installés, la clé API est demandée si nécessaire et les documents sont préparés après votre accord.
3. Double-cliquez sur **DEMARRER_SOUFFLE.bat** : le navigateur s’ouvre automatiquement. Gardez la fenêtre ouverte ; **Ctrl+C** arrête le serveur.

Un compte API OpenAI avec crédits et accès au modèle est nécessaire. L’installation guidée ne crée aucun compte et n’ajoute aucun moyen de paiement. La clé reste dans `.env` et n’est pas affichée pendant sa saisie. Ne publiez jamais ce fichier sur GitHub.

La consigne initiale est conservée dans [PROMPT_INITIAL_GENERATION_CODE.md](PROMPT_INITIAL_GENERATION_CODE.md). La suite du README détaille l’installation manuelle et l’architecture pour les développeurs.

## Choix et architecture

Les versions vérifiées sont figées dans `requirements-lock.txt`. `requirements.txt` décrit les dépendances directes. Voir [VERIFICATION.md](VERIFICATION.md) pour les résultats et limites de vérification.

HTML/CSS/JavaScript natifs pour une interface à un écran ; FastAPI pour l’API et la validation ; OpenAI pour les embeddings et GPT‑6 Astra, modèle provisoire du rapport ; NumPy pour un index vectoriel local en JSON. Aucun framework RAG, serveur de base de données ou service supplémentaire.

```text
Navigateur (frontend/) — même origine
  POST /ask → validation → contrôle médical / sujet
    → embedding de la question → similarité cosinus
    → passages au-dessus du seuil → Responses API
    → contrôle des identifiants cités → réponse + extraits + sources
```

Le rapport UQAC est une référence de cadrage académique, pas une source médicale indexée. Une copie complétée est fournie dans `rapport/`. Le fine-tuning reste hors de ce MVP ; aucune validation clinique n’est prétendue.

## Installation Windows PowerShell

Prérequis : Python stable 3.11 à 3.13 (3.13 conseillé), accès réseau pour installer les paquets, compte API OpenAI avec accès au modèle configuré et facturation active. Un abonnement ChatGPT ne remplace pas une clé API. Éviter le Python 3.14 bêta présent sur cette machine, incompatible avec les dépendances installées.

Depuis le dossier du projet :

```powershell
py -3.13 -m venv .venv313
.\.venv313\Scripts\python -m pip install -r requirements-lock.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
```

Ouvrir `.env` dans un éditeur et renseigner `OPENAI_API_KEY`. Ne jamais partager ce fichier ni placer la clé dans `frontend/`. `LLM_MODEL=gpt-6-astra` suit le rapport ; le nom reste configurable selon votre accès API. Les tarifs facultatifs permettent une estimation en USD, hors embeddings. Sans tarifs renseignés, le coût vaut `null`, pas zéro.

## Corpus et index

Si l’indexation échoue, lancer `.\.venv313\Scripts\python -m scripts.check_connection` : ce diagnostic vérifie DNS et HTTPS sans transmettre la clé. Un HTTP 401 y est normal. Une erreur OpenAI 429 liée au quota exige de vérifier le solde et la facturation du projet API ; redémarrer le serveur ne rétablit pas les crédits. Après rechargement, relancer l’indexation. Aucun index fictif n’est créé en cas d’échec.

Le corpus initial est une courte synthèse pédagogique reformulée de la [fiche OMS BPCO](https://www.who.int/fr/news-room/fact-sheets/detail/chronic-obstructive-pulmonary-disease-(copd)), consultée le 27 octobre 2026. Sa couverture est limitée ; le seuil de recherche doit être évalué sur un corpus plus complet.

1. Ajouter des fichiers `.pdf`, `.docx`, `.md` ou `.txt` en UTF‑8 dans `backend/documents/`.
2. Vérifier leur fiabilité, leur actualité, leur contenu et le droit d’utilisation. Ne pas ajouter de dossiers patients. Les documents sont des données : leurs éventuelles instructions ne doivent pas être suivies par le modèle.
3. Ajouter un fichier de métadonnées de même nom suivi de `.json`, par exemple `guide.pdf.json` :

```json
{"title": "Titre exact du guide", "url": "https://institution.example/guide", "approved": true, "reviewed_on": "2026-10-27"}
```

`approved=true` constitue une validation manuelle par le responsable du corpus, pas une certification automatique. Les PDF conservent les pages ; les DOCX/TXT n’inventent pas de pagination. Les titres Markdown servent de sections. Les scans PDF nécessitent un OCR externe préalable. Le découpage utilise des passages de 1 000 caractères, avec chevauchement de 150 caractères.

```powershell
.\.venv313\Scripts\python -m scripts.build_index
```

Cette commande envoie le texte du corpus à l’API d’embeddings et engendre des frais. L’index local conserve les passages et leurs vecteurs. Reconstruire après toute modification du corpus ou du modèle d’embeddings, puis redémarrer le serveur. Ne pas modifier les documents pendant une indexation.

## Lancement

```powershell
.\.venv313\Scripts\python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Ouvrir **http://127.0.0.1:8000**. FastAPI sert directement le frontend : pas de deuxième commande ni de CORS permissif. La documentation API est disponible à `/docs` ; `GET /health` distingue disponibilité du serveur, présence de l’index et présence d’une clé. Ces indicateurs ne vérifient pas les droits API à distance.

```powershell
Invoke-RestMethod http://127.0.0.1:8000/ask -Method Post -ContentType 'application/json; charset=utf-8' -Body '{"question":"Quels sont les symptômes de la MPOC ?"}'
```

`POST /ask` accepte uniquement une chaîne `question` de 1 à 1 000 caractères. La réponse comprend `answer`, `status`, `sources`, `disclaimer`, `metrics`. Statuts métier : `answered`, `insufficient`, `medical`, `off_topic`. Erreurs : 422 validation, 503 configuration/index, 502 fournisseur, 500 serveur. Les détails internes ne sont pas retournés.

## Tests et comparaison académique

### Temps de réponse

Les quatre questions publiques proposées par l’interface sont vectorisées à l’indexation. Leur recherche ne nécessite donc plus d’appel réseau aux embeddings ; les autres questions conservent leur recherche vectorielle normale. Les réponses ne sont pas mises en cache. Reconstruire l’index pour activer cette optimisation sur un ancien index.

Le corpus comprend maintenant des synthèses françaises supplémentaires des pages NHLBI sur la définition, les symptômes, les causes, le diagnostic et la prise en charge. Elles ont été rapprochées des pages officielles, sans revue clinique indépendante. Elles élargissent la couverture mais ne remplacent pas des recommandations médicales complètes. Les limites de couverture restent applicables.

Le client OpenAI réutilise ses connexions HTTP. Pour Astra, `LLM_REASONING_EFFORT=low` réduit l’effort de raisonnement ; le modèle reste configurable. Le contexte envoyé au modèle contient seulement les identifiants et textes des passages, et le prompt demande des réponses concises. Les métriques `retrieval_ms` et `generation_ms` séparent les délais de recherche (dont l’appel embeddings) et de génération. Deux appels réseau restent nécessaires ; leur durée dépend du fournisseur et du réseau. Aucun cache de questions personnelles n’est conservé.

```powershell
.\.venv313\Scripts\python -m pytest backend/tests -q
.\.venv313\Scripts\python -m scripts.evaluate
```

Les tests utilisent des réponses et embeddings simulés : ils sont gratuits et fonctionnent sans clé. Ils vérifient validation, parcours complet, citations invalides, recherche pertinente ou vide, métadonnées, refus médicaux et erreurs. Ils ne mesurent pas la qualité réelle du modèle.

Le script d’évaluation nécessite une clé et un index. Il compare les mêmes 15 questions avec et sans RAG ; les mêmes garde-fous précèdent les deux modes. Il produit `evaluation-results.json` avec réponses, extraits, temps, jetons et champs de notation humaine. Les erreurs sont identifiées par type ; aucun score ni résultat favorable n’est inventé. Il peut effectuer jusqu’à 30 générations payantes. Utiliser uniquement les questions synthétiques du script.

Pour le rapport : noter de 1 à 5 exactitude, traçabilité et sécurité après comparaison avec les documents ; consigner modèle, corpus, seuil, date et environnement. Évaluer aussi les refus injustifiés et les questions sans réponse. Les temps incluent recherche et génération ; les jetons indiqués sont ceux de la génération, pas ceux de l’indexation. Les journaux du serveur ne contiennent que statut, métriques et types d’erreur.

## Limites et confidentialité

Le prompt et les contrôles de citations réduisent certains risques mais ne garantissent ni absence d’hallucinations ni exactitude clinique. Le serveur vérifie les identifiants de sources ; il ne prouve pas que chaque phrase découle des passages. La relecture humaine reste nécessaire.

Le filtre médical et le filtre de sujet sont volontairement simples : variantes linguistiques et formulations ambiguës peuvent être mal reconnues. L’absence de terme MPOC/BPCO ou respiratoire peut demander une reformulation. Chaque question est indépendante, sans mémoire conversationnelle.

Les questions et les extraits pertinents sont transmis au fournisseur OpenAI. `store=False` désactive le stockage des réponses via Responses ; les conditions de conservation et de traitement du fournisseur continuent de s’appliquer. L’application ne journalise pas le texte des questions. L’évaluation, exécutée explicitement, enregistre ses questions synthétiques et réponses localement.

Le prototype est destiné au développement local. Avant toute exposition publique : revue de confidentialité et du corpus, validation médicale, limitation de débit et de coûts, HTTPS et configuration de l’hébergement. Une publication statique seule ne pourrait pas héberger ce backend Python.

## Structure

```text
frontend/                 interface, styles, requêtes et affichage sécurisé
backend/app/
  main.py                routes, validation et fichiers statiques
  config.py              paramètres centralisés
  documents.py           extraction, sections et métadonnées
  rag.py                 création de l’index et similarité cosinus
  llm.py                 embeddings, prompt et accès OpenAI
  safety.py              refus médicaux et questions hors sujet
  service.py             orchestration et métriques
backend/documents/       corpus approuvé et métadonnées
backend/vector_store/    index généré, ignoré par Git
backend/tests/           tests sans appels externes
scripts/build_index.py   indexation explicite
scripts/evaluate.py      comparaison universitaire hors interface
.env.example             configuration sans secret
requirements.txt         dépendances avec bornes majeures
```

Références techniques : [modèle](https://developers.openai.com/api/docs/models/gpt-6-astra), [embeddings](https://developers.openai.com/api/docs/guides/embeddings), [génération de texte](https://developers.openai.com/api/docs/guides/text).
