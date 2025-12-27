# Documentation Projet - Système Multi-Agent TelecomPlus

**Auteur :** Keita Mamadi
**Formation :** M2 IASD - Université Paris Dauphine
**Année :** 2025-2026
**Date :** Décembre 2025

---

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture du Système](#architecture-du-système)
3. [Choix Techniques et Justifications](#choix-techniques-et-justifications)
4. [Installation et Configuration](#installation-et-configuration)
5. [Utilisation](#utilisation)
6. [Résultats d'Évaluation](#résultats-dévaluation)
7. [Limitations et Améliorations Futures](#limitations-et-améliorations-futures)
8. [Structure du Projet](#structure-du-projet)

---

## 🎯 Vue d'ensemble

### Objectif du Projet

Développer un système multi-agent intelligent pour le support client de **TelecomPlus**, capable de :
- Répondre aux questions générales à partir de documents PDF (FAQ)
- Interroger des données clients structurées (fichiers Excel)
- Router intelligemment les questions vers l'agent approprié

### Solution Implémentée

**Architecture Multi-Agent avec LangGraph** comprenant :
- **Agent Superviseur** : Analyse et route les questions
- **Agent RAG** : Recherche dans 7 PDFs (FAQ TelecomPlus)
- **Agent Data** : Interroge 6 tables Excel (clients, forfaits, factures, etc.)

### Technologies Principales

- **LLM :** Google Gemini 2.0-flash
- **Framework :** LangChain + LangGraph
- **Embeddings :** HuggingFace (`paraphrase-MiniLM-L3-v2`)
- **Vector Store :** FAISS (local)
- **Monitoring :** Langfuse
- **Interface :** Streamlit

---

## 🏗️ Architecture du Système

### Schéma Global

```
┌─────────────────────────────────────────────────────────────┐
│                    UTILISATEUR                              │
│                  (Question en français)                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  AGENT SUPERVISEUR                          │
│  • Analyse la question avec LLM                             │
│  • Décide : "rag" ou "data"                                 │
│  • Monitoring Langfuse                                      │
└──────────────┬──────────────────────┬───────────────────────┘
               │                      │
       ┌───────▼────────┐    ┌───────▼────────┐
       │   AGENT RAG    │    │   AGENT DATA   │
       └────────────────┘    └────────────────┘
               │                      │
       ┌───────▼────────┐    ┌───────▼────────┐
       │  FAISS Index   │    │  Excel Files   │
       │  (7 PDFs)      │    │  (6 tables)    │
       │  81 chunks     │    │  176 lignes    │
       └────────────────┘    └────────────────┘
```

### Flux de Traitement

1. **Réception** : L'utilisateur pose une question via Streamlit
2. **Analyse** : Le superviseur détermine le type de question
3. **Routing** :
   - Questions générales → Agent RAG
   - Questions sur données clients → Agent Data
4. **Traitement** :
   - RAG : Recherche sémantique dans FAISS + génération LLM
   - Data : Extraction statistiques + génération LLM
5. **Réponse** : Retour à l'utilisateur avec sources

---

## 🔧 Choix Techniques et Justifications

### 1. Architecture Multi-Agent (LangGraph)

**Pourquoi ?**
- Séparation claire des responsabilités
- Scalabilité : facile d'ajouter de nouveaux agents
- Traçabilité : chaque agent peut être monitoré indépendamment

**Alternative considérée :** Agent unique avec ReAct
- ❌ Moins modulaire
- ❌ Difficile à maintenir
- ❌ Mixing de logiques différentes

### 2. RAG avec FAISS Local

**Pourquoi ?**
- **FAISS** : Rapide, gratuit, fonctionne offline
- **Embeddings locaux** (HuggingFace) : Pas de coût API
- **Chunks de 1000 caractères** : Bon équilibre précision/contexte

**Alternative considérée :** Pinecone/Weaviate
- ❌ Coût supplémentaire
- ❌ Nécessite connexion internet
- ✅ FAISS suffit pour 7 PDFs

### 3. Data Agent Sans Pandas Agent

**Pourquoi ?**
- **Pandas Agent expérimental** → bugs avec Gemini
- **Approche directe** : Plus fiable et rapide
- **Statistiques pré-calculées** : Moins de tokens consommés

**Évolution :**
- Version 1 : `create_pandas_dataframe_agent()` → ❌ Erreurs de parsing
- Version 2 : Requêtes LLM directes avec stats → ✅ Fonctionne

### 4. Google Gemini 2.0-flash

**Pourquoi ?**
- **Gratuit** : 1500 requêtes/jour
- **Rapide** : ~8s par réponse en moyenne
- **Multilingue** : Supporte français nativement
- **Disponible** : Via API simple

**Alternative considérée :** OpenAI GPT-4
- ❌ Payant dès la première requête
- ✅ Gemini suffisant pour le use case

### 5. Monitoring avec Langfuse

**Pourquoi ?**
- **Gratuit** pour usage étudiant
- **Cloud-based** : Pas d'infrastructure à gérer
- **Traces** : Input/Output de chaque agent
- **Métriques** : Latence, tokens, coûts

**Implémentation :**
- Client Langfuse initialisé dans `monitoring.py`
- Logging via `langfuse.span()` dans chaque agent
- Fonction `log_to_langfuse()` pour centraliser

### 6. Gestion de la Confidentialité

**Choix de conception :**
- Le Data Agent **refuse** de divulguer des données personnelles
- Répond de manière générale même avec accès aux données
- Redirige vers l'espace client pour informations sensibles

**Justification :**
- **Sécurité by design** : Pas d'authentification dans la démo
- **Conformité RGPD** : Protection des données personnelles
- **Production-ready** : Architecture préparée pour OAuth2/JWT

---

## 💻 Installation et Configuration

### Prérequis

- Python 3.10+
- Git
- Compte Google AI Studio (clé API gratuite)
- Compte Langfuse (optionnel, pour monitoring)

### 1. Cloner le Projet

```bash
git clone https://github.com/keita223/dauphine-project-iasd-2025.git
cd dauphine-project-iasd-2025
```

### 2. Créer l'Environnement Virtuel

```bash
# Créer le venv
python -m venv venv

# Activer (Windows)
.\venv\Scripts\activate

# Activer (Linux/Mac)
source venv/bin/activate
```

### 3. Installer les Dépendances

```bash
pip install -r requirements.txt
```

### 4. Configuration des Clés API

Créer un fichier `.env` à la racine :

```bash
# Google Gemini API
GOOGLE_API_KEY=votre_clé_google_ici

# Langfuse (optionnel)
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

**Obtenir une clé Google AI Studio :**
1. Aller sur https://aistudio.google.com/app/apikey
2. Créer une API key
3. Copier dans `.env`

### 5. Indexer les PDFs (Première fois uniquement)

```bash
python src/tools/pdf_tools.py
```

Résultat attendu :
```
📄 7 fichiers PDF trouvés
✂️  Découpage des documents en chunks...
✅ 81 chunks créés
💾 Index FAISS créé et sauvegardé
```

---

## 🚀 Utilisation

### Lancer l'Interface Streamlit

```bash
streamlit run app.py
```

L'application s'ouvre sur `http://localhost:8501`

### Exemples de Questions

**Questions pour le RAG Agent (PDFs) :**
```
- Comment résilier mon forfait ?
- Quels sont les tarifs de roaming en Europe ?
- Comment activer le roaming international ?
```

**Questions pour le Data Agent (Excel) :**
```
- Combien de clients avons-nous ?
- Combien de tickets support sont ouverts ?
- Combien de forfaits proposons-nous ?
```

### Tester les Agents Individuellement

**Test du RAG Agent :**
```bash
python -m src.agents.rag_agent
```

**Test du Data Agent :**
```bash
python -m src.agents.data_agent
```

**Test du Superviseur :**
```bash
python -m src.agents.supervisor
```

### Lancer l'Évaluation

```bash
python evaluate.py
```

Résultat attendu :
```
Total questions: 25
Total score: 25/25
Accuracy: 100.00%
Average response time: 8.24s
```

---

## 📊 Résultats d'Évaluation

### Performance Globale

| Métrique | Résultat |
|----------|----------|
| **Score total** | 25/25 (100%) |
| **Temps moyen** | 8.24 secondes |
| **Temps total** | 3min 26s |
| **Questions testées** | 25 |

### Résultats par Difficulté

| Difficulté | Score | Pourcentage |
|------------|-------|-------------|
| Facile | 7/7 | 100% |
| Moyen | 11/11 | 100% |
| Difficile | 3/3 | 100% |
| Très Difficile | 4/4 | 100% |

### Exemples de Réponses Réussies

**Question (Facile) :** "Comment consulter ma facture en ligne ?"
**Réponse :** "Vous pouvez consulter vos factures en vous connectant à votre espace client sur notre site web ou via l'application mobile. Toutes vos factures sont disponibles dans la section 'Mes factures' pendant 24 mois."
**Agent utilisé :** RAG
**Temps :** 8.08s

**Question (Moyen) :** "Y a-t-il des frais de résiliation si je suis engagé ?"
**Réponse :** "Oui, si vous êtes encore engagé, des frais égaux au montant des mensualités restantes peuvent s'appliquer."
**Agent utilisé :** RAG
**Temps :** 8.20s

**Question (Data) :** "Combien de clients avons-nous ?"
**Réponse :** "Il y a 20 clients au total."
**Agent utilisé :** Data
**Temps :** 5.50s

### Analyse des Performances

**Points forts :**
- ✅ Routing parfait du superviseur (100% de bonnes décisions)
- ✅ RAG trouve les bonnes sources même quand info absente
- ✅ Data Agent protège la confidentialité des données
- ✅ Temps de réponse acceptable (<10s en moyenne)

**Comportement intelligent :**
- Quand l'info n'existe pas → "Je n'ai pas trouvé cette information"
- Pour données sensibles → Redirige vers l'espace client
- Questions complexes → Conseils généraux pertinents

---

## ⚠️ Limitations et Améliorations Futures

### Limitations Connues

1. **Langue mixte dans les PDFs**
   - Certains PDFs contiennent du texte en anglais
   - Les embeddings peuvent avoir du mal à matcher français ↔ anglais
   - **Solution** : Traduire les PDFs ou utiliser des embeddings multilingues

2. **Pas d'authentification**
   - Le Data Agent ne peut pas donner de données personnelles
   - **Solution production** : Ajouter OAuth2/JWT pour identifier l'utilisateur

3. **Quota API limité**
   - Google Gemini free tier : 1500 req/jour
   - **Solution** : Passer à l'API payante ou utiliser un autre provider

4. **Monitoring Langfuse pas visible**
   - Les traces ne s'affichent pas dans l'UI Langfuse
   - Le code de monitoring est présent mais nécessite debug
   - **Impact** : Faible, le système fonctionne sans

### Améliorations Futures

1. **LLM-as-a-Judge pour l'évaluation**
   - Actuellement : Évaluation basique (0/1)
   - Amélioration : Utiliser un LLM pour noter les réponses (0-10)

2. **Mémoire conversationnelle**
   - Ajouter un historique des échanges
   - Permettre des questions de suivi

3. **Cache des embeddings**
   - Éviter de recalculer les embeddings à chaque requête
   - Gain de temps et de ressources

4. **Agent SQL**
   - Remplacer les Excel par une vraie base SQL
   - Requêtes plus complexes et performantes

5. **Fine-tuning du modèle**
   - Adapter Gemini au domaine télécom
   - Améliorer la précision des réponses

---

## 📁 Structure du Projet

```
dauphine-project-iasd-2025/
│
├── data/                          # Données du projet
│   ├── pdfs/                      # 7 documents FAQ (indexés dans FAISS)
│   ├── xlsx/                      # 6 tables Excel (clients, forfaits, etc.)
│   ├── faiss_index/               # Index vectoriel FAISS (généré)
│   └── evaluation_questions.xlsx  # 25 questions d'évaluation
│
├── src/                           # Code source
│   ├── agents/                    # Agents intelligents
│   │   ├── __init__.py
│   │   ├── supervisor.py          # Agent superviseur (routing)
│   │   ├── rag_agent.py           # Agent RAG (recherche PDFs)
│   │   └── data_agent.py          # Agent Data (requêtes Excel)
│   │
│   ├── tools/                     # Outils et utilitaires
│   │   ├── __init__.py
│   │   ├── pdf_tools.py           # Indexation FAISS
│   │   └── excel_tools.py         # Chargement Excel
│   │
│   ├── utils/                     # Utilitaires
│   │   ├── __init__.py
│   │   └── monitoring.py          # Configuration Langfuse
│   │
│   ├── config.py                  # Configuration centralisée
│   ├── graph.py                   # Graph LangGraph (multi-agent)
│   └── main.py                    # Point d'entrée (test CLI)
│
├── app.py                         # Interface Streamlit
├── evaluate.py                    # Script d'évaluation
├── requirements.txt               # Dépendances Python
├── .env                           # Variables d'environnement (à créer)
├── .gitignore                     # Fichiers à ignorer
├── README.md                      # Documentation du professeur
└── README_PROJET.md               # Cette documentation

```

### Rôle des Fichiers Principaux

| Fichier | Rôle |
|---------|------|
| `app.py` | Interface utilisateur Streamlit |
| `src/graph.py` | Orchestration LangGraph des agents |
| `src/agents/supervisor.py` | Décide quel agent appeler |
| `src/agents/rag_agent.py` | Recherche dans les PDFs |
| `src/agents/data_agent.py` | Interroge les données Excel |
| `src/tools/pdf_tools.py` | Indexation FAISS des PDFs |
| `src/utils/monitoring.py` | Monitoring Langfuse |
| `evaluate.py` | Évaluation automatique du système |

---

## 🎓 Compétences Démontrées

### Techniques

- ✅ Architecture multi-agent avec LangGraph
- ✅ RAG (Retrieval-Augmented Generation)
- ✅ Vector stores (FAISS)
- ✅ Embeddings locaux (HuggingFace)
- ✅ Prompt engineering
- ✅ LLM orchestration
- ✅ Monitoring et observabilité
- ✅ Gestion de la confidentialité

### Pratiques de Développement

- ✅ Code structuré et modulaire
- ✅ Documentation complète
- ✅ Gestion de configuration (`.env`)
- ✅ Tests unitaires des agents
- ✅ Évaluation automatisée
- ✅ Gestion de version (Git)
- ✅ Interface utilisateur (Streamlit)

---

## 📞 Contact

**Keita Mamadi**
M2 IASD - Université Paris Dauphine
GitHub : https://github.com/keita223/dauphine-project-iasd-2025

---

**Université Paris Dauphine - IASD 2025-2026**
