"""Assistant d'installation Windows. Aucun téléchargement hors de PyPI."""
import argparse
import getpass
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
ENVIRONMENT = ROOT / '.venv313'
PYTHON = ENVIRONMENT / 'Scripts/python.exe'
LOCK = ROOT / 'requirements-lock.txt'
STAMP = ENVIRONMENT / '.souffle-requirements'


def save_api_key(path, key):
    if not key or any(c.isspace() for c in key):
        raise ValueError('La clé doit être renseignée sans espace ni retour à la ligne.')
    text = path.read_text(encoding='utf-8')
    line = 'OPENAI_API_KEY=' + key
    if re.search(r'^OPENAI_API_KEY=.*$', text, flags=re.M):
        text = re.sub(r'^OPENAI_API_KEY=.*$', lambda match: line, text, flags=re.M)
    else:
        text += '\n' + line + '\n'
    path.write_text(text, encoding='utf-8')


def install():
    if not ((3, 12) <= sys.version_info[:2] <= (3, 13)) or sys.version_info.releaselevel != 'final':
        raise ValueError('Installez une version stable de Python 3.12 ou 3.13.')
    print('\nSOUFFLE — Installation guidée\n')
    print('Le logiciel est local. Les appels OpenAI nécessitent une clé API et des crédits payants.')
    if not PYTHON.exists():
        print('1/3 Préparation de Python…')
        subprocess.run([sys.executable, '-m', 'venv', str(ENVIRONMENT)], check=True)
    digest = hashlib.sha256(LOCK.read_bytes()).hexdigest()
    if not STAMP.exists() or STAMP.read_text() != digest:
        print('2/3 Installation des composants. Cela peut prendre plusieurs minutes…')
        subprocess.run([str(PYTHON), '-m', 'pip', 'install', '-r', str(LOCK)], cwd=ROOT, check=True)
        STAMP.write_text(digest)
    print('3/3 Configuration et documents…')
    subprocess.run([str(PYTHON), str(Path(__file__).resolve()), '--configure'], cwd=ROOT, check=True)


def configure():
    sys.path.insert(0, str(ROOT))
    env_file = ROOT / '.env'
    if not env_file.exists():
        env_file.write_text((ROOT / '.env.example').read_text(encoding='utf-8'), encoding='utf-8')
    from dotenv import load_dotenv
    load_dotenv(env_file)
    if not os.getenv('OPENAI_API_KEY', '').strip():
        print('Créez votre clé sur https://platform.openai.com/api-keys')
        print('Collez-la ci-dessous. La saisie est masquée, puis enregistrée uniquement dans .env.')
        key = getpass.getpass('Clé API : ').strip()
        save_api_key(env_file, key)
        os.environ['OPENAI_API_KEY'] = key
    from backend.app import config, rag
    ready = False
    if config.INDEX.exists():
        try:
            rag.read_index(config.INDEX.stat().st_mtime_ns)
            ready = True
        except (ValueError, KeyError, OSError):
            pass
    if not ready:
        print('La préparation des documents enverra le corpus public à OpenAI et consommera des crédits API.')
        if input('Préparer les documents maintenant ? [O/n] : ').strip().lower() not in ('', 'o', 'oui'):
            print('Installation des composants terminée. Relancez INSTALLER_SOUFFLE.bat pour préparer les documents.')
            return
        from openai import APIError
        from backend.app.errors import provider_error_message
        try:
            print(f'Documents prêts : {rag.build_index()} passages.')
        except APIError as exc:
            raise ValueError(provider_error_message(exc)) from None
    print('\nInstallation terminée. Double-cliquez sur DEMARRER_SOUFFLE.bat.')


def open_when_ready():
    for _ in range(60):
        try:
            with urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=1) as response:
                if response.status == 200:
                    webbrowser.open('http://127.0.0.1:8000')
                    return
        except OSError:
            time.sleep(.5)
    print('Si le navigateur ne s’ouvre pas, consultez http://127.0.0.1:8000.')


def start():
    sys.path.insert(0, str(ROOT))
    from backend.app import config, rag
    if not os.getenv('OPENAI_API_KEY') or not config.INDEX.exists():
        raise ValueError('La préparation est incomplète. Relancez INSTALLER_SOUFFLE.bat.')
    rag.read_index(config.INDEX.stat().st_mtime_ns)
    print('Ouverture de Souffle… Gardez cette fenêtre ouverte. Pour arrêter : Ctrl+C.')
    threading.Thread(target=open_when_ready, daemon=True).start()
    import uvicorn
    uvicorn.run('backend.app.main:app', host='127.0.0.1', port=8000, log_level='warning')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--configure', action='store_true')
    parser.add_argument('--start', action='store_true')
    args = parser.parse_args()
    os.chdir(ROOT)
    try:
        if args.start:
            start()
        elif args.configure:
            configure()
        else:
            install()
    except KeyboardInterrupt:
        print('\nOpération arrêtée.')
    except subprocess.CalledProcessError:
        print('\nInstallation non terminée. Vérifiez Internet et consultez GUIDE_INSTALLATION.md, puis relancez l’installateur.')
        sys.exit(1)
    except Exception as exc:
        # Les erreurs API sont converties plus haut : ne jamais imprimer un objet de requête.
        if isinstance(exc, ValueError):
            print('\n' + str(exc))
        else:
            print('\nImpossible de terminer :', type(exc).__name__, '— consultez GUIDE_INSTALLATION.md.')
        sys.exit(1)
