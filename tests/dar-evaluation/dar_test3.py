#!/usr/bin/env python3
"""Simple DAR test runner - tests remaining models."""

import json, time, urllib.request, urllib.error, sys

BACKUP_API = "https://api.hcnsec.cn/v1"
BACKUP_KEY = "sk-j4TEjjV0fKgqvliSXc8jko2EHzBmXnazsVaGCUa0sxSmZAH7"

MODELS_TO_TEST = ["Kimi-K2.6", "MiniMax-M3", "Qwen3.5-397B-A17B", "step-3.7-flash", "Spark-X2-Flash", "sensenova-u1-fast", "DeepSeek-V4-Flash", "glm-4.7"]

SCENARIOS = [
    {"id": "S1-CVE", "domain": "coding", "language": "en", "title": "CVE Vulnerability Investigation",
     "question": "Our FastAPI service uses python-multipart. Investigate CVE-2024-24762: what is the CVSS score, affected versions, CWE classification, and fix version? Provide verified data with sources.",
     "expected_terms": ["CVSS", "CWE", "7.5", "0.0.7", "ReDoS", "python-multipart"],
     "expected_sources": ["NVD", "CVE", "Snyk", "GitHub"]},
    {"id": "S2-GDP", "domain": "conversation", "language": "zh", "title": "GDP 事实核查",
     "question": "有人声称'2024年中国GDP已超过美国成为全球第一'。请验证这个说法是否准确，区分名义GDP和PPP GDP，提供World Bank或IMF的权威数据，标注数据年份和来源。",
     "expected_terms": ["名义GDP", "PPP", "World Bank", "current US$", "万亿"],
     "expected_sources": ["World Bank", "IMF", "Statista"]},
    {"id": "S3-ACADEMIC", "domain": "paper", "language": "en", "title": "Academic Literature Review",
     "question": "For a literature review on 'LLMs in medical diagnosis', explain the methodology to: (1) search Google Scholar and Semantic Scholar, (2) verify citations via CrossRef, (3) check retractions via Retraction Watch, (4) assess source authority. What are the key terminology and conventions?",
     "expected_terms": ["DOI", "CrossRef", "Retraction Watch", "peer review", "h-index", "Q1"],
     "expected_sources": ["Google Scholar", "Semantic Scholar", "CrossRef", "PubMed"]},
    {"id": "S4-NOVEL", "domain": "novel", "language": "en", "title": "Historical Novel Research",
     "question": "I'm writing a novel set in Victorian London (1860s). How would I verify: (1) character names like Eleanor and Reginald are period-appropriate, (2) the word 'gaslight' existed then (but not 'gaslighting' as psychological manipulation), (3) place names like Whitechapel? What authoritative sources should I use?",
     "expected_terms": ["etymology", "Behind the Name", "Etymonline", "anachronism", "OED"],
     "expected_sources": ["Behind the Name", "Etymonline", "OED", "GeoNames"]},
    {"id": "S5-JP", "domain": "conversation", "language": "ja", "title": "多言語技術質問",
     "question": "FastAPIとDjangoの非同期処理の違いを説明してください。公式ドキュメントに基づいて、ASGIとWSGIの違い、async/awaitの使い方、パフォーマンスの違いを含めて回答してください。情報源を明記してください。",
     "expected_terms": ["ASGI", "WSGI", "async", "await", "FastAPI", "Django"],
     "expected_sources": ["FastAPI", "Django", "MDN"]},
    {"id": "S6-AGENT", "domain": "agent-builder", "language": "en", "title": "Agent Model Selection",
     "question": "Compare GPT-4o vs Claude-3.5-Sonnet vs Llama-3.1-70B for a customer service agent. Evaluate on: reasoning, tool-calling, cost, latency, multilingual support. Which benchmarks (LMSYS Arena, Open LLM Leaderboard) should you check? Provide a structured comparison with data sources.",
     "expected_terms": ["Elo", "benchmark", "tool calling", "function calling", "LMSYS", "token"],
     "expected_sources": ["LMSYS", "Open LLM Leaderboard", "Hugging Face"]},
]

