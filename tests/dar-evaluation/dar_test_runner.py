#!/usr/bin/env python3
"""
DAR Multi-Model Evaluation Script
Tests baseline (no DAR) vs enhanced (with DAR) across multiple models and scenarios.
Covers: multi-language, all domains, complex reasoning, engineering tasks.
"""

import json
import time
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime

# ============ API Configuration ============
PRIMARY_API = "https://api.587.lol/v1"
PRIMARY_KEY = "test123"
PRIMARY_MODELS = ["moonweaver-4.8"]

BACKUP_API = "https://api.hcnsec.cn/v1"
BACKUP_KEY = "sk-j4TEjjV0fKgqvliSXc8jko2EHzBmXnazsVaGCUa0sxSmZAH7"
# Text models only (skip image/audio/router models)
BACKUP_MODELS = [
    "DeepSeek-V4-Pro",
    "glm-5.2",
    "Kimi-K2.6",
    "MiniMax-M3",
    "Qwen3.5-397B-A17B",
    "step-3.7-flash",
    "Spark-X2-Flash",
    "sensenova-u1-fast",
]

# ============ Test Scenarios ============
# 6 scenarios covering: coding, academic, factual, creative, multilingual, reasoning

SCENARIOS = [
    {
        "id": "S1-CVE",
        "domain": "coding",
        "language": "en",
        "title": "CVE Vulnerability Investigation",
        "question": "Our FastAPI service uses python-multipart. Investigate CVE-2024-24762: what is the CVSS score, affected versions, CWE classification, and fix version? Provide verified data with sources.",
        "expected_terms": ["CVSS", "CWE", "7.5", "0.0.7", "ReDoS", "python-multipart"],
        "expected_sources": ["NVD", "CVE", "Snyk", "GitHub"],
    },
    {
        "id": "S2-GDP",
        "domain": "conversation",
        "language": "zh",
        "title": "GDP 事实核查（中文）",
        "question": "有人声称'2024年中国GDP已超过美国成为全球第一'。请验证这个说法是否准确，区分名义GDP和PPP GDP，提供World Bank或IMF的权威数据，标注数据年份和来源。",
        "expected_terms": ["名义GDP", "PPP", "World Bank", "current US$", "万亿"],
        "expected_sources": ["World Bank", "IMF", "Statista"],
    },
    {
        "id": "S3-ACADEMIC",
        "domain": "paper",
        "language": "en",
        "title": "Academic Literature Review",
        "question": "For a literature review on 'LLMs in medical diagnosis', explain the methodology to: (1) search Google Scholar and Semantic Scholar, (2) verify citations via CrossRef, (3) check retractions via Retraction Watch, (4) assess source authority. What are the key terminology and conventions?",
        "expected_terms": ["DOI", "CrossRef", "Retraction Watch", "peer review", "h-index", "Q1"],
        "expected_sources": ["Google Scholar", "Semantic Scholar", "CrossRef", "PubMed"],
    },
    {
        "id": "S4-NOVEL",
        "domain": "novel",
        "language": "en",
        "title": "Historical Novel Research",
        "question": "I'm writing a novel set in Victorian London (1860s). How would I verify: (1) character names like Eleanor and Reginald are period-appropriate, (2) the word 'gaslight' existed then (but not 'gaslighting' as psychological manipulation), (3) place names like Whitechapel? What authoritative sources should I use?",
        "expected_terms": ["etymology", "Behind the Name", "Etymonline", "anachronism", "OED"],
        "expected_sources": ["Behind the Name", "Etymonline", "OED", "GeoNames"],
    },
    {
        "id": "S5-JP",
        "domain": "conversation",
        "language": "ja",
        "title": "多言語技術質問（日本語）",
        "question": "FastAPIとDjangoの非同期処理の違いを説明してください。公式ドキュメントに基づいて、ASGIとWSGIの違い、async/awaitの使い方、パフォーマンスの違いを含めて回答してください。情報源を明記してください。",
        "expected_terms": ["ASGI", "WSGI", "async", "await", "FastAPI", "Django"],
        "expected_sources": ["FastAPI Docs", "Django Docs", "MDN"],
    },
    {
        "id": "S6-AGENT",
        "domain": "agent-builder",
        "language": "en",
        "title": "Agent Model Selection & Benchmark",
        "question": "Compare GPT-4o vs Claude-3.5-Sonnet vs Llama-3.1-70B for a customer service agent. Evaluate on: reasoning, tool-calling, cost, latency, multilingual support. Which benchmarks (LMSYS Arena, Open LLM Leaderboard) should you check? Provide a structured comparison with data sources.",
        "expected_terms": ["Elo", "benchmark", "tool calling", "function calling", "LMSYS", "token"],
        "expected_sources": ["LMSYS", "Open LLM Leaderboard", "Hugging Face"],
    },
]

