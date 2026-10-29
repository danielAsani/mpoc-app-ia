from backend.app.rag import build_index
from backend.app.errors import provider_error_message
from openai import APIError

if __name__ == '__main__':
    try:
        print(f'Index créé : {build_index()} passages.')
    except APIError as exc:
        raise SystemExit(f'Index non créé : {provider_error_message(exc)}') from None
    except Exception as exc:
        raise SystemExit(f'Index non créé : {exc}') from None
