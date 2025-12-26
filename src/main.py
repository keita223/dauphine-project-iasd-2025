"""Main module for the TelecomPlus multi-agent support system."""

from src.graph import create_graph


# Cache pour éviter de recréer le graph à chaque appel
_graph_instance = None


def get_graph():
    """
    Retourne l'instance du graph (singleton pattern).
    
    Returns:
        Graph LangGraph compilé
    """
    global _graph_instance
    
    if _graph_instance is None:
        print("🔧 Initialisation du système multi-agent...")
        _graph_instance = create_graph()
        print("✅ Système prêt !")
    
    return _graph_instance


def answer(question: str) -> str:
    """Answer customer questions using RAG and SQL agents.

    Cette fonction est le point d'entrée principal du système.
    Elle route la question vers l'agent approprié (RAG ou Data)
    via le superviseur LangGraph.

    Args:
        question: Customer question in French

    Returns:
        Answer string
    """
    # Obtenir le graph multi-agent
    app = get_graph()
    
    # État initial
    initial_state = {
        "question": question,
        "next_action": "",
        "context": "",
        "answer": ""
    }
    
    try:
        # Invoquer le graph multi-agent
        result = app.invoke(initial_state)
        return result.get('answer', 'Désolé, je n\'ai pas pu générer de réponse.')
        
    except Exception as e:
        error_msg = f"Erreur lors du traitement : {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg


# Test interactif (optionnel)
if __name__ == "__main__":
    print("\n🤖 SYSTÈME MULTI-AGENT TELECOMPLUS")
    print("=" * 80)
    print("\nPosez vos questions (tapez 'quit' pour quitter)\n")
    
    while True:
        user_question = input("❓ Votre question : ").strip()
        
        if user_question.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Au revoir !")
            break
        
        if not user_question:
            continue
        
        print("\n🔍 Traitement en cours...\n")
        response = answer(user_question)
        print(f"💬 Réponse : {response}\n")
        print("-" * 80 + "\n")