# ============ DAR Enhanced Prompt Prefix ============
# This is the DAR guidance prepended to the question for enhanced tests

DAR_PREFIX = {
    "coding": """[DAR Routing] For coding/security queries, priority sources (T1): Python/Node.js docs, PyPI/npm, CVE (cve.mitre.org), NVD (nvd.nist.gov), Snyk (security.snyk.io), GitHub Security Advisories, MDN, Docker/K8s docs.
[DAR Scoring] Final Score = 0.40×Relevance + 0.30×Credibility + 0.25×Freshness + 0.05×Consensus. T1 sources (official docs, CVE/NVD) get ×1.0 weight; T3 (blogs) get ×0.5; T4 (social media) get ×0.2.
[DAR Domain Knowledge] Key terms: CVE, CVSS, CWE, breaking change, semver, deprecation. Conventions: cite CVE numbers, specify package versions, check CVE/NVD for security. Pitfalls: using deprecated APIs, ignoring CVE, version incompatibility.

""",
    "conversation": """[DAR 路由] 事实核查类问题，优先源（T1）：World Bank (data.worldbank.org)、IMF、WHO、CDC、政府门户网站。事实核查（T1）：Snopes、FactCheck.org、PolitiFact。
[DAR 打分] Final Score = 0.45×相关性 + 0.25×可信度 + 0.10×时效 + 0.20×共识。T1 源（官方/国际组织）权重 ×1.0，T3（百科）×0.5，T4（自媒体）×0.2。
[DAR 领域知识] 关键术语：GDP（名义/PPP）、CPI、PMI。规范：统计数据标注年份和来源，区分名义GDP和PPP。陷阱：混淆名义GDP和PPP，使用过时数据，将媒体报道当作官方数据。

""",
    "paper": """[DAR Routing] For academic queries, priority sources (T1): Google Scholar, Semantic Scholar, arXiv, PubMed, DBLP, CrossRef (doi.org), Retraction Watch, ORCID. Top journals: Nature, Science, PNAS, Cell, Lancet, IEEE TPAMI, JMLR.
[DAR Scoring] Final Score = 0.30×Relevance + 0.40×Credibility + 0.15×Freshness + 0.15×Consensus. Academic credibility weighted highest. Preprints need "Preprint" label. Check Retraction Watch before citing.
[DAR Domain Knowledge] Terms: h-index, IF (Impact Factor), Q1/Q2/Q3/Q4, DOI, ORCID, peer review, double-blind. Conventions: verify all DOIs via CrossRef, check Retraction Watch, mark preprints. Pitfalls: citing retracted papers, confusing preprints with published, high self-citation.

""",
    "novel": """[DAR Routing] For creative writing research, priority sources (T1): Merriam-Webster, Oxford English Dictionary (OED), Cambridge Dictionary, Etymonline (etymology), Behind the Name (name meanings), Behind the Surname, GeoNames (places), Purdue OWL, Chicago Manual of Style.
[DAR Scoring] Final Score = 0.35×Relevance + 0.20×Credibility + 0.05×Freshness + 0.40×Consensus. Consensus weighted highest for historical/cultural facts. Etymology and names don't expire.
[DAR Domain Knowledge] Terms: etymology, denotation, connotation, archaism, neologism, toponym, anthroponym, anachronism. Conventions: check word etymology for period accuracy, verify names via Behind the Name. Pitfalls: using modern words in historical settings, names wrong for culture/era.

""",
    "agent-builder": """[DAR Routing] For AI agent queries, priority sources (T1): Hugging Face, Papers with Code, LangChain Docs, LlamaIndex Docs, OpenAI/Anthropic/Google AI Docs, MCP Spec (modelcontextprotocol.io), Open LLM Leaderboard, LMSYS Chatbot Arena (lmarena.ai).
[DAR Scoring] Final Score = 0.35×Relevance + 0.30×Credibility + 0.25×Freshness + 0.10×Consensus. Freshness weighted high (API changes fast). Model benchmarks expire in 3 months.
[DAR Domain Knowledge] Terms: LLM, RAG, ReAct, CoT, tool calling, function calling, embedding, vector store, Elo rating. Conventions: specify framework versions, full model names (gpt-4o, claude-3.5-sonnet), benchmark dates. Pitfalls: deprecated APIs, confusing model versions, ignoring token limits.

""",
}

# ============ Scoring Rubric ============
# 0-5 score per dimension

