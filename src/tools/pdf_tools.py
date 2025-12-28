"""Outils pour indexer et rechercher dans les documents PDF avec FAISS."""

from pathlib import Path
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from src.config import PDF_DIR, FAISS_INDEX_PATH


def load_pdfs() -> List:
    """
    Charge tous les PDFs depuis le dossier PDF_DIR.

    Returns:
        List: Liste de documents chargés
    """
    print(f"📂 Chargement des PDFs depuis: {PDF_DIR}")

    documents = []
    pdf_files = list(PDF_DIR.glob("*.pdf"))

    print(f"📄 {len(pdf_files)} fichiers PDF trouvés")

    for pdf_file in pdf_files:
        print(f"   → Chargement de {pdf_file.name}")

        try:
            loader = PyPDFLoader(str(pdf_file))
            pdf_docs = loader.load()
            documents.extend(pdf_docs)
        except Exception as e:
            print(f"❌ Erreur lors du chargement de {pdf_file.name}: {e}")
            continue

    print(f"✅ {len(documents)} pages chargées au total")
    return documents


def split_documents(documents: List) -> List:
    """
    Découpe les documents en chunks.
    
    Args:
        documents: Liste de documents à découper
        
    Returns:
        List: Liste de chunks
    """
    print("✂️  Découpage des documents en chunks...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"✅ {len(chunks)} chunks créés")
    
    return chunks


def create_faiss_index(chunks: List):
    """
    Crée un index FAISS à partir des chunks.
    """
    print("🔢 Création des embeddings avec HuggingFace...")
    
    # Utilisation d'un modèle d'embeddings local (gratuit et rapide)
    embeddings = HuggingFaceEmbeddings(
        model_name="paraphrase-MiniLM-L3-v2",  # Plus petit et plus rapide
        encode_kwargs={'normalize_embeddings': True}
    )
    
    print("💾 Création de l'index FAISS...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    print("✅ Index FAISS créé avec succès")
    return vectorstore


def save_faiss_index(vectorstore):
    """
    Sauvegarde l'index FAISS sur le disque.
    
    Args:
        vectorstore: Index FAISS à sauvegarder
    """
    # Créer le dossier si nécessaire
    FAISS_INDEX_PATH.mkdir(parents=True, exist_ok=True)
    
    print(f"💾 Sauvegarde de l'index dans: {FAISS_INDEX_PATH}")
    vectorstore.save_local(str(FAISS_INDEX_PATH))
    print("✅ Index sauvegardé avec succès")


# Test du module
if __name__ == "__main__":
    print("\n🚀 Test de pdf_tools.py\n")
    
    # 1. Charger les PDFs
    documents = load_pdfs()
    
    # 2. Découper en chunks
    chunks = split_documents(documents)
    
    # 3. Créer l'index FAISS
    vectorstore = create_faiss_index(chunks)
    
    # 4. Sauvegarder l'index
    save_faiss_index(vectorstore)
    
    print("\n Index FAISS créé et sauvegardé avec succès !")