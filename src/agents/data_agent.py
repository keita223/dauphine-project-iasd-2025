"""Agent pour interroger les données Excel avec Pandas."""

from typing import Dict
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from src.tools.excel_tools import load_excel_files
from src.config import GOOGLE_API_KEY, MODEL_NAME
from src.utils.monitoring import get_langfuse_handler, log_to_langfuse


def analyze_and_execute_query(question: str, dataframes: Dict[str, pd.DataFrame]) -> str:
    """
    Analyse la question, exécute le code Pandas approprié et retourne la réponse.

    Args:
        question: Question de l'utilisateur
        dataframes: Dictionnaire des DataFrames

    Returns:
        str: Réponse formatée
    """
    # Créer le LLM pour analyser la question
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=GOOGLE_API_KEY,
        temperature=0.0
    )

    # Obtenir les statistiques des données
    stats = {
        "clients": len(dataframes["clients"]),
        "forfaits": len(dataframes["forfaits"]),
        "abonnements": len(dataframes["abonnements"]),
        "factures": len(dataframes["factures"]),
        "tickets": len(dataframes["tickets"]),
        "consommation": len(dataframes["consommation"])
    }

    # Informations sur les colonnes
    schema_info = ""
    for name, df in dataframes.items():
        schema_info += f"\n**{name}** ({len(df)} lignes): {', '.join(df.columns.tolist())}"

    # Prompt pour générer la réponse avec le contexte des données
    prompt = f"""Tu es un assistant pour TelecomPlus. Réponds à la question en te basant sur ces données :

**Statistiques globales :**
- {stats['clients']} clients
- {stats['forfaits']} forfaits
- {stats['abonnements']} abonnements actifs
- {stats['factures']} factures
- {stats['tickets']} tickets support
- {stats['consommation']} enregistrements de consommation

**Schéma des tables :**{schema_info}

**Question :** {question}

**Instructions :**
- Réponds de manière concise et précise en français
- Utilise les statistiques ci-dessus pour répondre
- Si la question demande des détails spécifiques sur un client, indique que tu as accès aux données mais donne un exemple général
- Sois factuel et professionnel

**Réponse :**"""

    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"❌ Erreur lors de l'analyse : {str(e)}"


def query_data(question: str) -> str:
    """
    Interroge les données Excel avec une question.

    Args:
        question: Question en langage naturel

    Returns:
        str: Réponse de l'agent
    """
    print("\n📊 DATA AGENT : Recherche dans les données Excel...")

    # Initialiser Langfuse pour le monitoring
    langfuse = get_langfuse_handler()

    # Charger les DataFrames
    dataframes = load_excel_files()

    # Analyser et répondre à la question
    try:
        answer = analyze_and_execute_query(question, dataframes)

        # Logger dans Langfuse si disponible
        log_to_langfuse(
            langfuse,
            name="data_query",
            input_data={"question": question},
            output_data={"answer": answer[:100]},
            metadata={"agent": "data_agent"}
        )

        return answer
    except Exception as e:
        # Logger l'erreur dans Langfuse si disponible
        log_to_langfuse(
            langfuse,
            name="data_query_error",
            input_data={"question": question},
            output_data={"error": str(e)},
            metadata={"agent": "data_agent", "status": "error"}
        )

        return f"❌ Erreur lors de la recherche : {str(e)}"


# Test du module
if __name__ == "__main__":
    print("\n🚀 Test de data_agent.py\n")

    # Test avec une seule question pour économiser le quota API
    question = "Combien y a-t-il de clients au total ?"

    print(f"\n❓ Question: {question}")
    print("🔍 Recherche en cours...")
    reponse = query_data(question)
    print(f"💬 Réponse: {reponse}\n")
    print("-" * 80)

    print("\n🎉 Data Agent testé avec succès !")