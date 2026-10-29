import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import APIError
from pydantic import BaseModel, ConfigDict, Field, field_validator

from . import config
from .service import answer_question
from .errors import ConfigurationError, provider_error_message

logging.basicConfig(level=logging.INFO)
logging.getLogger('httpx').setLevel(logging.WARNING)
app = FastAPI(title='Souffle — Assistant MPOC')


class Question(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    question: str = Field(min_length=1, max_length=config.MAX_QUESTION)

    @field_validator('question')
    @classmethod
    def not_empty(cls, value):
        if not value.strip():
            raise ValueError('La question est vide.')
        return value.strip()


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc):
    return JSONResponse(status_code=422, content={'detail': 'Saisissez une question de 1 à 1 000 caractères dans le champ question.'})


@app.get('/health')
def health():
    import os
    return dict(status='ok', index_ready=config.INDEX.exists(), api_configured=bool(os.getenv('OPENAI_API_KEY')))


@app.post('/ask')
def ask(body: Question):
    try:
        return answer_question(body.question)
    except ConfigurationError as exc:
        logging.warning('ask configuration type=%s', type(exc).__name__)
        return JSONResponse(status_code=503, content={'detail': str(exc)})
    except (ValueError, FileNotFoundError) as exc:
        logging.warning('ask failed type=%s', type(exc).__name__)
        return JSONResponse(status_code=503, content={'detail': 'Le service nécessite une configuration valide : vérifiez la clé API et reconstruisez l’index documentaire.'})
    except APIError as exc:
        logging.warning('provider failed type=%s', type(exc).__name__)
        return JSONResponse(status_code=502, content={'detail': provider_error_message(exc)})
    except Exception as exc:
        logging.error('ask failed type=%s', type(exc).__name__)
        return JSONResponse(status_code=500, content={'detail': 'Une erreur est survenue pendant la préparation de la réponse. Veuillez réessayer.'})


@app.get('/favicon.ico', include_in_schema=False)
def favicon():
    return FileResponse(config.ROOT / 'frontend/favicon.svg', media_type='image/svg+xml')


# Une seule origine : aucun CORS permissif ni serveur frontend supplémentaire.
app.mount('/', StaticFiles(directory=config.ROOT / 'frontend', html=True), name='frontend')
