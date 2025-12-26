"""Définition du graph LangGraph pour orchestrer les agents."""

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from src.agents.supervisor import analyze_question
from src.agents.rag_agent import query_documents
from src.agents.data_agent import query_data


# ===== ÉTAT PARTAGÉ =====
class AgentState(TypedDict):
    """État partagé entre tous les nœuds du graph."""
    question: str           # Question de l'utilisateur
    next_action: str        # Quel agent appeler : "rag", "data", ou "end"
    context: str            # Contexte trouvé par les agents
    answer: str             # Réponse finale


# ===== NŒUD 1 : SUPERVISEUR =====
def supervisor_node(state: AgentState) -> AgentState:
    """
    Superviseur qui analyse la question et décide quel agent appeler.
    
    Args:
        state: État actuel
        
    Returns:
        État mis à jour avec next_action
    """
    # Utiliser le superviseur séparé
    decision = analyze_question(state["question"])
    state["next_action"] = decision
    
    return state


# ===== NŒUD 2 : RAG AGENT =====
def rag_agent_node(state: AgentState) -> AgentState:
    """
    Agent RAG qui interroge les PDFs avec FAISS.
    
    Args:
        state: État actuel
        
    Returns:
        État mis à jour avec answer
    """
    print("\n📚 RAG AGENT : Recherche dans les PDFs...")
    
    try:
        # Utiliser le vrai agent RAG
        result = query_documents(state["question"])
        state["answer"] = result["answer"]
        state["next_action"] = "end"
        
        print(f"✅ Réponse RAG générée")
        
    except Exception as e:
        print(f"❌ Erreur RAG Agent : {e}")
        state["answer"] = f"Désolé, une erreur s'est produite : {str(e)}"
        state["next_action"] = "end"
    
    return state


# ===== NŒUD 3 : DATA AGENT =====
def data_agent_node(state: AgentState) -> AgentState:
    """
    Agent Data qui interroge les Excel avec Pandas.
    
    Args:
        state: État actuel
        
    Returns:
        État mis à jour avec answer
    """
    print("\n📊 DATA AGENT : Recherche dans les données Excel...")
    
    try:
        # Utiliser le vrai agent Data
        answer = query_data(state["question"])
        state["answer"] = answer
        state["next_action"] = "end"
        
        print(f"✅ Réponse Data générée")
        
    except Exception as e:
        print(f"❌ Erreur Data Agent : {e}")
        state["answer"] = f"Désolé, une erreur s'est produite : {str(e)}"
        state["next_action"] = "end"
    
    return state


# ===== FONCTION DE ROUTAGE =====
def route_question(state: AgentState) -> Literal["rag_agent", "data_agent", "end"]:
    """
    Détermine le prochain nœud à appeler.
    
    Args:
        state: État actuel
        
    Returns:
        Nom du prochain nœud
    """
    next_action = state.get("next_action", "end")
    
    if next_action == "rag":
        return "rag_agent"
    elif next_action == "data":
        return "data_agent"
    else:
        return "end"


# ===== CRÉATION DU GRAPH =====
def create_graph():
    """
    Crée et retourne le graph LangGraph.
    
    Returns:
        Graph compilé prêt à être invoqué
    """
    print("\n🔧 Création du graph LangGraph...")
    
    # Créer le graph
    workflow = StateGraph(AgentState)
    
    # Ajouter les nœuds
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("rag_agent", rag_agent_node)
    workflow.add_node("data_agent", data_agent_node)
    
    # Définir le point d'entrée
    workflow.set_entry_point("supervisor")
    
    # Ajouter les transitions conditionnelles depuis le superviseur
    workflow.add_conditional_edges(
        "supervisor",
        route_question,
        {
            "rag_agent": "rag_agent",
            "data_agent": "data_agent",
            "end": END
        }
    )
    
    # Transitions depuis les agents vers la fin
    workflow.add_edge("rag_agent", END)
    workflow.add_edge("data_agent", END)
    
    # Compiler le graph
    app = workflow.compile()
    
    print("✅ Graph créé avec succès !")
    
    return app


# ===== TEST DU MODULE =====
if __name__ == "__main__":
    print("\n🚀 Test de graph.py avec les VRAIS agents\n")
    print("=" * 80)
    
    # Créer le graph
    app = create_graph()
    
    # Questions de test
    test_questions = [
        "Comment résilier mon abonnement ?",         # → RAG
        "Combien y a-t-il de clients au total ?",    # → DATA
    ]
    
    for question in test_questions:
        print(f"\n{'='*80}")
        print(f"❓ QUESTION : {question}")
        print(f"{'='*80}")
        
        # État initial
        initial_state = {
            "question": question,
            "next_action": "",
            "context": "",
            "answer": ""
        }
        
        # Invoquer le graph
        try:
            result = app.invoke(initial_state)
            print(f"\n💬 RÉPONSE FINALE :")
            print(result['answer'])
        except Exception as e:
            print(f"\n❌ ERREUR : {e}")
        
        print(f"\n{'='*80}\n")
    
    print("\n🎉 Test terminé !")