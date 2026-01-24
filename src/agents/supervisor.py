"""Agent superviseur qui décide quel agent appeler."""

from langchain_anthropic import ChatAnthropic
from src.config import ANTHROPIC_API_KEY
from src.utils.monitoring import get_langfuse_handler, log_to_langfuse


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

    # Créer le LLM Claude
    llm = ChatAnthropic(
        model="claude-3-haiku-20240307",
        api_key=ANTHROPIC_API_KEY,
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
        log_to_langfuse(
            langfuse,
            name="supervisor_decision",
            input_data={"question": question},
            output_data={"decision": decision},
            metadata={"agent": "supervisor"}
        )

        return decision

    except Exception as e:
        print(f"❌ Erreur superviseur : {e}")
        print("⚠️ Fallback sur 'rag'")

        # Logger l'erreur dans Langfuse si disponible
        log_to_langfuse(
            langfuse,
            name="supervisor_error",
            input_data={"question": question},
            output_data={"error": str(e), "fallback": "rag"},
            metadata={"agent": "supervisor", "status": "error"}
        )

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