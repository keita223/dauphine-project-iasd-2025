"""Agent RAG pour interroger les documents PDF avec FAISS."""

from pathlib import Path
from langchain_anthropic import ChatAnthropic
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from src.config import ANTHROPIC_API_KEY, FAISS_INDEX_PATH
from src.utils.monitoring import get_langfuse_handler, log_to_langfuse


def load_faiss_index():
    """
    Charge l'index FAISS depuis le disque.
    
    Returns:
        FAISS vectorstore ou None si échec
    """
    print("📂 Chargement de l'index FAISS...")
    
    if not FAISS_INDEX_PATH.exists():
        print(f"❌ Index FAISS non trouvé : {FAISS_INDEX_PATH}")
        print("💡 Exécutez d'abord : python -m src.tools.pdf_tools")
        return None
    
    try:
        # Créer les mêmes embeddings que lors de la création
        embeddings = HuggingFaceEmbeddings(
            model_name="paraphrase-MiniLM-L3-v2",
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Charger l'index
        vectorstore = FAISS.load_local(
            str(FAISS_INDEX_PATH),
            embeddings,
            allow_dangerous_deserialization=True  # Nécessaire pour charger l'index
        )
        
        print("✅ Index FAISS chargé avec succès")
        return vectorstore
    
    except Exception as e:
        print(f"❌ Erreur lors du chargement de l'index : {e}")
        return None


def create_rag_chain(vectorstore):
    """
    Crée une chaîne RAG (Retrieval-Augmented Generation).

    Args:
        vectorstore: Index FAISS chargé

    Returns:
        Chaîne RAG configurée
    """
    print("🔗 Création de la chaîne RAG...")

    # Créer le LLM Claude
    llm = ChatAnthropic(
        model="claude-3-haiku-20240307",
        api_key=ANTHROPIC_API_KEY,
        temperature=0
    )

    # Template de prompt pour le RAG (optimisé pour réponses directes)
    template = """Tu es un conseiller client TelecomPlus. Réponds directement à la question du client.

RÈGLES STRICTES :
1. Réponds DIRECTEMENT sans introduction ("Voici", "Selon le contexte", etc.)
2. NE MENTIONNE JAMAIS "le contexte", "la documentation", "Q30", "FAQ"
3. Parle comme si tu connaissais naturellement l'information
4. Sois concis et professionnel
5. Si l'info n'existe pas, dis simplement "Je n'ai pas cette information."

EXEMPLES DE BONNES RÉPONSES :
- "Vous pouvez consulter vos factures dans votre espace client, section 'Mes factures'."
- "La résiliation est gratuite hors engagement. Si vous êtes engagé, des frais peuvent s'appliquer."

EXEMPLES DE MAUVAISES RÉPONSES (À ÉVITER) :
- "Voici les informations pertinentes..." ❌
- "Selon le contexte fourni..." ❌
- "Q30. Comment consulter..." ❌

Contexte :
{context}

Question : {question}

Réponse :"""

    prompt = ChatPromptTemplate.from_template(template)

    # Créer le retriever avec k augmenté pour meilleur recall
    retriever = vectorstore.as_retriever(search_kwargs={"k": 7})

    # Créer la chaîne RAG avec LCEL (LangChain Expression Language)
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    print("✅ Chaîne RAG créée avec succès")
    return rag_chain, retriever


def query_documents(question: str) -> dict:
    """
    Interroge les documents PDF avec une question.

    Args:
        question: Question en langage naturel

    Returns:
        dict avec 'answer' et 'source_documents'
    """
    print(f"\n🔍 Recherche pour : {question}")

    # Initialiser Langfuse pour le monitoring
    langfuse = get_langfuse_handler()

    # Charger l'index
    vectorstore = load_faiss_index()

    if vectorstore is None:
        return {
            "answer": "❌ L'index FAISS n'est pas disponible. Veuillez d'abord indexer les PDFs.",
            "source_documents": []
        }

    # Créer la chaîne RAG
    rag_chain, retriever = create_rag_chain(vectorstore)

    # Poser la question
    try:
        # Récupérer les documents sources
        source_docs = retriever.invoke(question)

        # Obtenir la réponse
        answer = rag_chain.invoke(question)

        # Afficher les sources
        print("\n📚 Sources utilisées :")
        for i, doc in enumerate(source_docs, 1):
            source = doc.metadata.get("source", "Unknown")
            print(f"   {i}. {Path(source).name}")

        # Logger dans Langfuse si disponible
        log_to_langfuse(
            langfuse,
            name="rag_query",
            input_data={"question": question},
            output_data={"answer": answer[:100], "num_sources": len(source_docs)},
            metadata={"agent": "rag_agent"}
        )

        return {
            "answer": answer,
            "source_documents": source_docs
        }

    except Exception as e:
        print(f"❌ Erreur lors de la recherche : {e}")

        # Logger l'erreur dans Langfuse si disponible
        log_to_langfuse(
            langfuse,
            name="rag_query_error",
            input_data={"question": question},
            output_data={"error": str(e)},
            metadata={"agent": "rag_agent", "status": "error"}
        )

        return {
            "answer": f"❌ Erreur : {str(e)}",
            "source_documents": []
        }


# Test du module
if __name__ == "__main__":
    print("\n🚀 Test de rag_agent.py\n")
    
    # Questions de test
    questions = [
        "Quels sont les modes de paiement acceptés ?",
        "Comment résilier mon forfait ?",
        "Quels sont les frais de roaming en Europe ?",
    ]
    
    for question in questions:
        print("\n" + "="*80)
        print(f"❓ Question : {question}")
        print("="*80)
        
        result = query_documents(question)
        
        print(f"\n💬 Réponse :")
        print(result["answer"])
        print("\n" + "="*80)
    
    print("\n🎉 RAG Agent testé avec succès !")