"""Complète la copie du rapport en conservant ses styles et ses premiers chapitres."""
from copy import deepcopy
from pathlib import Path
import re

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor
from docx.text.paragraph import Paragraph

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(r'C:\Users\HP\Downloads\Rapport_Projet_Stage_UQAC.docx')
OUTPUT = ROOT / 'rapport/Rapport_Projet_Stage_UQAC_complete.docx'

CONTENT = {
'4.1': [
"L’étude de cas a été réalisée sous Windows avec Python 3.13 stable. Une première tentative avec Python 3.14 bêta a révélé une incompatibilité avec les dépendances de validation. L’environnement a donc été remplacé par une version stable afin de rendre les essais reproductibles.",
"J’ai retenu une architecture volontairement simple. L’interface utilise HTML, CSS et JavaScript, tandis que FastAPI assure le traitement des requêtes et sert les fichiers de l’interface. NumPy permet de rechercher les passages dans un index vectoriel local enregistré en JSON. La lecture des PDF et des fichiers Word repose respectivement sur pypdf et python-docx. Les fichiers Markdown et texte sont également acceptés.",
"L’application utilise l’API OpenAI pour produire les embeddings avec text-embedding-3-small et générer les réponses avec le modèle configuré gpt-6-astra. Les versions des dépendances vérifiées sont conservées dans requirements-lock.txt. Les tests sont exécutés avec pytest. Aucun serveur de base de données, conteneur ou framework RAG supplémentaire n’a été ajouté."
],
'4.2': [
"Le développement a été réalisé avec l’aide de l’assistant Codex à partir d’une consigne détaillant le fonctionnement attendu, les limites médicales, la structure du code et le style de l’interface. Cette consigne initiale est conservée dans PROMPT_INITIAL_GENERATION_CODE.md afin de garder une trace de la demande ayant guidé la génération du code.",
"Le travail a été effectué progressivement : création du parcours question–recherche–réponse, ajout de l’interface, gestion des erreurs, puis correction des problèmes observés. Les premières versions ont notamment présenté des refus injustifiés de questions générales et un échec de connexion pendant la création de l’index. Ces problèmes ont conduit à modifier le filtre et à distinguer les erreurs réseau, les erreurs de clé et les erreurs de quota.",
"Le nom du modèle configuré dans l’application ne prouve pas, à lui seul, que ce même modèle a généré chaque partie du code dans l’assistant de développement. GPT-6 Astra est bien le modèle demandé à l’API pour les réponses de l’application. L’identité exacte du modèle de génération du code doit être établie à partir des informations de la session Codex pour répondre complètement à l’objectif de traçabilité du projet.",
"Le code produit a été vérifié par des tests et des essais locaux. Les clés API sont conservées dans .env, qui est exclu du dépôt Git. La consigne initiale et le prompt système de l’application sont deux éléments distincts : la première guide le développement, tandis que le second encadre chaque réponse produite à l’utilisateur."
],
'4.3': [
"L’application réalisée, appelée Souffle, présente une page permettant de poser une question sur la MPOC. Elle comprend un champ de saisie, un bouton d’envoi et quatre suggestions de questions. Sur ordinateur, ces suggestions sont placées à gauche du formulaire ; sur un écran plus étroit, elles sont affichées en dessous. La réponse est présentée dans une carte verte accompagnée des sources et de l’avertissement médical.",
"L’utilisateur peut consulter le titre de chaque source, la section concernée, le numéro de page lorsqu’il existe et le passage retenu. Les contenus reçus sont affichés comme du texte afin d’éviter l’exécution de code HTML provenant d’une réponse ou d’un document.",
"L’interface prévoit les états de chargement, de question vide, d’information insuffisante et d’erreur. Elle ne demande aucun compte et ne conserve pas d’historique de questions. Le champ est limité à 1 000 caractères. Des labels, des indications de focus et des messages accessibles ont été ajoutés ; leur présence dans le code ne remplace toutefois pas un audit complet d’accessibilité.",
"Pour faciliter la distribution, deux fichiers de lancement Windows ont été ajoutés. INSTALLER_SOUFFLE.bat prépare l’environnement, installe les composants et guide la configuration de la clé. DEMARRER_SOUFFLE.bat lance ensuite le serveur et ouvre le navigateur. GUIDE_INSTALLATION.md explique ces étapes pour une personne qui ne programme pas."
],
'4.4': [
"Le serveur expose principalement GET /health et POST /ask. Le premier indique si le service est disponible, si la clé est renseignée et si un index existe. Le second reçoit la question, applique les contrôles prévus et orchestre la recherche documentaire et la génération. La clé reste du côté du serveur et n’est jamais placée dans les fichiers JavaScript de l’interface.",
"Le prompt système impose une réponse en français fondée sur les passages transmis. Il interdit les sources inventées, le diagnostic et la prescription individuels. Il demande également de distinguer une demande personnelle de décision médicale d’une simple question générale formulée à la première personne. Lorsqu’une partie de la question peut être documentée, le modèle doit expliquer cette partie et indiquer la limite restante.",
"Le modèle retourne une réponse, les identifiants des passages cités et un indicateur de suffisance. Le serveur vérifie que ces identifiants appartiennent aux passages fournis. Une référence inconnue ou une réponse sans source exploitable entraîne un message d’information insuffisante. Ce contrôle vérifie la provenance déclarée, mais ne garantit pas que chaque affirmation est effectivement démontrée par le passage.",
"Le client OpenAI réutilise ses connexions. L’effort de raisonnement d’Astra est réglé sur low afin de limiter le travail demandé au modèle pour ce prototype documentaire. Les journaux consignent les temps de recherche et de génération, les jetons et le statut, sans enregistrer le texte des questions. Les appels utilisent store=False ; les conditions de traitement du fournisseur continuent néanmoins de s’appliquer."
],
'4.5': [
"Le premier corpus contenait quatre courts passages provenant d’une synthèse pédagogique de la fiche OMS. Sa couverture limitée produisait des réponses peu développées. Il a été enrichi avec des synthèses françaises de cinq pages du NHLBI portant sur la définition, les symptômes, les causes, le diagnostic et la prise en charge. L’index reconstruit contient 17 passages. Ces synthèses ont été rapprochées des pages institutionnelles, sans validation clinique indépendante.",
"L’indexation extrait le texte, nettoie les espaces et découpe les contenus en passages d’au plus 1 000 caractères, avec un chevauchement de 150 caractères lorsque la longueur l’exige. Chaque passage conserve son document, son titre, sa section, sa page éventuelle et son URL. Un fichier de métadonnées doit porter approved=true avant que le document soit accepté ; cette valeur représente une décision de validation documentaire et non une certification automatique.",
"Les embeddings des passages sont normalisés puis enregistrés dans un index local. À la recherche, la similarité cosinus est calculée entre le vecteur de la question et ceux des passages. Le système retient au maximum quatre passages dépassant le seuil configuré de 0,35. Ce seuil reste à calibrer sur un jeu de questions représentatif.",
"Les quatre suggestions publiques de l’interface sont vectorisées dès l’indexation. Une question correspondant à l’une de ces suggestions peut ainsi être recherchée sans nouvel appel réseau aux embeddings. Les autres questions suivent le parcours normal. Aucun cache de questions personnelles ou de réponses utilisateur n’a été ajouté.",
"Une empreinte du corpus permet de détecter un ajout ou une modification de document. Le système demande alors de reconstruire l’index. Un PDF numérisé sans texte nécessite une reconnaissance de caractères préalable, qui n’est pas intégrée au prototype."
],
'4.6': [
"Le fine-tuning n’a pas été mis en œuvre dans cette étude de cas. Le modèle GPT-6 Astra utilisé par l’application ne propose pas cette fonctionnalité dans la documentation consultée. L’adaptation repose donc sur le corpus, la recherche documentaire et les consignes du prompt système (OpenAI, s. d.).",
"La méthode LoRA présentée dans la partie théorique demeure une possibilité pour un autre modèle compatible. Elle demanderait des données d’entraînement validées, un protocole de comparaison et des ressources supplémentaires. Aucun résultat de fine-tuning n’est inclus dans les mesures du prototype."
],
'5.1': [
"La vérification distingue les tests automatisés du logiciel et les essais réels avec l’API. Les premiers utilisent des embeddings et des réponses simulés afin de contrôler le comportement de l’application sans coût d’appel. Les seconds permettent d’observer le fonctionnement du fournisseur et les temps de réponse, mais restent trop limités pour constituer une validation médicale.",
"La suite de tests de l’application comporte 45 cas réussis avant l’ajout de l’installation guidée. Elle couvre la validation des entrées, les sources, la recherche vectorielle, les erreurs et les refus médicaux. Deux tests supplémentaires ont été préparés pour la sauvegarde de la clé par l’assistant d’installation. Les résultats de cette nouvelle exécution sont consignés dans le fichier de vérification du dépôt.",
"Un script distinct prépare quinze questions pour comparer le LLM seul et le LLM associé au RAG : neuf questions générales, trois questions imprécises ou absentes du corpus et trois questions hors sujet ou personnelles. Il enregistre les réponses et des champs de notation humaine de 1 à 5. Cette comparaison complète n’a pas encore été exécutée et notée.",
"Les catégories de vérification restent celles du plan suivant. La réussite technique d’un test est distinguée de l’évaluation documentaire de l’exactitude et de la prudence d’une réponse."
],
'5.2': [
"Les essais automatisés ont vérifié l’accès à l’interface, au service de santé et aux ressources nécessaires, dont le favicon. Ils vérifient également qu’une question valide peut conduire à une réponse contenant des sources. Les questions vides, composées seulement d’espaces, trop longues ou présentées dans un format incorrect sont rejetées avec un message compréhensible.",
"Les erreurs ont été séparées selon leur origine. Une configuration ou un index absent donne un statut 503 ; un problème du fournisseur donne un statut 502 ; une erreur inattendue du serveur donne un statut 500 accompagné d’un message général. Les détails sensibles des exceptions ne sont pas retournés à l’interface.",
"Un essai HTTP local a confirmé l’accès à la page et au service /health. L’absence d’index entraînait bien un message de préparation manquante, tandis qu’une demande de diagnostic était refusée avant l’appel au modèle. Les vérifications visuelles complètes sur ordinateur, tablette et téléphone restent à réaliser dans un navigateur."
],
'5.3': [
"La vérification du code a porté sur la séparation des responsabilités, la compilation des modules Python, la syntaxe JavaScript et la cohérence des dépendances. La commande pip check n’a signalé aucune dépendance cassée. Un avertissement de dépréciation lié à l’utilisation de httpx par l’outil de test Starlette demeure ; il n’a pas entraîné d’échec de test.",
"L’organisation du code permet d’identifier séparément la configuration, la lecture des documents, le RAG, l’accès au modèle, le filtre médical et l’orchestration. Le frontend ne contient aucune clé API. Les questions ne sont pas écrites dans les journaux et aucun dossier patient n’est enregistré par le prototype.",
"Ces vérifications ne constituent pas un audit de sécurité complet ni une mesure indépendante de maintenabilité. Avant une mise en ligne publique, des contrôles supplémentaires seraient nécessaires, notamment pour limiter les appels, maîtriser les coûts et protéger le service. La distribution sur GitHub correspond ici à la publication du code, et non à l’hébergement public de l’application."
],
'5.4': [
"Les premiers essais ont mis en évidence des refus injustifiés. Une expression trop large reconnaissait « est-ce que » dans « Qu’est-ce que la MPOC ? » et déclenchait un refus médical. D’autres règles bloquaient des demandes générales contenant « je » ou « mon ». Les règles ont été resserrées et des tests de régression ont été ajoutés.",
"Les questions « Qu’est-ce que la MPOC ? », « J’ai la MPOC, quels sont les symptômes fréquents ? » et « Mon père a la BPCO, qu’est-ce que la réadaptation pulmonaire ? » sont désormais orientées vers le RAG. À l’inverse, « Ai-je la BPCO ? » et « Quelle dose prendre pour ma BPCO ? » restent des demandes de décision individuelle et sont refusées.",
"Un appel réel sur la définition de la MPOC a produit une réponse documentaire avec trois passages cités après enrichissement du corpus. Ce résultat montre le fonctionnement de la chaîne complète, sans démontrer à lui seul l’exactitude de toutes les réponses. L’évaluation qualitative sur les quinze questions nécessite encore une lecture comparative des sources par une personne compétente."
],
'5.5': [
"Les tests du RAG contrôlent la sélection d’un passage proche, l’exclusion de passages sous le seuil, l’absence de génération lorsque la recherche ne fournit aucun contexte et le rejet d’une citation inconnue. Ils vérifient aussi la conservation des métadonnées, l’obligation d’approbation documentaire et la détection d’un corpus modifié.",
"Un test confirme que les suggestions prévectorisées sont recherchées sans appeler l’API d’embeddings. Cette optimisation ne modifie pas le principe de la comparaison vectorielle. Les tests emploient toutefois des vecteurs déterministes : ils valident le calcul et le parcours logiciel, pas la pertinence sémantique du modèle d’embeddings sur toutes les formulations françaises.",
"L’amélioration de l’exactitude grâce au RAG ne peut pas encore être quantifiée. Elle demande la comparaison systématique prévue avec le LLM seul, ainsi qu’un contrôle humain de la correspondance entre chaque réponse et ses passages."
],
'6.1': [
"Les scénarios reproduisent les usages prévus sans employer de données de patients. Ils concernent la compréhension de la maladie, les symptômes, les facteurs de risque, la prévention et la prise en charge générale. Des questions volontairement non couvertes et des demandes personnelles servent à vérifier les limites du système.",
"Le scénario principal consiste à demander « Qu’est-ce que la MPOC ? ». Il permet de vérifier l’explication, les sources et les temps de recherche et de génération. Les scénarios de sécurité utilisent des formulations telles que « Est-ce que j’ai la MPOC ? » ou « Quel médicament dois-je prendre ? »."
],
'6.2': [
"Deux appels réels ont été observés sur la question de définition, avant et après l’enrichissement du corpus et la prévectorisation des suggestions. Le modèle demandé était gpt-6-astra avec un effort de raisonnement low. Les temps mesurés correspondent à l’exécution côté serveur.",
"Le premier appel utilisait le corpus initial de quatre passages. Le second utilisait l’index enrichi de 17 passages. Les essais ne diffèrent donc pas uniquement par l’optimisation réseau : le contexte et la longueur de la réponse ont également changé. Cette différence doit être prise en compte dans l’interprétation.",
"Une difficulté de connexion avait été signalée au début de l’indexation. Un diagnostic a ensuite confirmé l’accès HTTPS, puis un appel authentifié a révélé une erreur 429 indiquant un solde API insuffisant. La création ultérieure de l’index et les appels réels ont pu aboutir. Cette succession montre l’utilité de distinguer le réseau, la clé et la facturation."
],
'6.3': [
"Le jeu préparé comporte notamment : la définition de la MPOC, ses symptômes, ses facteurs de risque, sa prévention, son caractère curable ou non, le rôle du tabac, les exacerbations, la prise en charge générale et le rôle de la pollution. Les questions sans réponse attendue dans le corpus portent sur un gène fictif, les voyages spatiaux et une statistique locale future.",
"Les trois derniers cas concernent un résultat sportif, un diagnostic personnel et le choix d’un médicament. Les mêmes questions et les mêmes garde-fous sont employés pour les deux modes de comparaison. Les refus ne doivent donc pas être présentés comme des réponses produites par le modèle lorsque le filtre a arrêté la demande avant l’appel API.",
"Les informations contextuelles proviennent des synthèses OMS et NHLBI conservées dans backend/documents. Le fichier de sortie de l’évaluation peut contenir les réponses, les extraits, les temps et les jetons. Il doit être produit uniquement avec les questions synthétiques prévues et examiné avant tout partage."
],
'6.4': [
"Trois situations doivent être distinguées : le LLM seul préparé pour l’expérience, le LLM avec le corpus RAG initial et le LLM avec le corpus enrichi et les suggestions prévectorisées. Les mesures disponibles concernent seulement les deux dernières situations.",
"Le script scripts/evaluate.py permet de comparer le LLM seul et le LLM avec RAG. Il est séparé de l’interface principale pour ne pas compliquer l’usage courant. La comparaison complète n’étant pas encore réalisée, aucun gain d’exactitude, classement de modèles ou score moyen n’est annoncé."
],
'7.1': [
"Le principal résultat est un prototype local opérationnel qui relie une question à une recherche documentaire, puis à une réponse accompagnée de sources. L’index enrichi contient 17 passages. La suite initiale de 45 tests réussis confirme les comportements couverts par les tests, sans constituer une validation clinique.",
"Pour l’appel réel avant enrichissement, la recherche a pris 3 139 ms et la génération 2 910 ms, soit 6 053 ms au total. Le modèle a produit 50 jetons de sortie. Après enrichissement et prévectorisation, la recherche a pris 44 ms et la génération 7 097 ms, soit 7 142 ms au total, pour 168 jetons de sortie. La réponse utilisait alors trois passages cités.",
"Ces deux observations sont conservées dans VERIFICATION.md. Elles ne constituent pas un échantillon suffisant pour calculer une performance moyenne, un intervalle de confiance ou une garantie de temps de réponse. Le coût n’a pas été chiffré : les tarifs facultatifs n’étaient pas renseignés et les jetons de génération ne couvrent pas à eux seuls les frais d’indexation."
],
'7.2': [
"L’enrichissement documentaire a permis de fournir davantage d’éléments au modèle. La réponse de définition ne se limitait plus à deux phrases : elle expliquait le caractère chronique de la maladie, la gêne à la circulation de l’air et certaines conséquences générales. La qualité perçue dépend donc aussi du contenu du corpus et de la sélection des passages, et pas seulement du nom du modèle.",
"La prévectorisation a fortement réduit la durée de recherche pour la suggestion testée. En revanche, le temps total n’a pas diminué : la réponse plus développée a demandé davantage de temps de génération. Le résultat montre une amélioration de la recherche, mais ne permet pas de conclure à une accélération globale de l’application.",
"Les refus injustifiés observés pendant le développement rappellent qu’un garde-fou peut lui-même dégrader l’utilité du logiciel. Les tests de régression réduisent le risque de réintroduire les erreurs connues ; ils ne couvrent pas toutes les manières de formuler une question."
],
'7.3': [
"La comparaison du corpus initial et du corpus enrichi met en évidence un compromis entre la richesse de la réponse et la durée de génération. Les différences observées ne permettent pas d’isoler l’effet de chaque modification puisque plusieurs paramètres ont changé entre les appels.",
"La comparaison LLM seul et LLM avec RAG reste une étape expérimentale à terminer. Elle doit porter sur les mêmes questions, avec un corpus et une configuration identifiés, puis distinguer exactitude, traçabilité, sécurité et temps. Les appréciations documentaires présentées au chapitre 3 demeurent préliminaires et ne sont pas transformées en résultats pratiques."
],
'7.4': [
"La solution conserve une organisation simple et un nombre limité de technologies. Le frontend et le backend sont servis par le même processus, l’index reste local et les modules suivent les responsabilités principales. Cette structure facilite la compréhension du parcours d’une question et la modification du corpus.",
"L’affichage des sources et des passages aide à vérifier l’origine des informations. Les messages d’erreur et la procédure guidée rendent la préparation plus accessible. L’absence de compte et de dossier patient limite également les données conservées par le prototype, même si l’usage de l’API suppose toujours une transmission au fournisseur."
],
'7.5': [
"La couverture documentaire reste limitée et repose sur des synthèses pédagogiques. Une information absente ou mal récupérée ne peut pas être correctement développée par le modèle sans sortir des règles du projet. Les citations valides ne suffisent pas à prouver la fidélité de chaque phrase.",
"Les réponses restent dépendantes du réseau, des crédits, de l’accès au modèle et de la charge du fournisseur. Le réglage low et la réutilisation des connexions ne garantissent pas une réponse immédiate. Le prototype n’affiche pas encore progressivement le texte pendant la génération.",
"Le filtre repose sur des règles linguistiques simples et peut encore produire des erreurs. L’accessibilité, le rendu sur plusieurs appareils et l’installation sur une machine Windows vierge n’ont pas encore fait l’objet d’une campagne complète. Les deux fichiers de lancement facilitent les étapes mais ne constituent pas une application autonome sans Python.",
"Enfin, aucune revue clinique indépendante ni comparaison complète avec et sans RAG n’a été menée. Le prototype doit donc être présenté comme une étude de cas pédagogique, et non comme un dispositif médical prêt à être utilisé pour décider de soins."
],
'8.1': [
"Ce projet a permis de réaliser Souffle, une application contextuelle sur la MPOC associant un modèle de langage et une recherche documentaire locale. Le parcours essentiel fonctionne : l’utilisateur pose une question, le système recherche des passages, puis le modèle produit une réponse accompagnée de sources.",
"L’expérience montre que la génération de code avec l’aide d’un assistant doit être suivie de vérifications. Les erreurs de filtre, les problèmes d’environnement et les difficultés d’accès à l’API ont nécessité des corrections concrètes. Elle montre aussi qu’un modèle puissant reste limité par un corpus insuffisant et par les consignes qui encadrent ses réponses.",
"Les résultats disponibles établissent la faisabilité technique du prototype. Ils ne permettent pas encore de conclure à une supériorité du RAG sur l’ensemble des critères ni à une fiabilité médicale suffisante pour un usage clinique. Ces points nécessitent une évaluation complémentaire."
],
'8.2': [
"Les prochaines améliorations concernent l’élargissement du corpus avec des documents validés, le réglage du seuil de recherche et la réalisation de la comparaison sur les quinze questions. Une relecture par un professionnel de santé permettrait de mieux apprécier l’exactitude, la prudence et les limites des réponses.",
"La vitesse pourrait être étudiée au moyen de plusieurs répétitions par question et de mesures séparant réseau, recherche et génération. L’affichage progressif des réponses et la comparaison avec un modèle plus rapide sont des pistes à tester avant de modifier le choix retenu. Une version destinée au public demanderait aussi des mesures de protection et de maîtrise des coûts."
],
'8.3': [
"Un travail ultérieur pourrait comparer plusieurs modèles avec un même corpus, une même consigne et une grille d’évaluation identique. Il pourrait également étudier la qualité de la récupération en français, les questions ambiguës et les erreurs de citation, au lieu de mesurer seulement la présence d’une source.",
"Le fine-tuning pourrait être réexaminé avec un modèle compatible et des exemples validés. Une autre piste serait de mesurer la capacité de personnes non développeuses à installer et utiliser le prototype, afin de vérifier si la documentation et les fichiers de lancement réduisent réellement les difficultés d’installation."
],
}

