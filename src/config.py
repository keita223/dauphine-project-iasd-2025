"""Configuration module for loading environment variables and settings."""
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
# Chemins des dossiers de données
PROJECT_ROOT=Path(__file__).parent.parent
DATA_DIR=PROJECT_ROOT/"data"
PDF_DIR = DATA_DIR / "pdfs"  
FAISS_INDEX_PATH = DATA_DIR / "faiss_index"
XLSX_DIR = DATA_DIR / "xlsx"  # Dossier des Excel

# Fichiers Excel des tables de données
EXCEL_FILES = {
    "clients": XLSX_DIR / "clients.xlsx",
    "forfaits": XLSX_DIR / "forfaits.xlsx",
    "abonnements": XLSX_DIR / "abonnements.xlsx",
    "consommation": XLSX_DIR / "consommation.xlsx",
    "factures": XLSX_DIR / "factures.xlsx",
    "tickets": XLSX_DIR / "tickets_support.xlsx",
}
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")

# Paramètres du modèle
MODEL_NAME = "gemini-2.0-flash"  # Modèle 2.0-flash avec quota séparé (rapide et gratuit)
TEMPERATURE = 0.0
MAX_TOKENS = 1024