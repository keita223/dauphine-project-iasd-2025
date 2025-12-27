"""Configuration et initialisation de LangFuse pour le monitoring."""

import os
import sys
from dotenv import load_dotenv
from langfuse import Langfuse

# Charger les variables d'environnement depuis .env
load_dotenv()

# Fix pour Windows: forcer l'encodage UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


def get_langfuse_client():
    """
    Crée et retourne un client LangFuse pour le monitoring.

    Returns:
        Langfuse: Client LangFuse configuré ou None si erreur
    """
    try:
        # Récupérer les clés depuis les variables d'environnement
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        host = os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")

        # Vérifier que les clés existent
        if not public_key or not secret_key:
            print("[WARN] Cles Langfuse manquantes dans .env")
            return None

        # Debug: afficher les premières lettres des clés
        print(f"[INFO] Initialisation Langfuse avec cles: pk-{public_key[3:8]}... / sk-{secret_key[3:8]}...")

        # Créer le client Langfuse
        client = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host,
        )

        # Vérifier la connexion
        print("[OK] LangFuse client initialise avec succes")
        print(f"[INFO] Connexion a: {host}")

        return client

    except Exception as e:
        print(f"[WARN] Erreur lors de l'initialisation de LangFuse: {e}")
        print("[INFO] Le systeme continuera sans monitoring")
        return None


# Alias pour compatibilité avec le code existant
get_langfuse_handler = get_langfuse_client


def log_to_langfuse(langfuse_client, name: str, input_data: dict, output_data: dict, metadata: dict = None):
    """
    Enregistre une span Langfuse pour tracer les appels d'agents.

    Args:
        langfuse_client: Client Langfuse
        name: Nom de l'événement (ex: "supervisor_decision", "rag_query")
        input_data: Données d'entrée
        output_data: Données de sortie
        metadata: Métadonnées optionnelles
    """
    if not langfuse_client:
        return

    try:
        # Créer une span dans Langfuse (API v3)
        span = langfuse_client.start_span(
            name=name,
            input=input_data,
            metadata=metadata or {}
        )

        # Ajouter l'output et terminer la span
        span.update(output=output_data)
        span.end()

        # Forcer l'envoi immédiat
        langfuse_client.flush()

        print(f"[LANGFUSE] Span '{name}' envoye")

    except Exception as e:
        # Ne pas bloquer le système si le monitoring échoue
        print(f"[WARN] Erreur Langfuse: {e}")


# Pour tester
if __name__ == "__main__":
    client = get_langfuse_client()
    if client:
        print("[OK] LangFuse client est pret!")
        print("[INFO] Le monitoring se fait via log_to_langfuse() dans les agents")

        # Test d'une span
        log_to_langfuse(
            client,
            name="test_monitoring",
            input_data={"test": "Configuration"},
            output_data={"status": "OK"},
            metadata={"source": "monitoring.py"}
        )
        print("[OK] Test de monitoring termine")
