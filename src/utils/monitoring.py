"""Configuration et initialisation de LangFuse pour le monitoring."""

from langfuse import Langfuse
from src.config import (
    LANGFUSE_PUBLIC_KEY,
    LANGFUSE_SECRET_KEY,
    LANGFUSE_HOST
)


def get_langfuse_handler():
    """
    Crée et retourne un client LangFuse pour le monitoring.

    Returns:
        Langfuse: Client LangFuse configuré ou None si erreur
    """
    try:
        # Vérifier que les clés existent
        if not LANGFUSE_PUBLIC_KEY or not LANGFUSE_SECRET_KEY:
            print("⚠️ Clés Langfuse manquantes dans .env")
            return None

        client = Langfuse(
            public_key=LANGFUSE_PUBLIC_KEY,
            secret_key=LANGFUSE_SECRET_KEY,
            host=LANGFUSE_HOST,
        )
        print("✅ LangFuse client initialisé avec succès")
        return client

    except Exception as e:
        print(f"⚠️ Erreur lors de l'initialisation de LangFuse: {e}")
        print("Le système continuera sans monitoring")
        return None


def log_to_langfuse(langfuse_client, name: str, input_data: dict, output_data: dict, metadata: dict = None):
    """
    Enregistre une trace dans Langfuse de manière fiable.

    Args:
        langfuse_client: Client Langfuse
        name: Nom de l'événement
        input_data: Données d'entrée
        output_data: Données de sortie
        metadata: Métadonnées optionnelles
    """
    if not langfuse_client:
        return

    try:
        # Créer une trace
        trace = langfuse_client.trace(
            name=name,
            input=input_data,
            output=output_data,
            metadata=metadata or {}
        )

        # Forcer l'envoi immédiat
        langfuse_client.flush()

    except Exception as e:
        # Ignorer silencieusement les erreurs de monitoring
        pass


# Pour tester
if __name__ == "__main__":
    handler = get_langfuse_handler()
    if handler:
        print("🎉 LangFuse est prêt à tracker vos appels LLM !")