# Consigne initiale de conception et de génération du code

Ce fichier conserve la demande initiale utilisée pour cadrer et construire Souffle.
Le texte ci-dessous est reproduit sans réécriture. Les choix techniques et les
corrections ultérieures sont décrits dans le README et le rapport universitaire.
Cette consigne de développement est distincte du prompt système de l’application,
qui se trouve dans `backend/app/llm.py`.

---

Tu es un **Senior Software Engineer, Software Architect, AI Engineer et Product Designer UX/UI**.

Ta mission est de **concevoir et construire entièrement une application Web contextuelle sur la MPOC/BPCO**, en suivant les exigences fonctionnelles, techniques et académiques décrites ci-dessous.

Le projet doit rester volontairement **simple, compréhensible, maintenable et pédagogique**.

Je veux éviter toute architecture inutilement complexe.

L'application doit pouvoir être comprise, modifiée et maintenue par un **développeur junior**.

---

# 1. OBJECTIF DU PROJET

Construire une application Web permettant à un utilisateur de poser des questions concernant la **MPOC/BPCO — maladie pulmonaire obstructive chronique**.

L'application doit utiliser un **LLM associé à un système RAG** afin de générer des réponses basées uniquement sur des documents médicaux fiables présents dans le corpus documentaire.

L'application doit notamment permettre de poser des questions sur :

- la définition de la MPOC ;
- les symptômes ;
- les causes ;
- les facteurs de risque ;
- la prévention ;
- la prise en charge générale ;
- les informations générales présentes dans les documents fournis.

L'application ne doit pas :

- réaliser de diagnostic médical ;
- remplacer un professionnel de santé ;
- inventer une information absente du corpus ;
- produire volontairement une recommandation médicale personnalisée.

Lorsqu'une information n'est pas disponible dans les documents utilisés par le RAG, l'application doit le dire clairement.

---

# 2. PRINCIPE FONDAMENTAL

Le projet doit répondre au problème de la manière **la plus simple techniquement possible**.

Avant d'ajouter une technologie, demande-toi :

> Est-ce réellement nécessaire pour résoudre le problème ?

Si la réponse est non, ne l'utilise pas.

Évite notamment :

- les microservices ;
- Kubernetes ;
- Docker si cela ne facilite pas réellement le projet ;
- Redis ;
- Kafka ;
- architecture événementielle ;
- architecture distribuée ;
- Redux si inutile ;
- plusieurs backends ;
- plusieurs bases de données ;
- abstraction excessive ;
- design patterns inutiles ;
- frameworks complexes sans justification.

Je préfère :

**moins de technologies + meilleur code**

plutôt que :

**beaucoup de technologies + architecture difficile à maintenir**.

---

# 3. CHOIX DE LA STACK

Choisis toi-même les technologies les plus adaptées au projet.

Les critères de sélection sont, dans cet ordre :

1. simplicité ;
2. lisibilité ;
3. facilité d'installation ;
4. facilité de maintenance ;
5. documentation ;
6. compatibilité avec le RAG ;
7. intégration simple avec une API LLM ;
8. possibilité d'effectuer des tests ;
9. possibilité pour un étudiant ou développeur junior de comprendre le projet.

Avant de commencer le développement, présente brièvement :

- le frontend retenu ;
- le backend retenu ;
- le système RAG ;
- la solution d'embeddings ;
- l'index ou base vectorielle ;
- la bibliothèque de lecture des documents ;
- les outils de tests.

Pour chaque choix, explique en **1 ou 2 phrases maximum** pourquoi cette solution est utilisée.

Privilégie une stack légère.

Une architecture du type suivant est acceptable si elle constitue effectivement la solution la plus simple :

Frontend :
React / Vite

Backend :
Python + FastAPI

LLM :
API du modèle retenu

RAG :
Python

Vector store :
FAISS ou Chroma local

Tests :
Pytest

Mais tu n'es pas obligé de suivre exactement cette stack si tu identifies une solution plus simple et mieux adaptée.