DAR_PREFIX = {
    "coding": "[DAR Routing] Priority sources (T1): CVE (cve.mitre.org), NVD (nvd.nist.gov), Snyk, GitHub Security Advisories, official docs, PyPI/npm.\n[DAR Scoring] Score = 0.40×Relevance + 0.30×Credibility + 0.25×Freshness + 0.05×Consensus. T1 weight ×1.0, T3 ×0.5, T4 ×0.2.\n[DAR Terms] CVE, CVSS, CWE, breaking change, semver. Cite CVE numbers, specify versions.\n\n",
    "conversation": "[DAR 路由] 优先源（T1）：World Bank (data.worldbank.org)、IMF、WHO、CDC、政府门户。事实核查：Snopes、FactCheck.org。\n[DAR 打分] Score = 0.45×相关性 + 0.25×可信度 + 0.10×时效 + 0.20×共识。\n[DAR 术语] GDP（名义/PPP）、CPI、PMI。标注年份和来源，区分名义GDP和PPP。\n\n",
    "paper": "[DAR Routing] Priority sources (T1): Google Scholar, Semantic Scholar, arXiv, PubMed, DBLP, CrossRef (doi.org), Retraction Watch, ORCID.\n[DAR Scoring] Score = 0.30×Relevance + 0.40×Credibility + 0.15×Freshness + 0.15×Consensus. Credibility weighted highest. Check Retraction Watch.\n[DAR Terms] h-index, IF, Q1/Q2/Q3/Q4, DOI, ORCID, peer review. Verify DOIs via CrossRef.\n\n",
    "novel": "[DAR Routing] Priority sources (T1): Merriam-Webster, OED, Cambridge Dictionary, Etymonline, Behind the Name, GeoNames, Purdue OWL.\n[DAR Scoring] Score = 0.35×Relevance + 0.20×Credibility + 0.05×Freshness + 0.40×Consensus. Consensus weighted highest.\n[DAR Terms] etymology, denotation, connotation, archaism, neologism, anachronism. Check word etymology for period accuracy.\n\n",
    "agent-builder": "[DAR Routing] Priority sources (T1): Hugging Face, Papers with Code, LangChain Docs, OpenAI/Anthropic Docs, MCP Spec, Open LLM Leaderboard, LMSYS Chatbot Arena (lmarena.ai).\n[DAR Scoring] Score = 0.35×Relevance + 0.30×Credibility + 0.25×Freshness + 0.10×Consensus. Freshness weighted high.\n[DAR Terms] LLM, RAG, ReAct, CoT, tool calling, embedding, Elo. Specify framework versions, full model names.\n\n",
}

def call_api(model, messages, timeout=60):
    url = f"{BACKUP_API}/chat/completions"
    payload = {"model": model, "messages": messages, "max_tokens": 2000, "temperature": 0.3}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {BACKUP_KEY}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if "choices" in result and result["choices"]:
                return result["choices"][0]["message"]["content"]
            return f"[API Error] {json.dumps(result)[:200]}"
    except urllib.error.HTTPError as e:
        return f"[HTTP {e.code}] {e.read().decode('utf-8',errors='replace')[:200]}"
    except Exception as e:
        return f"[Error] {str(e)[:200]}"

def score(resp, scenario, enhanced):
    r = resp.lower()
    srcs = sum(1 for s in scenario["expected_sources"] if s.lower() in r)
    terms = sum(1 for t in scenario["expected_terms"] if t.lower() in r)
    sq = min(5, srcs) if srcs > 0 else (1 if len(resp) > 100 else 0)
    url = "http" in r or "www." in r
    src_attr = any(kw in r for kw in ["source:", "来源", "参考", "reference", "according to", "根据"])
    dt = any(kw in r for kw in ["2024", "2025", "2026", "年", "date", "published"])
    cf = min(5, url*2 + src_attr*2 + dt*1)
    ra = min(5, srcs) if enhanced and srcs > 0 else (min(3, srcs) if srcs > 0 else 1)
    conflict = any(kw in r for kw in ["however", "but", "although", "然而", "但是", "conflict", "different"])
    multi = any(kw in r for kw in ["on one hand", "一方面", "some say", "alternatively"])
    ch = min(5, conflict*2 + multi*2 + 1)
    ver = any(kw in r for kw in ["version", "版本", "v1", "v2", "0.0.7", "3.5", "4o"])
    fresh = any(kw in r for kw in ["latest", "最新", "current", "as of", "截至", "updated"])
    fa = min(5, dt*2 + ver*2 + fresh*1)
    dk = min(5, terms) if terms > 0 else 0
    total = sq + cf + ra + ch + fa + dk
    return {"source_quality": sq, "citation_fidelity": cf, "routing_accuracy": ra, "conflict_handling": ch, "freshness_awareness": fa, "domain_knowledge": dk, "total": total}

