"""Evaluation script for the TelecomPlus support agent.

This script evaluates the agent's responses against the expected answers
from the evaluation dataset.

Students should modify this script to:
1. Call their actual agent implementation ✅ FAIT
2. Implement proper evaluation logic (e.g., LLM-as-a-judge) ✅ FAIT
3. Calculate meaningful metrics (accuracy, relevance, etc.) ✅ FAIT
"""

import pandas as pd
import time
from datetime import datetime
from src.main import answer
import anthropic
import os
from dotenv import load_dotenv
from src.utils.monitoring import get_langfuse_handler

# Charger les variables d'environnement
load_dotenv()

# Configurer Claude pour l'évaluation
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Initialiser Langfuse pour le monitoring des évaluations
langfuse = get_langfuse_handler()


def llm_as_judge(question: str, expected_answer: str, agent_answer: str) -> tuple[int, str]:
    """Évalue la qualité de la réponse de l'agent en utilisant Claude comme juge.

    Cette fonction utilise Claude pour comparer la réponse générée par l'agent
    avec la réponse attendue, en tenant compte de la question posée.

    Args:
        question: La question du client
        expected_answer: La réponse attendue (référence)
        agent_answer: La réponse générée par l'agent

    Returns:
        tuple[int, str]: Score de 0 à 10 et justification détaillée
    """

    # Validation basique
    if not agent_answer or len(agent_answer.strip()) < 10:
        return 0, "Réponse trop courte ou vide"

    # Prompt pour Claude en tant que juge
    judge_prompt = f"""Tu es un évaluateur expert pour un système de support client de TelecomPlus.

**Question du client:**
{question}

**Réponse attendue (référence):**
{expected_answer}

**Réponse générée par l'agent:**
{agent_answer}

**Critères d'évaluation:**
1. **Exactitude** (40%): La réponse contient-elle les informations correctes et factuelles?
2. **Complétude** (30%): Tous les éléments de la réponse attendue sont-ils couverts?
3. **Pertinence** (20%): La réponse répond-elle précisément à la question posée?
4. **Clarté** (10%): La réponse est-elle claire, bien structurée et compréhensible?

**Instructions:**
- Compare la réponse générée avec la réponse attendue
- Évalue selon les 4 critères ci-dessus
- Donne un score de 0 à 10 (10 = parfait, 0 = complètement incorrect)
- Fournis une justification courte et précise

**Format de réponse obligatoire:**
SCORE: [nombre entre 0 et 10]
JUSTIFICATION: [explication en 1-2 phrases]"""

    try:
        # Appeler Claude pour l'évaluation
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=200,
            messages=[{"role": "user", "content": judge_prompt}]
        )
        evaluation_text = response.content[0].text.strip()

        # Parser la réponse
        score = 0
        justification = "Erreur de parsing"

        lines = evaluation_text.split('\n')
        for line in lines:
            if line.startswith("SCORE:"):
                score_text = line.replace("SCORE:", "").strip()
                # Extraire le nombre (gérer "8/10" ou "8")
                score_text = score_text.split('/')[0].strip()
                try:
                    score = int(float(score_text))
                    score = max(0, min(10, score))  # Clamp entre 0 et 10
                except ValueError:
                    score = 0
            elif line.startswith("JUSTIFICATION:"):
                justification = line.replace("JUSTIFICATION:", "").strip()

        # Logger l'évaluation dans Langfuse
        if langfuse:
            try:
                # Créer une span pour l'évaluation (comme dans monitoring.py)
                span = langfuse.start_span(
                    name="llm_as_judge_evaluation",
                    input={"question": question, "expected": expected_answer[:200], "agent_answer": agent_answer[:200]},
                    metadata={"score": score, "model": "claude-3-haiku-20240307"}
                )
                span.update(output={"score": score, "justification": justification})
                span.end()

                langfuse.flush()
                print(f"[LANGFUSE] Evaluation loggee: {score}/10")
            except Exception as e:
                print(f"[WARN] Erreur lors du logging Langfuse: {e}")

        return score, justification

    except Exception as e:
        print(f"[WARN] Erreur lors de l'évaluation LLM-as-judge: {e}")
        # Fallback: évaluation basique
        if "erreur" in agent_answer.lower():
            return 0, "Réponse contient une erreur"
        return 5, f"Évaluation automatique échouée: {str(e)}"