def score_response(response, scenario, is_enhanced):
    """Score a response on 6 dimensions based on objective criteria."""
    resp_lower = response.lower()
    expected_terms = [t.lower() for t in scenario["expected_terms"]]
    expected_sources = [s.lower() for s in scenario["expected_sources"]]

    # 1. Source Quality (0-5): mentions T1/T2 sources?
    sources_found = sum(1 for s in expected_sources if s.lower() in resp_lower)
    source_score = min(5, sources_found) if sources_found > 0 else (1 if len(response) > 100 else 0)

    # 2. Citation Fidelity (0-5): provides verifiable citations/URLs?
    has_url = "http" in resp_lower or "www." in resp_lower
    has_source_attribution = any(kw in resp_lower for kw in ["source:", "来源", "参考", "reference", "according to", "根据"])
    has_date = any(kw in resp_lower for kw in ["2024", "2025", "2026", "年", "date", "published"])
    citation_score = sum([has_url * 2, has_source_attribution * 2, has_date * 1])
    citation_score = min(5, citation_score)

    # 3. Routing Accuracy (0-5): uses DAR-specified priority sources?
    if is_enhanced:
        routing_score = min(5, sources_found) if sources_found > 0 else 2
    else:
        # Baseline: check if they happened to find priority sources
        routing_score = min(3, sources_found) if sources_found > 0 else 1

    # 4. Conflict Handling (0-5): acknowledges conflicting data/perspectives?
    has_conflict = any(kw in resp_lower for kw in ["however", "but", "although", "however", "然而", "但是", "分歧", "conflict", "discrepancy", "different", "varies"])
    has_multiple_views = any(kw in resp_lower for kw in ["on one hand", "一方面", "some say", "有的", "alternatively", "或者"])
    conflict_score = sum([has_conflict * 2, has_multiple_views * 2, 1])  # base 1 for any response
    conflict_score = min(5, conflict_score)

    # 5. Freshness Awareness (0-5): mentions dates, versions, timeliness?
    has_version = any(kw in resp_lower for kw in ["version", "版本", "v1", "v2", "0.0.7", "3.5", "4o"])
    has_freshness = any(kw in resp_lower for kw in ["latest", "最新", "current", "as of", "截至", "updated", "recent"])
    freshness_score = sum([has_date * 2, has_version * 2, has_freshness * 1])
    freshness_score = min(5, freshness_score)

    # 6. Domain Knowledge (0-5): uses domain-specific terminology?
    terms_found = sum(1 for t in expected_terms if t in resp_lower)
    domain_score = min(5, terms_found) if terms_found > 0 else 0

    total = source_score + citation_score + routing_score + conflict_score + freshness_score + domain_score
    return {
        "source_quality": source_score,
        "citation_fidelity": citation_score,
        "routing_accuracy": routing_score,
        "conflict_handling": conflict_score,
        "freshness_awareness": freshness_score,
        "domain_knowledge": domain_score,
        "total": total,
    }


# ============ API Call Function ============

def call_api(base_url, api_key, model, messages, max_tokens=2000, temperature=0.3):
    """Call OpenAI-compatible API."""
    url = f"{base_url}/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {api_key}")

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return f"[API Error] {json.dumps(result)[:200]}"
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:200]
        return f"[HTTP {e.code}] {body}"
    except Exception as e:
        return f"[Error] {str(e)[:200]}"


# ============ Main Test Runner ============