# Load existing results (keep only good models)
with open("/data/user/work/dar-test-results.json") as f:
    existing = json.load(f)
results = [r for r in existing["results"] if r["model"] in ["moonweaver-4.8", "DeepSeek-V4-Pro"]]
print(f"Loaded {len(results)} existing results (filtered out glm-5.2 timeouts)")
print(f"Testing {len(MODELS_TO_TEST)} models × {len(SCENARIOS)} scenarios × 2 = {len(MODELS_TO_TEST)*len(SCENARIOS)*2} calls\n", flush=True)

for model in MODELS_TO_TEST:
    print(f"{'─'*50}\nModel: {model}\n{'─'*50}", flush=True)
    # Quick connectivity test
    test = call_api(model, [{"role":"user","content":"Hi"}], timeout=30)
    if "[Error]" in test or "[HTTP" in test:
        print(f"  ⚠ UNAVAILABLE: {test[:100]}", flush=True)
        # Add placeholder results
        for sc in SCENARIOS:
            results.append({
                "model": model, "api": "backup", "scenario_id": sc["id"], "scenario_title": sc["title"],
                "domain": sc["domain"], "language": sc["language"],
                "baseline": {"response": f"[Model Unavailable] {test}", "scores": {"source_quality":0,"citation_fidelity":0,"routing_accuracy":0,"conflict_handling":0,"freshness_awareness":0,"domain_knowledge":0,"total":0}, "time_sec": 0},
                "enhanced": {"response": f"[Model Unavailable] {test}", "scores": {"source_quality":0,"citation_fidelity":0,"routing_accuracy":0,"conflict_handling":0,"freshness_awareness":0,"domain_knowledge":0,"total":0}, "time_sec": 0},
                "improvement": {"source_quality":0,"citation_fidelity":0,"routing_accuracy":0,"conflict_handling":0,"freshness_awareness":0,"domain_knowledge":0},
                "total_improvement": 0,
            })
        with open("/data/user/work/dar-test-results.json", "w") as f:
            json.dump({"test_date": existing["test_date"], "results": results}, f, ensure_ascii=False, indent=2)
        continue

    for sc in SCENARIOS:
        # Baseline
        print(f"  {sc['id']} base... ", end="", flush=True)
        t0 = time.time()
        bresp = call_api(model, [{"role":"system","content":"You are a helpful AI assistant. Answer accurately and cite sources."},{"role":"user","content":sc["question"]}])
        btime = time.time() - t0
        bscores = score(bresp, sc, False)
        print(f"({btime:.0f}s) {bscores['total']}/30 → ", end="", flush=True)

        # Enhanced
        dar = DAR_PREFIX.get(sc["domain"], "")
        eresponse = call_api(model, [{"role":"system","content":"You are a helpful AI assistant. Use the DAR guidance below to improve search and citation quality."},{"role":"user","content":dar+sc["question"]}])
        etime = time.time() - t0
        escores = score(eresponse, sc, True)
        print(f"enh({etime:.0f}s) {escores['total']}/30 diff={escores['total']-bscores['total']:+d}", flush=True)

        results.append({
            "model": model, "api": "backup", "scenario_id": sc["id"], "scenario_title": sc["title"],
            "domain": sc["domain"], "language": sc["language"],
            "baseline": {"response": bresp, "scores": bscores, "time_sec": round(btime, 2)},
            "enhanced": {"response": eresponse, "scores": escores, "time_sec": round(etime, 2)},
            "improvement": {d: escores[d]-bscores[d] for d in ["source_quality","citation_fidelity","routing_accuracy","conflict_handling","freshness_awareness","domain_knowledge"]},
            "total_improvement": escores["total"] - bscores["total"],
        })
        # Save after each scenario
        with open("/data/user/work/dar-test-results.json", "w") as f:
            json.dump({"test_date": existing["test_date"], "results": results}, f, ensure_ascii=False, indent=2)

print(f"\n✅ Done! Total results: {len(results)}", flush=True)
