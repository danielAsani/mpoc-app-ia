"""Diagnostic réseau sans envoyer ni afficher la clé API."""
import os
import socket

import httpx

from backend.app import config


def main():
    print('Clé API renseignée :', bool(os.getenv('OPENAI_API_KEY')))
    print('Index présent :', config.INDEX.exists())
    print('Proxy configuré :', any(os.getenv(k) for k in ('HTTPS_PROXY', 'HTTP_PROXY', 'ALL_PROXY')))
    try:
        socket.getaddrinfo('api.openai.com', 443)
        print('Résolution DNS : OK')
        response = httpx.get('https://api.openai.com/v1/models', timeout=15)
        print('Connexion HTTPS : OK (HTTP', response.status_code, ')')
        print('Un HTTP 401 est attendu ici : ce diagnostic n’envoie pas la clé.')
    except Exception as exc:
        print('Connexion HTTPS impossible :', type(exc).__name__)
        cause = exc
        while cause.__cause__:
            cause = cause.__cause__
        print('Cause réseau :', type(cause).__name__, str(cause))


if __name__ == '__main__':
    main()
