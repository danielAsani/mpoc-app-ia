from openai import APIConnectionError, APITimeoutError, AuthenticationError, RateLimitError


class ConfigurationError(ValueError):
    """Erreur locale dont le message peut être présenté sans exposer de secret."""


def provider_error_message(error):
    if isinstance(error, AuthenticationError):
        return 'La clé API OpenAI est refusée. Vérifiez OPENAI_API_KEY dans .env puis redémarrez le serveur.'
    if isinstance(error, RateLimitError):
        return 'Le quota ou la limite OpenAI est atteint. Vérifiez la facturation et le quota du projet API, puis réessayez.'
    if isinstance(error, APITimeoutError):
        return 'OpenAI met trop de temps à répondre. Veuillez réessayer dans quelques instants.'
    if isinstance(error, APIConnectionError):
        return 'Connexion à OpenAI impossible. Vérifiez votre connexion, le proxy ou le pare-feu, puis réessayez. Diagnostic : python -m scripts.check_connection.'
    return 'Le fournisseur IA est temporairement indisponible. Veuillez réessayer.'