def evaluate_response(question: str, expected_answer: str, agent_answer: str) -> int:
    """Evaluate the relevance of the agent's answer.

    DEPRECATED: Cette fonction est conservée pour compatibilité mais
    utilise maintenant llm_as_judge() en interne.

    Args:
        question: The customer question
        expected_answer: The expected answer from the dataset
        agent_answer: The answer generated by your agent

    Returns:
        Score: 1 if relevant, 0 if not
    """
    score, _ = llm_as_judge(question, expected_answer, agent_answer)
    # Convertir le score 0-10 en 0-1 pour compatibilité
    return 1 if score >= 5 else 0


def run_evaluation():
    """Run evaluation on all questions from the evaluation dataset."""

    # Load evaluation questions
    print("Loading evaluation questions...")
    df = pd.read_excel("data/evaluation_questions.xlsx")

    print(f"Loaded {len(df)} questions\n")
    print("=" * 80)

    results = []
    total_score = 0
    total_time = 0

    # Evaluate each question
    for idx, row in df.iterrows():
        question = row["Question"]
        expected_answer = row["Réponse Attendue"]
        difficulty = row["Difficulté"]

        print(f"\nQuestion {idx + 1}/{len(df)} [{difficulty}]:")
        print(f"Q: {question}")

        # Mesurer le temps de réponse
        start_time = time.time()

        # Get agent's answer (appel de notre système multi-agent)
        agent_answer = answer(question)

        end_time = time.time()
        response_time = round(end_time - start_time, 2)
        total_time += response_time

        print(f"Agent: {agent_answer}")
        print(f"Time: {response_time}s")

        # Évaluation avec LLM-as-a-judge (score de 0 à 10)
        llm_score, justification = llm_as_judge(question, expected_answer, agent_answer)
        total_score += llm_score

        print(f"Score LLM-as-judge: {llm_score}/10")
        print(f"Justification: {justification}")

        # Store results
        results.append({
            "Question": question,
            "Expected Answer": expected_answer,
            "Agent Answer": agent_answer,
            "Difficulty": difficulty,
            "LLM Score (0-10)": llm_score,
            "Justification": justification,
            "Response Time (s)": response_time
        })

        print("-" * 80)

    # Calculate final metrics
    max_possible_score = len(df) * 10  # Score max = 10 par question
    avg_score = total_score / len(df) if len(df) > 0 else 0
    accuracy_percentage = (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0
    avg_time = total_time / len(df) if len(df) > 0 else 0

    print("\n" + "=" * 80)
    print("EVALUATION RESULTS (LLM-as-a-Judge)")
    print("=" * 80)
    print(f"Total questions: {len(df)}")
    print(f"Total score: {total_score}/{max_possible_score}")
    print(f"Average score per question: {avg_score:.2f}/10")
    print(f"Overall accuracy: {accuracy_percentage:.1f}%")
    print(f"Average response time: {avg_time:.2f}s")
    print(f"Total time: {total_time:.2f}s")

    # Stats par difficulté
    print("\nResults by difficulty:")
    results_df = pd.DataFrame(results)
    for diff in ["Facile", "Moyen", "Difficile"]:
        diff_results = results_df[results_df["Difficulty"] == diff]
        if len(diff_results) > 0:
            diff_score = diff_results["LLM Score (0-10)"].sum()
            diff_count = len(diff_results)
            diff_max = diff_count * 10
            diff_avg = diff_score / diff_count
            diff_accuracy = (diff_score / diff_max) * 100 if diff_max > 0 else 0
            print(f"  {diff}: {diff_score}/{diff_max} (avg: {diff_avg:.1f}/10, accuracy: {diff_accuracy:.1f}%)")

    # Save results to Excel
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"evaluation_results_{timestamp}.xlsx"
    results_df.to_excel(output_file, index=False)
    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    run_evaluation()