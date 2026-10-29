import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / '.env')
DOCUMENTS = ROOT / 'backend/documents'
INDEX = ROOT / 'backend/vector_store/index.json'
LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-6-astra')
LLM_REASONING_EFFORT = os.getenv('LLM_REASONING_EFFORT', 'low')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')
THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', '0.35'))
TOP_K = int(os.getenv('TOP_K', '4'))
MAX_QUESTION = 1000
DISCLAIMER = "Informations générales uniquement : cet assistant ne remplace pas l’avis d’un professionnel de santé. N’indiquez pas de données personnelles."
INSUFFICIENT = "Les documents disponibles ne contiennent pas suffisamment d’informations pour répondre à cette question."
