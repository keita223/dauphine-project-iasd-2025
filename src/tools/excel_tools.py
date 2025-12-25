"""Outils pour interroger les fichiers Excel avec Pandas."""

import pandas as pd
from typing import Dict
from src.config import DATA_DIR


def load_excel_files() -> Dict[str, pd.DataFrame]:
    """
    Charge tous les fichiers Excel dans un dictionnaire de DataFrames.
    
    Returns:
        Dict[str, pd.DataFrame]: Dictionnaire {nom_table: DataFrame}
    """
    print("📊 Chargement des fichiers Excel...")
    
    xlsx_dir = DATA_DIR / "xlsx"
    
    excel_files = {
        "clients": xlsx_dir / "clients.xlsx",
        "forfaits": xlsx_dir / "forfaits.xlsx",
        "abonnements": xlsx_dir / "abonnements.xlsx",
        "consommation": xlsx_dir / "consommation.xlsx",
        "factures": xlsx_dir / "factures.xlsx",
        "tickets": xlsx_dir / "tickets_support.xlsx",
    }
    
    dataframes = {}
    
    for name, filepath in excel_files.items():
        if filepath.exists():
            df = pd.read_excel(filepath)
            dataframes[name] = df
            print(f"   ✅ {name}: {len(df)} lignes chargées")
        else:
            print(f"   ⚠️ {name}: fichier non trouvé ({filepath})")
    
    print(f"✅ {len(dataframes)} tables chargées au total\n")
    return dataframes


def get_table_info(dataframes: Dict[str, pd.DataFrame]) -> str:
    """
    Génère une description des tables disponibles.
    
    Args:
        dataframes: Dictionnaire des DataFrames
        
    Returns:
        str: Description formatée des tables
    """
    info = "📋 Tables disponibles:\n\n"
    
    for name, df in dataframes.items():
        info += f"**{name}** ({len(df)} lignes)\n"
        info += f"Colonnes: {', '.join(df.columns.tolist())}\n"
        info += f"Aperçu: {df.head(2).to_dict('records')}\n\n"
    
    return info


# Test du module
if __name__ == "__main__":
    print("\n🚀 Test de excel_tools.py\n")
    
    # Charger les fichiers Excel
    dataframes = load_excel_files()
    
    # Afficher les informations
    info = get_table_info(dataframes)
    print(info)
    
    # Quelques statistiques
    print("📊 Statistiques:")
    for name, df in dataframes.items():
        print(f"   {name}: {len(df)} lignes, {len(df.columns)} colonnes")
    
    print("\n🎉 Excel tools testés avec succès !")