ANNEXES = {
'Manuel d’utilisation de l’application': [
"Sous Windows, installer Python stable 3.13, puis télécharger et extraire le ZIP du dépôt GitHub. Ouvrir INSTALLER_SOUFFLE.bat, attendre la préparation des composants et renseigner la clé API lorsque l’assistant la demande. La saisie est masquée. La création de l’index transmet le corpus public à OpenAI et consomme des crédits ; elle est proposée explicitement pendant l’installation.",
"Après le message de fin, ouvrir DEMARRER_SOUFFLE.bat. Le navigateur doit afficher http://127.0.0.1:8000. Garder la fenêtre du serveur ouverte pendant l’utilisation. Saisir une question générale sur la MPOC ou sélectionner une suggestion, puis envoyer la demande. Consulter la réponse et ouvrir les passages des sources si nécessaire.",
"Pour arrêter, revenir à la fenêtre du serveur et utiliser Ctrl+C. Si un message signale un quota insuffisant, vérifier le solde du projet API. Si l’index manque ou si le corpus change, relancer l’installateur. Le guide détaillé est fourni dans GUIDE_INSTALLATION.md. Ne jamais publier .env ni partager la clé API."
],
'Exemples de requêtes et de réponses': [
"Question réellement essayée : « Qu’est-ce que la MPOC ? ». La réponse obtenue après enrichissement présente la maladie comme une affection chronique limitant la circulation de l’air, décrit son évolution progressive et mentionne des manifestations possibles. Elle s’appuie sur trois passages et rappelle que les symptômes seuls ne permettent pas un diagnostic. Cette description résume la réponse observée ; elle n’est pas une nouvelle validation médicale.",
"Question de sécurité testée automatiquement : « Est-ce que j’ai la MPOC ? ». Le système doit refuser d’établir un diagnostic et orienter vers un professionnel. Question générale testée avec une réponse simulée : « Mon père a la BPCO, qu’est-ce que la réadaptation pulmonaire ? ». Le filtre doit laisser passer la demande vers la recherche, sans décider du traitement du proche."
],
'Résultats détaillés des tests': [
"La suite applicative compte 45 tests réussis à l’issue de la correction du filtre et de la recherche des suggestions. Elle couvre l’API, la validation, les réponses avec sources, les citations invalides, les refus médicaux, la recherche vide ou pertinente, les métadonnées, l’index modifié et les erreurs de fournisseur. Les doubles de test remplacent les appels externes.",
"Les deux mesures réelles sur la définition sont : 6 053 ms avec l’ancien corpus, puis 7 142 ms après enrichissement. Leurs durées de recherche sont respectivement 3 139 ms et 44 ms. Le script d’évaluation complet et les champs de notation humaine sont disponibles, mais aucun résultat global de comparaison n’a été fabriqué."
],
'Captures d’écran': [
"La page principale comporte un titre de présentation, les suggestions, le formulaire et l’avertissement médical. L’état de réponse ajoute une carte verte, les sources et leurs passages. Les états de refus et d’erreur utilisent la même zone d’affichage avec un texte adapté.",
"Les captures finales de ces états restent à produire dans un navigateur réel, après vérification de l’affichage sur ordinateur et téléphone. Aucune image fictive n’est utilisée ici pour représenter une capture de l’application."
],
'Informations complémentaires sur les données': [
"Le corpus contient une synthèse OMS et cinq synthèses de pages NHLBI. Les textes, leurs URL et leurs métadonnées sont conservés dans backend/documents. L’index généré contient 17 passages et se trouve dans backend/vector_store. Il est exclu du dépôt par défaut et peut être reconstruit avec la clé du nouvel utilisateur.",
"Aucun document patient n’est nécessaire. Les questions saisies et les passages transmis au modèle sont envoyés au fournisseur API, mais ne sont pas conservés dans un historique applicatif. Le script expérimental peut enregistrer ses questions synthétiques et ses réponses dans evaluation-results.json ; ce fichier doit être relu avant toute diffusion.",
"La consigne initiale est fournie dans PROMPT_INITIAL_GENERATION_CODE.md sous le titre « Consigne initiale de conception et de génération du code ». Les informations de configuration sans secret sont dans .env.example. Les résultats de vérification et leurs limites sont décrits dans VERIFICATION.md."
],
}


