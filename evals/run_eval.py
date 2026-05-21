import json
import sys
import os
import requests
import mlflow
import mlflow.sklearn
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_URL = "http://localhost:8000"

def load_golden_dataset(path: str):
    with open(path) as f:
        return json.load(f)

def keyword_score(answer: str, keywords: list) -> float:
    answer_lower = answer.lower()
    hits = sum(1 for kw in keywords if kw.lower() in answer_lower)
    return round(hits / len(keywords), 2)

def citation_score(citations: list, expected_page: int) -> float:
    for cite in citations:
        if cite.get("page") == expected_page:
            return 1.0
    return 0.0

def llm_judge(question: str, answer: str) -> float:
    prompt = f"""You are an evaluator. Rate this answer from 0.0 to 1.0 based on how well it answers the question.
Return ONLY a number between 0.0 and 1.0, nothing else.

Question: {question}
Answer: {answer}

Score:"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral:7b", "prompt": prompt, "stream": False},
            timeout=60,
        )
        score_str = response.json().get("response", "0").strip()
        return min(1.0, max(0.0, float(score_str)))
    except Exception:
        return 0.0

def run_evaluation(dataset_path: str, use_reranker: bool = True):
    dataset = load_golden_dataset(dataset_path)
    results = []

    mlflow.set_experiment("doc-intelligence-eval")

    run_name = f"{'with_reranker' if use_reranker else 'no_reranker'}_{datetime.now().strftime('%H%M%S')}"

    with mlflow.start_run(run_name=run_name):
        mlflow.log_param("use_reranker", use_reranker)
        mlflow.log_param("dataset_size", len(dataset))
        mlflow.log_param("model", "mistral:7b")
        mlflow.log_param("embeddings", "BAAI/bge-base-en-v1.5")

        keyword_scores = []
        citation_scores = []
        judge_scores = []

        for i, item in enumerate(dataset):
            print(f"Evaluating {i+1}/{len(dataset)}: {item['question'][:50]}...")

            try:
                response = requests.post(
                    f"{API_URL}/query",
                    json={"question": item["question"]},
                    timeout=120,
                )
                data = response.json()
                answer = data.get("answer", "")
                citations = data.get("citations", [])
            except Exception as e:
                print(f"  Error: {e}")
                answer = ""
                citations = []

            ks = keyword_score(answer, item["expected_keywords"])
            cs = citation_score(citations, item["page"])
            js = llm_judge(item["question"], answer)

            keyword_scores.append(ks)
            citation_scores.append(cs)
            judge_scores.append(js)

            results.append({
                "question": item["question"],
                "answer": answer[:200],
                "keyword_score": ks,
                "citation_score": cs,
                "judge_score": js,
            })

            print(f"  keyword={ks:.2f} citation={cs:.2f} judge={js:.2f}")

        avg_keyword = sum(keyword_scores) / len(keyword_scores)
        avg_citation = sum(citation_scores) / len(citation_scores)
        avg_judge = sum(judge_scores) / len(judge_scores)

        mlflow.log_metric("avg_keyword_score", avg_keyword)
        mlflow.log_metric("avg_citation_score", avg_citation)
        mlflow.log_metric("avg_judge_score", avg_judge)

        print(f"\n{'='*50}")
        print(f"RESULTS — {run_name}")
        print(f"{'='*50}")
        print(f"Avg keyword score:  {avg_keyword:.2f}")
        print(f"Avg citation score: {avg_citation:.2f}")
        print(f"Avg judge score:    {avg_judge:.2f}")
        print(f"{'='*50}\n")

        results_path = f"evals/results_{run_name}.json"
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)
        mlflow.log_artifact(results_path)

    return results

if __name__ == "__main__":
    run_evaluation("evals/golden_dataset.json", use_reranker=True)
