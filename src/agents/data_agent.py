"""Agent pour interroger les données Excel avec Pandas."""

from typing import Dict
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from src.tools.excel_tools import load_excel_files
from src.config import GOOGLE_API_KEY, MODEL_NAME
from src.utils.monitoring import get_langfuse_handler

def create_data_agent(dataframes: Dict[str, pd.DataFrame]):
    """
    Crée un agent capable d'interroger les DataFrames.

    Args:
        dataframes: Dictionnaire des DataFrames à interroger

    Returns:
        Agent configuré pour interroger les données
    """
    print("🤖 Création du Data Agent...")

    # Créer le LLM
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=GOOGLE_API_KEY,
        temperature=0.0
    )

    # Combiner tous les DataFrames en un seul pour simplifier
    # On garde seulement le DataFrame clients pour commencer
    df_clients = dataframes['clients']

    # Créer l'agent Pandas avec un seul DataFrame
    agent = create_pandas_dataframe_agent(
        llm=llm,
        df=df_clients,
        verbose=True,
        allow_dangerous_code=True,  # Nécessaire pour exécuter du code Pandas
        prefix="""Tu es un assistant spécialisé dans l'analyse de données clients pour TelecomPlus.

Tu as accès à un DataFrame nommé 'df' qui contient les informations des clients.

Instructions:
- Utilise 'df' pour accéder aux données des clients
- Tu dois répondre en français et être précis
- Le DataFrame contient les colonnes suivantes: client_id, nom, prenom, email, telephone, date_inscription, ville, forfait_id
"""
    )

    print("✅ Data Agent créé avec succès")
    return agent


def query_data(question: str) -> str:
    """
    Interroge les données Excel avec une question.

    Args:
        question: Question en langage naturel

    Returns:
        str: Réponse de l'agent
    """
    # Initialiser Langfuse pour le monitoring
    langfuse = get_langfuse_handler()

    # Charger les DataFrames
    dataframes = load_excel_files()

    # Créer l'agent
    agent = create_data_agent(dataframes)

    # Poser la question
    try:
        response = agent.invoke({"input": question})
        answer = response["output"]

        # Logger dans Langfuse si disponible
        if langfuse:
            try:
                langfuse.span(
                    name="data_query",
                    input={"question": question},
                    output={"answer": answer[:100]},
                    metadata={"agent": "data_agent"}
                )
            except:
                pass  # Ignore si erreur de logging

        return answer
    except Exception as e:
        # Logger l'erreur dans Langfuse si disponible
        if langfuse:
            try:
                langfuse.span(
                    name="data_query_error",
                    input={"question": question},
                    output={"error": str(e)},
                    metadata={"agent": "data_agent", "status": "error"}
                )
            except:
                pass

        return f"❌ Erreur: {str(e)}"


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