---

# 4. ARCHITECTURE ATTENDUE

Je veux une architecture simple, idéalement :

```text
Utilisateur
    ↓
Interface Web
    ↓
Backend API
    ↓
Question utilisateur
    ↓
Recherche RAG
    ↓
Index vectoriel
    ↓
Documents MPOC
    ↓
Passages pertinents
    ↓
LLM
    ↓
Réponse contextualisée
    ↓
Sources
    ↓
Interface utilisateur
```

Sépare clairement :

- interface utilisateur ;
- logique métier ;
- système RAG ;
- accès au LLM ;
- gestion des documents ;
- configuration.

Ne mélange pas toutes les responsabilités dans un seul fichier.

---

# 5. STRUCTURE DU CODE

Le code doit être pensé pour un développeur junior.

Je veux :

- des fichiers courts ;
- des noms explicites ;
- des fonctions courtes ;
- peu de niveaux d'abstraction ;
- pas de duplication inutile ;
- une organisation logique des dossiers ;
- des commentaires uniquement lorsque cela apporte réellement quelque chose ;
- des messages d'erreur compréhensibles ;
- des constantes centralisées ;
- les secrets dans `.env`.

Ne crée pas de fonctions génériques extrêmement abstraites lorsque trois fonctions simples seraient plus faciles à comprendre.

Évite également les classes lorsque de simples fonctions suffisent.

---

# 6. ORGANISATION POSSIBLE

Cherche une structure proche de :

```text
project/
│
├── frontend/
│
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.*
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── routes/
│   │   ├── services/
│   │   │   ├── rag.py
│   │   │   ├── llm.py
│   │   │   └── documents.py
│   │   └── models/
│   │
│   ├── documents/
│   ├── vector_store/
│   └── tests/
│
├── .env.example
├── README.md
└── requirements.txt
```

La structure exacte peut être différente si tu trouves quelque chose de plus simple.

---

# 7. RAG

Le fonctionnement du RAG doit être transparent et facile à comprendre.

Pipeline :

1. importer les documents médicaux fiables ;
2. extraire leur texte ;
3. nettoyer le contenu ;
4. découper les documents en passages ;
5. conserver les métadonnées des sources ;
6. générer les embeddings ;
7. enregistrer les embeddings dans un index vectoriel local ;
8. transformer la question utilisateur en embedding ;
9. rechercher les passages les plus proches ;
10. envoyer uniquement les passages pertinents au LLM ;
11. générer la réponse ;
12. afficher la réponse et les sources.

Chaque passage doit idéalement conserver :

- nom du document ;
- titre ;
- section ;
- numéro de page si disponible ;
- URL ou référence de la source si disponible.

---

# 8. RÈGLE ANTI-HALLUCINATION

Le LLM doit recevoir une instruction stricte :

Répondre principalement ou uniquement à partir du contexte documentaire fourni.

Si le contexte est insuffisant, répondre clairement qu'il n'existe pas suffisamment d'informations dans les documents disponibles.

Ne jamais inventer une source.

Ne jamais prétendre qu'une information provient d'un document lorsqu'elle n'y apparaît pas.

---

# 9. QUESTIONS HORS SUJET

L'application doit reconnaître trois situations principales.

### Question valide

Exemple :

> Quels sont les symptômes fréquents de la MPOC ?

→ effectuer le RAG et répondre.

### Information inexistante

Exemple :

> Quel est exactement le meilleur traitement pour mon cas personnel ?

Si cette information n'existe pas dans les documents :

→ expliquer que le corpus disponible ne permet pas de répondre correctement.

### Demande médicale personnalisée

Exemple :

> J'ai mal à la poitrine et je respire mal, quel médicament dois-je prendre ?

→ ne pas fournir de diagnostic ni prescription.

Afficher un message prudent invitant l'utilisateur à contacter un professionnel de santé.

---

# 10. INTERFACE UTILISATEUR

