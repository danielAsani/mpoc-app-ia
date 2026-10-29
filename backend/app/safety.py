import re
import unicodedata


def simplify(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text.lower()) if unicodedata.category(c) != 'Mn').replace('’', "'")


def check_question(question):
    text = simplify(question)
    urgent = ["mal a respirer", "respire mal", "douleur thoracique", "mal a la poitrine", "ne peux plus respirer"]
    if any(term in text for term in urgent) and re.search(r"\b(je|j'|mon|ma|mes)\b|j'ai", text):
        return 'medical', "Je ne peux pas évaluer vos symptômes. Contactez rapidement un professionnel de santé ; si la difficulté respiratoire est importante ou soudaine, contactez les services d’urgence locaux."
    personal = [
        r"\bquel\w* (medicament|traitement)\b.*\b(dois-je|devrais-je|je dois|pour moi|mon cas)\b",
        r"\b(quel|quelle) (dose|dosage)\b.*\b(prendre|pour moi|mon cas|dois-je)\b",
        r"\b(ai-je|suis-je)\b.*\b(mpoc|bpco|malade|atteint|atteinte)\b",
        r"\best-ce que j'ai\b.*\b(mpoc|bpco)\b",
        r"\b(dis-moi|dites-moi|savoir|dire)\b.*\bsi j'ai\b.*\b(mpoc|bpco)\b",
        r"\bme (prescri|diagnost)",
    ]
    personal.extend([r"\btraitement\b.*\b(mon cas|pour moi|ma situation)\b", r"\b(diagnostique|diagnostiquer|prescris|prescrire|prescrivez)\b.*\b(moi|mon|ma|mes)\b"])
    if any(re.search(pattern, text) for pattern in personal):
        return 'medical', "Je ne peux pas établir de diagnostic ni proposer de médicament ou de traitement pour votre cas personnel. Consultez un professionnel de santé."
    if not re.search(r'\b(mpoc|bpco|copd|pulmonaire|respiratoire|poumon|poumons|tabagisme|bronchite|emphyseme)\b', text):
        return 'off_topic', 'Cet assistant répond aux questions générales sur la MPOC/BPCO. Précisez ce lien dans votre question.'
    return None