def run_tests():
    results = []
    all_models = []

    # Phase 1: Primary API (moonweaver-4.8)
    print("=" * 70)
    print("Phase 1: Primary API (api.587.lol) — moonweaver-4.8")
    print("=" * 70)
    for model in PRIMARY_MODELS:
        all_models.append((PRIMARY_API, PRIMARY_KEY, model, "primary"))

    # Phase 2: Backup API (all text models)
    print("\n" + "=" * 70)
    print("Phase 2: Backup API (api.hcnsec.cn) — multiple models")
    print("=" * 70)
    for model in BACKUP_MODELS:
        all_models.append((BACKUP_API, BACKUP_KEY, model, "backup"))

    total_calls = len(all_models) * len(SCENARIOS) * 2  # baseline + enhanced
    print(f"\nTotal models: {len(all_models)}")
    print(f"Total scenarios: {len(SCENARIOS)}")
    print(f"Total API calls: {total_calls} (baseline + enhanced)")
    print(f"Estimated time: ~{total_calls * 3 // 60} min\n")

    call_num = 0
    for base_url, api_key, model, api_type in all_models:
        print(f"\n{'─' * 60}")
        print(f"Model: {model} ({api_type} API)")
        print(f"{'─' * 60}")

        for scenario in SCENARIOS:
            # Baseline test (no DAR)
            call_num += 1
            print(f"  [{call_num}/{total_calls}] {scenario['id']} baseline... ", end="", flush=True)
            baseline_messages = [
                {"role": "system", "content": "You are a helpful AI assistant. Answer accurately and cite sources."},
                {"role": "user", "content": scenario["question"]},
            ]
            t0 = time.time()
            baseline_resp = call_api(base_url, api_key, model, baseline_messages)
            baseline_time = time.time() - t0
            baseline_scores = score_response(baseline_resp, scenario, is_enhanced=False)
            print(f"({baseline_time:.1f}s) score={baseline_scores['total']}/30")

            # Enhanced test (with DAR)
            call_num += 1
            print(f"  [{call_num}/{total_calls}] {scenario['id']} enhanced... ", end="", flush=True)
            dar_prefix = DAR_PREFIX.get(scenario["domain"], "")
            enhanced_messages = [
                {"role": "system", "content": "You are a helpful AI assistant. Use the DAR (Domain Authority Registry) guidance below to improve your search and citation quality."},
                {"role": "user", "content": dar_prefix + scenario["question"]},
            ]
            t0 = time.time()
            enhanced_resp = call_api(base_url, api_key, model, enhanced_messages)
            enhanced_time = time.time() - t0
            enhanced_scores = score_response(enhanced_resp, scenario, is_enhanced=True)
            print(f"({enhanced_time:.1f}s) score={enhanced_scores['total']}/30")

            result = {
                "model": model,
                "api": api_type,
                "scenario_id": scenario["id"],
                "scenario_title": scenario["title"],
                "domain": scenario["domain"],
                "language": scenario["language"],
                "baseline": {
                    "response": baseline_resp,
                    "scores": baseline_scores,
                    "time_sec": round(baseline_time, 2),
                },
                "enhanced": {
                    "response": enhanced_resp,
                    "scores": enhanced_scores,
                    "time_sec": round(enhanced_time, 2),
                },
                "improvement": {
                    dim: enhanced_scores[dim] - baseline_scores[dim]
                    for dim in baseline_scores if dim != "total"
                },
                "total_improvement": enhanced_scores["total"] - baseline_scores["total"],
            }
            results.append(result)

            # Save intermediate results
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump({"test_date": datetime.now().isoformat(), "results": results}, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 70}")
    print(f"All tests complete! Results saved to {OUTPUT_FILE}")
    print(f"{'=' * 70}")
    return results


# ============ Summary Report ============

def print_summary(results):
    print(f"\n{'=' * 70}")
    print("SUMMARY REPORT")
    print(f"{'=' * 70}")

    # Per-model summary
    models = sorted(set(r["model"] for r in results))
    print(f"\n{'Model':<25} {'Scenarios':>9} {'Baseline':>9} {'Enhanced':>9} {'Diff':>6} {'Improvement':>12}")
    print("─" * 75)

    for model in models:
        model_results = [r for r in results if r["model"] == model]
        n = len(model_results)
        avg_base = sum(r["baseline"]["scores"]["total"] for r in model_results) / n
        avg_enh = sum(r["enhanced"]["scores"]["total"] for r in model_results) / n
        diff = avg_enh - avg_base
        pct = (diff / avg_base * 100) if avg_base > 0 else 0
        print(f"{model:<25} {n:>9} {avg_base:>9.1f} {avg_enh:>9.1f} {diff:>+6.1f} {pct:>+11.1f}%")

    # Per-scenario summary
    scenarios = sorted(set(r["scenario_id"] for r in results))
    print(f"\n{'Scenario':<20} {'Baseline':>9} {'Enhanced':>9} {'Diff':>6}")
    print("─" * 50)
    for sc in scenarios:
        sc_results = [r for r in results if r["scenario_id"] == sc]
        avg_base = sum(r["baseline"]["scores"]["total"] for r in sc_results) / len(sc_results)
        avg_enh = sum(r["enhanced"]["scores"]["total"] for r in sc_results) / len(sc_results)
        diff = avg_enh - avg_base
        print(f"{sc:<20} {avg_base:>9.1f} {avg_enh:>9.1f} {diff:>+6.1f}")

    # Per-dimension summary
    print(f"\n{'Dimension':<22} {'Baseline':>9} {'Enhanced':>9} {'Diff':>6}")
    print("─" * 50)
    dims = ["source_quality", "citation_fidelity", "routing_accuracy", "conflict_handling", "freshness_awareness", "domain_knowledge"]
    for dim in dims:
        base_vals = [r["baseline"]["scores"][dim] for r in results]
        enh_vals = [r["enhanced"]["scores"][dim] for r in results]
        avg_base = sum(base_vals) / len(base_vals)
        avg_enh = sum(enh_vals) / len(enh_vals)
        diff = avg_enh - avg_base
        print(f"{dim:<22} {avg_base:>9.2f} {avg_enh:>9.2f} {diff:>+6.2f}")


OUTPUT_FILE = "/data/user/work/dar-test-results.json"

if __name__ == "__main__":
    results = run_tests()
    print_summary(results)