Je veux une interface :

- très simple ;
- premium ;
- moderne ;
- élégante ;
- rassurante ;
- accessible ;
- sans surcharge visuelle.

Inspiration :

- Apple ;
- Notion ;
- Linear ;
- interfaces modernes minimalistes.

Ne copie directement aucune de ces interfaces.

Utilise seulement leurs principes de design.

---

# 11. STYLE VISUEL

Design :

- beaucoup d'espace blanc ;
- typography propre ;
- excellente hiérarchie visuelle ;
- couleurs sobres ;
- cartes légèrement arrondies ;
- bordures fines ;
- ombres très légères ;
- animations discrètes ;
- boutons simples ;
- icônes cohérentes ;
- interface responsive.

Pas de :

- gros gradients agressifs ;
- néons ;
- animations inutiles ;
- dashboard surchargé ;
- dizaines de couleurs ;
- éléments purement décoratifs.

Le design doit donner une impression de :

**calme + sérieux + santé + technologie moderne.**

---

# 12. PAGE PRINCIPALE

L'écran principal doit être immédiatement compréhensible.

Il peut contenir :

### Header

Logo ou nom de l'application.

Petit sous-titre :

> Assistant d'information sur la MPOC basé sur des sources documentaires.

### Zone principale

Titre :

> Comment puis-je vous aider ?

Sous-titre :

> Posez une question concernant la MPOC.

Champ de saisie.

Bouton :

> Poser ma question

Quelques suggestions :

- Qu'est-ce que la MPOC ?
- Quels sont ses symptômes ?
- Quels sont les facteurs de risque ?
- Comment peut-on prévenir la MPOC ?

---

# 13. AFFICHAGE DES RÉPONSES

Une réponse doit être structurée proprement.

Exemple :

```text
Réponse

La MPOC est une maladie respiratoire chronique...

Sources utilisées

1. Organisation mondiale de la Santé
2. Document X — page 4

Important

Cette application fournit des informations générales et ne remplace pas l'avis d'un professionnel de santé.
```

Les sources doivent être facilement visibles.

---

# 14. UX

Prévoir les états suivants :

- question vide ;
- chargement ;
- réponse réussie ;
- aucune source trouvée ;
- erreur réseau ;
- erreur API ;
- question hors sujet ;
- erreur serveur.

Ne jamais laisser simplement l'utilisateur devant :

```text
Error 500
```

Afficher plutôt une formulation comme :

> Une erreur est survenue pendant la génération de la réponse. Veuillez réessayer.

---

# 15. LOADING

Pendant la génération :

afficher une animation sobre accompagnée par exemple de :

> Recherche des informations pertinentes…

Puis :

> Préparation de la réponse…

Évite les loaders trop complexes.

---

# 16. RESPONSIVE DESIGN

L'application doit fonctionner correctement sur :

- ordinateur ;
- tablette ;
- téléphone.

Commence par une interface desktop propre mais assure également une bonne adaptation mobile.

---

# 17. ACCESSIBILITÉ

Prévoir :

- contraste lisible ;
- taille de police correcte ;
- navigation clavier ;
- labels des champs ;
- boutons explicites ;
- états focus visibles ;
- HTML sémantique lorsque possible.

---

# 18. SÉCURITÉ

La clé API ne doit jamais être exposée dans le frontend.

Elle doit rester côté backend.

Utiliser :

```env
OPENAI_API_KEY=...
```

ou l'équivalent correspondant au fournisseur choisi.

Ajouter :

```text
.env
```

au `.gitignore`.

Créer :

```text
.env.example
```

sans vraie clé.

Ajouter également :

- validation des entrées ;
- taille maximale raisonnable des questions ;
- gestion des erreurs ;
- protection basique contre les entrées incorrectes ;
- CORS correctement configuré.

N'implémente pas un système de sécurité extrêmement complexe si le prototype ne le justifie pas.

---

# 19. DONNÉES PERSONNELLES