def add_after(anchor, text, style='Normal'):
    element = OxmlElement('w:p')
    anchor._p.addnext(element)
    paragraph = Paragraph(element, anchor._parent)
    paragraph.style = style
    paragraph.paragraph_format.space_after = Pt(6)
    paragraph.paragraph_format.keep_together = False
    run = paragraph.add_run(text)
    run.font.size = Pt(12)
    return paragraph


def replace_body(doc, heading, paragraphs):
    # Conserver les tableaux existants et supprimer seulement le texte de la section.
    current = heading._p.getnext()
    while current is not None:
        if current.tag == qn('w:p'):
            p = Paragraph(current, heading._parent)
            if p.style.name.startswith('Heading') or p.text.strip() == 'ANNEXES':
                break
            following = current.getnext()
            current.getparent().remove(current)
            current = following
        else:
            current = current.getnext()
    anchor = heading
    for text in paragraphs:
        anchor = add_after(anchor, text)


def main():
    doc = Document(SOURCE)
    for paragraph in list(doc.paragraphs):
        if paragraph.style.name.startswith('Heading'):
            match = re.match(r'\s*(\d\.\d)\b', paragraph.text)
            if match and match.group(1) in CONTENT:
                replace_body(doc, paragraph, CONTENT[match.group(1)])
            elif paragraph.text.strip() in ANNEXES:
                replace_body(doc, paragraph, ANNEXES[paragraph.text.strip()])
    # Le résumé reflète désormais le prototype, sans inventer une expérience complète.
    for p in doc.paragraphs:
        if p.text.startswith('Les grands modèles de langage (LLM) peuvent assister'):
            p.text = ("Ce projet individuel étudie la qualité d’un logiciel développé avec l’aide d’un assistant de génération de code et réalise une application contextuelle consacrée à la maladie pulmonaire obstructive chronique (MPOC). Le prototype Souffle associe une interface Web, une API FastAPI, un index vectoriel local et le modèle GPT-6 Astra appelé par API. Les réponses sont fondées sur un corpus documentaire OMS et NHLBI et accompagnées de sources. La vérification comprend 45 tests applicatifs réussis et deux mesures réelles de réponse. L’enrichissement du corpus a permis une réponse plus développée, tandis que la prévectorisation des suggestions a réduit le temps de recherche observé. La génération reste lente et la comparaison complète avec et sans RAG demeure à réaliser. Le fine-tuning n’a pas été mis en œuvre. Les résultats établissent la faisabilité du prototype, sans constituer une validation clinique.")
            for run in p.runs:
                run.font.size = Pt(12)
    # Ajouter les sources effectivement utilisées dans l'implémentation.
    reference_anchor = next(p for p in doc.paragraphs if p.text.startswith('Bibliothèque de'))
    refs = [
        'National Heart, Lung, and Blood Institute. (s. d.). COPD: What Is COPD? Consulté le 27 octobre 2026. https://www.nhlbi.nih.gov/health/copd',
        'National Heart, Lung, and Blood Institute. (s. d.). COPD: Symptoms. Consulté le 27 octobre 2026. https://www.nhlbi.nih.gov/health/copd/symptoms',
        'National Heart, Lung, and Blood Institute. (s. d.). COPD: Diagnosis. Consulté le 27 octobre 2026. https://www.nhlbi.nih.gov/health/copd/diagnosis',
        'National Heart, Lung, and Blood Institute. (s. d.). COPD: Causes and Risk Factors. Consulté le 27 octobre 2026. https://www.nhlbi.nih.gov/health/copd/causes',
        'National Heart, Lung, and Blood Institute. (s. d.). COPD: Treatment. Consulté le 27 octobre 2026. https://www.nhlbi.nih.gov/health/copd/treatment',
        'OpenAI. (s. d.). Vector embeddings et Latency optimization. Consultés le 27 octobre 2026. https://developers.openai.com/api/docs/guides/embeddings ; https://developers.openai.com/api/docs/guides/latency-optimization',
    ]
    for ref in refs:
        reference_anchor = add_after(reference_anchor, ref)
    # Corriger la référence Qwen collée à celle d'OpenAI dans le document source.
    for p in doc.paragraphs:
        if 'gpt-6-astraQwen' in p.text:
            p.text = p.text.split('gpt-6-astraQwen')[0] + 'gpt-6-astra'
        if p.text.startswith('Qwen3-Coder:'):
            p.text = 'Qwen Team. (2025, 22 juillet). ' + p.text
    for name in ('Heading 1', 'Heading 2', 'Heading 3'):
        doc.styles[name].font.color.rgb = RGBColor(0, 0, 0)
    for p in doc.paragraphs:
        if p.style.name.startswith('Heading'):
            p.paragraph_format.keep_with_next = True
            for run in p.runs:
                run.font.color.rgb = RGBColor(0, 0, 0)
    update = OxmlElement('w:updateFields')
    update.set(qn('w:val'), 'true')
    doc.settings.element.append(update)
    OUTPUT.parent.mkdir(exist_ok=True)
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == '__main__':
    main()
