"""Configuration et initialisation de LangFuse pour le monitoring."""

from langfuse import Langfuse
from src.config import (
    LANGFUSE_PUBLIC_KEY,
    LANGFUSE_SECRET_KEY,
    LANGFUSE_HOST
)


def get_langfuse_handler():
    """
    Crée et retourne un client LangFuse pour tracker les appels LLM.
    
    Returns:
        Langfuse: Client LangFuse configuré
    """
    try:
        langfuse_client = Langfuse(
            public_key=LANGFUSE_PUBLIC_KEY,
            secret_key=LANGFUSE_SECRET_KEY,
            host=LANGFUSE_HOST,
        )
        print("✅ LangFuse client initialisé avec succès")
        return langfuse_client
    
    except Exception as e:
        print(f"⚠️ Erreur lors de l'initialisation de LangFuse: {e}")
        print("Le système continuera sans monitoring")
        return None


# Pour tester
if __name__ == "__main__":
    handler = get_langfuse_handler()
    if handler:
        print("🎉 LangFuse est prêt à tracker vos appels LLM !")