Le prototype ne doit pas nécessiter de compte utilisateur.

Ne stocke pas de dossier médical.

Ne stocke pas d'informations patient.

Ne construis pas inutilement :

- système d'inscription ;
- authentification ;
- profil patient ;
- historique médical.

Le corpus documentaire doit être séparé des éventuelles questions utilisateurs.

---

# 20. API

Créer des endpoints simples.

Par exemple :

```text
GET /health
POST /ask
```

`POST /ask`

Entrée :

```json
{
  "question": "Quels sont les symptômes de la MPOC ?"
}
```

Sortie :

```json
{
  "answer": "...",
  "sources": [
    {
      "title": "...",
      "page": 4
    }
  ]
}
```

N'ajoute d'autres endpoints que lorsqu'ils sont réellement nécessaires.

---

# 21. PROMPT SYSTÈME DU LLM

Construire un prompt système robuste.

Il doit préciser notamment :

- le rôle de l'assistant ;
- l'utilisation obligatoire du contexte fourni ;
- l'interdiction d'inventer des sources ;
- l'interdiction de diagnostiquer ;
- l'interdiction de prescrire un traitement ;
- la nécessité de reconnaître l'incertitude ;
- l'obligation d'indiquer quand les informations sont insuffisantes ;
- le format attendu de la réponse.

Le prompt doit rester lisible.

---

# 22. TESTS

Le projet doit être suffisamment testé.

Préparer des tests pour :

### Fonctionnement général

- API accessible ;
- question valide ;
- réponse générée ;
- sources présentes.

### Validation

- question vide ;
- question trop longue ;
- mauvais format.

### RAG

- récupération des passages ;
- pertinence des documents ;
- absence de documents pertinents.

### Sécurité médicale

Tester notamment :

> Quel médicament dois-je prendre ?

> Est-ce que j'ai la MPOC ?

> J'ai du mal à respirer, que dois-je faire ?

L'application doit éviter le diagnostic personnalisé.

---

# 23. EXPÉRIENCE AVEC ET SANS RAG

Le projet universitaire demande également d'évaluer l'intérêt du RAG.

Prévois donc une façon très simple, réservée au développement ou aux tests, de comparer :

```text
LLM seul
```

et

```text
LLM + RAG
```

Cette fonction ne doit pas compliquer l'interface utilisateur principale.

Elle peut être implémentée dans :

- un endpoint de test ;
- un script ;
- une page développement ;
- ou les tests automatisés.

Choisis la solution la plus simple.

---

# 24. MÉTRIQUES

Lorsque cela est raisonnablement possible, mesure :

- temps de réponse ;
- nombre de passages retrouvés ;
- sources utilisées ;
- succès ou échec ;
- erreurs rencontrées.

Si l'API permet facilement d'obtenir la consommation de tokens, conserve également :

- tokens entrée ;
- tokens sortie ;
- estimation du coût.

Ne construis pas une plateforme complète d'observabilité.

Un logging simple suffit.

---

# 25. QUALITÉ DU CODE

La qualité du logiciel sera évaluée notamment selon :

- exactitude fonctionnelle ;
- maintenabilité ;
- lisibilité ;
- organisation ;
- documentation ;
- gestion des erreurs ;
- sécurité ;
- performance.

Je veux donc que chaque choix soit cohérent avec ces critères.

---

# 26. README

Créer un README extrêmement clair.

Il doit expliquer :

1. le projet ;
2. l'architecture ;
3. les prérequis ;
4. l'installation ;
5. la création de `.env` ;
6. l'ajout des documents ;
7. la création de l'index vectoriel ;
8. le lancement du backend ;
9. le lancement du frontend ;
10. l'exécution des tests ;
11. la structure du projet.

Un étudiant doit pouvoir récupérer le dépôt et lancer le projet sans devoir comprendre toute l'architecture au préalable.

---

# 27. COMMENT TU DOIS TRAVAILLER

