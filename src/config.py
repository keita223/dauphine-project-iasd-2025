"""Configuration module for loading environment variables and settings."""
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
# Chemins des dossiers de données
PROJECT_ROOT=Path(__file__).parent.parent
DATA_DIR=PROJECT_ROOT/"data"
PDFS_DIR=PROJECT_ROOT/"pdfs"