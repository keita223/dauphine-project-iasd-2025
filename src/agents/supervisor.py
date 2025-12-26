"""Agent superviseur qui décide quel agent appeler."""

from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import GOOGLE_API_KEY, MODEL_NAME
from src.utils.monitoring import get_langfuse_handler


def analyze_question(question: str) -> str:
    """
    Analyse une question et décide quel agent appeler.

    Args:
        question: Question de l'utilisateur

    Returns:
        "rag" ou "data" selon le type de question
    """
    print(f"\n🧠 SUPERVISEUR : Analyse de '{question[:50]}...'")

    # Initialiser Langfuse pour le monitoring
    langfuse = get_langfuse_handler()

    # Créer le LLM
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=GOOGLE_API_KEY,
        temperature=0
    )

    # Prompt pour la décision
    prompt = f"""Tu es un superviseur intelligent pour TelecomPlus, un opérateur télécom.

Analyse la question et décide quel agent appeler :

**Agent RAG (rag)** - Pour les questions sur :
- FAQ et documentation générale
- Procédures : résiliation, modification, activation
- Informations produits : forfaits disponibles, options, tarifs généraux
- Support technique : problèmes réseau, configuration, dépannage
- Roaming international : tarifs, zones, activation
- Modes de paiement acceptés
- Catalogue de téléphones
- Toute question générale sur les services

**Agent DATA (data)** - Pour les questions sur des données clients spécifiques :
- Informations d'UN client nommé (ex: "forfait de Jean Dupont")
- Factures d'un client spécifique
- Consommation d'un client
- Tickets support d'une personne précise
- Statistiques globales (nombre total de clients, factures en attente, etc.)

IMPORTANT :
- Si la question mentionne un NOM de client → "data"
- Si la question demande des STATISTIQUES globales → "data"
- Si la question est GÉNÉRALE sur les services → "rag"

Question : {question}

Réponds UNIQUEMENT par "rag" ou "data" (un seul mot, pas d'explication).
"""

    try:
        response = llm.invoke(prompt)
        decision = response.content.strip().lower()

        # Validation
        if decision not in ["rag", "data"]:
            print(f"⚠️ Décision invalide '{decision}', fallback sur 'rag'")
            decision = "rag"

        print(f"✅ Décision : Agent {decision.upper()}")

        # Logger dans Langfuse si disponible
        if langfuse:
            try:
                langfuse.span(
                    name="supervisor_decision",
                    input={"question": question},
                    output={"decision": decision},
                    metadata={"agent": "supervisor"}
                )
            except:
                pass  # Ignore si erreur de logging

        return decision

    except Exception as e:
        print(f"❌ Erreur superviseur : {e}")
        print("⚠️ Fallback sur 'rag'")

        # Logger l'erreur dans Langfuse si disponible
        if langfuse:
            try:
                langfuse.span(
                    name="supervisor_error",
                    input={"question": question},
                    output={"error": str(e), "fallback": "rag"},
                    metadata={"agent": "supervisor", "status": "error"}
                )
            except:
                pass

        return "rag"  # Fallback par défaut


# Test du module
if __name__ == "__main__":
    print("\n🚀 Test de supervisor.py\n")
    
    # Questions de test
    test_questions = [
        "Comment résilier mon abonnement ?",              # → rag
        "Quels sont les forfaits disponibles ?",          # → rag
        "Quel est le forfait de Jean Dupont ?",           # → data
        "Combien y a-t-il de clients au total ?",         # → data
        "Comment activer le roaming en Europe ?",         # → rag
        "Quels sont les modes de paiement acceptés ?",    # → rag
        "Quelle est la facture de Sophie Martin ?",       # → data
    ]
    
    for question in test_questions:
        print("\n" + "=" * 80)
        decision = analyze_question(question)
        print(f"Question : {question}")
        print(f"Décision : {decision}")
        print("=" * 80)
    
    print("\n🎉 Superviseur testé avec succès !")