Ne génère pas immédiatement des dizaines de fichiers.

Procède dans cet ordre.

### Étape 1 — Analyse

Résume :

- problème ;
- exigences ;
- contraintes ;
- fonctionnalités.

### Étape 2 — Stack

Propose la stack minimale.

### Étape 3 — Architecture

Présente l'architecture des composants.

### Étape 4 — Structure

Montre l'arborescence du projet.

### Étape 5 — MVP

Construis d'abord le parcours essentiel :

```text
Question
→ RAG
→ LLM
→ Réponse
→ Sources
```

### Étape 6 — Interface

Ajoute ensuite l'interface premium et responsive.

### Étape 7 — Gestion des erreurs

Ajoute les cas limites.

### Étape 8 — Tests

Crée les tests.

### Étape 9 — Documentation

Termine par le README et les instructions.

---

# 28. RÈGLE DE MODIFICATION

Lorsque tu modifies du code existant :

1. lis d'abord les fichiers concernés ;
2. comprends ce qui existe ;
3. ne réécris pas tout le projet sans nécessité ;
4. effectue la plus petite modification propre permettant de résoudre le problème ;
5. vérifie que tu n'as pas cassé une autre fonctionnalité.

---

# 29. RÈGLE DE SIMPLICITÉ

À chaque décision technique, préfère :

```text
solution simple
```

à

```text
solution impressionnante mais complexe.
```

Par exemple :

Préférer :

```python
def search_documents(question):
    ...
```

à une architecture avec cinq interfaces, trois classes abstraites et plusieurs factories si elles n'apportent aucune valeur réelle.

---

# 30. STYLE DU CODE

Le code doit avoir l'air d'avoir été écrit par un bon développeur humain.

Je ne veux pas :

- commentaires sur chaque ligne ;
- noms de variables vagues ;
- fonctions gigantesques ;
- abstraction prématurée ;
- architecture enterprise ;
- duplication ;
- centaines de fichiers minuscules ;
- logique cachée inutilement.

Je veux :

```text
simple
clair
prévisible
testable
documenté
maintenable
```

---

# 31. CRITÈRE DE DÉCISION PRINCIPAL

Lorsqu'il existe plusieurs façons de réaliser une fonctionnalité, utilise cette question :

> Quelle solution permet à un développeur junior de comprendre le fonctionnement du projet le plus rapidement tout en conservant une bonne qualité logicielle ?

Cette solution doit généralement être privilégiée.

---

# 32. RÉSULTAT FINAL ATTENDU

À la fin, je dois disposer d'une application fonctionnelle dans laquelle :

```text
Utilisateur
        ↓
pose une question
        ↓
le système analyse la question
        ↓
le RAG recherche les documents MPOC
        ↓
les meilleurs passages sont sélectionnés
        ↓
le LLM reçoit uniquement le contexte pertinent
        ↓
une réponse claire est produite
        ↓
les sources sont affichées
        ↓
un avertissement médical est présenté
```

Le tout avec :

- une interface premium mais minimaliste ;
- une architecture simple ;
- un code lisible ;
- un backend compréhensible ;
- un RAG transparent ;
- des tests ;
- une documentation claire ;
- une installation facile ;
- aucune complexité inutile.

---

# 33. IMPORTANT

Tu as le droit de remettre en question mes choix techniques.

Si une technologie que je demande :

- complique inutilement le projet ;
- crée trop de dépendances ;
- rend le code difficile à comprendre ;
- n'apporte pas de bénéfice concret ;

propose une alternative plus simple.

Ne cherche pas à impressionner par la complexité.

Cherche à construire **la solution la plus simple, la plus propre et la plus professionnelle permettant de résoudre correctement le problème.**

Commence maintenant par :

1. résumer ce que tu dois construire ;
2. proposer la stack minimale ;
3. justifier chaque choix ;
4. proposer l'architecture ;
5. proposer l'arborescence ;
6. puis commencer immédiatement la construction du MVP.