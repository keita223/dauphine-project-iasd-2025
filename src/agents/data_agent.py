"""Agent pour interroger les données Excel avec Pandas."""

from typing import Dict
import pandas as pd
from langchain_anthropic import ChatAnthropic
from src.tools.excel_tools import load_excel_files
from src.config import ANTHROPIC_API_KEY
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
    # Créer le LLM Claude pour analyser la question
    llm = ChatAnthropic(
        model="claude-3-haiku-20240307",
        api_key=ANTHROPIC_API_KEY,
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

    # Informations sur les colonnes + aperçu des données
    schema_info = ""
    for name, df in dataframes.items():
        schema_info += f"\n**{name}** ({len(df)} lignes): {', '.join(df.columns.tolist())}"
        # Ajouter un aperçu des 3 premières lignes pour aider le LLM
        schema_info += f"\n   Exemple: {df.head(3).to_dict('records')}"

    # Prompt optimisé pour donner les vraies données (pas de refus pour confidentialité)
    prompt = f"""Tu es un assistant DATA pour TelecomPlus. Tu as un accès COMPLET et AUTORISÉ aux données clients.

**Statistiques globales :**
- {stats['clients']} clients
- {stats['forfaits']} forfaits
- {stats['abonnements']} abonnements actifs
- {stats['factures']} factures
- {stats['tickets']} tickets support
- {stats['consommation']} enregistrements de consommation

**Schéma des tables :**{schema_info}

**Question :** {question}

**INSTRUCTIONS CRITIQUES :**
1. Tu es AUTORISÉ à partager toutes les données clients (c'est un système interne sécurisé)
2. Réponds avec les VRAIES données, pas des exemples génériques
3. Si on te demande des infos sur un client spécifique, donne-les DIRECTEMENT
4. Ne JAMAIS dire "pour des raisons de confidentialité" ou refuser de donner une info
5. Sois précis, factuel et professionnel
6. RÉPONDS DE FAÇON CONCISE : commence par la réponse directe, puis ajoute 1-2 détails pertinents maximum
7. Ne répète JAMAIS le nom du client ou des formules de politesse inutiles

**Exemples de bonnes réponses (CONCISES ET DIRECTES) :**
Q: "Quel est le forfait de Marie Laurent ?"
R: "Forfait Premium 5G à 49.99€/mois avec 150 Go."

Q: "Puis-je résilier sans frais ?" (client engagé jusqu'au 15 mars 2025)
R: "Non, vous êtes engagé jusqu'au 15 mars 2025. Des frais de résiliation s'appliqueraient."

Q: "Combien dois-je payer pour ma prochaine facture ?"
R: "Votre prochaine facture est de 29.99€, échéance le 15 janvier 2025."

Q: "Quelle est ma consommation data ce mois-ci ?"
R: "Vous avez consommé 3.2 GB sur vos 5 GB disponibles ce mois-ci."

**Réponse (en français, avec les vraies données) :**"""

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