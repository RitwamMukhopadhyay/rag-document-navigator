# 📊 Document Navigator — BASELINE Evaluation Report

**Date**: September 7, 2026  
**Status**: BASELINE (Pre-optimization)

---

## 🎯 Benchmark Summary

| Metric | Measured Baseline | Target Threshold | Status |
| :--- | :--- | :--- | :--- |
| **Total Evaluation Questions** | `15 Questions` | 15 Questions | **PASS** |
| **Mean Precision@3** | **31.1%** | $\ge 25.0\%$ | **PASS** |
| **Mean Precision@5** | **18.7%** | $\ge 15.0\%$ | **PASS** |
| **Mean Recall@5** | **93.3%** | $\ge 85.0\%$ | **PASS** |
| **Key-Phrase Accuracy** | **86.7%** | $\ge 80.0\%$ | **PASS** |

---

## 📋 Per-Question Baseline Results

| ID | Question | Gold Citation | Gold File | Baseline P@3 | Baseline P@5 | Baseline R@5 | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Q01** | What is the standard delivery timeline? | `policy_shipping_returns.pdf:1` | `policy_shipping_returns.pdf` | 0.33 | 0.20 | 1.00 | **PASS** |
| **Q02** | How can I return a damaged product? | `policy_shipping_returns.pdf:1` | `policy_shipping_returns.pdf` | 0.33 | 0.20 | 1.00 | **PASS** |
| **Q03** | Is shipping free on all orders? | `policy_shipping_returns.pdf:1` | `policy_shipping_returns.pdf` | 0.33 | 0.20 | 1.00 | **PASS** |
| **Q04** | What payment options are supported on the platform? | `policy_payments_security.pdf:1` | `policy_payments_security.pdf` | 0.33 | 0.20 | 1.00 | **PASS** |
| **Q05** | Is Cash on Delivery (COD) allowed for all pin codes? | `policy_payments_security.pdf:1` | `policy_payments_security.pdf` | 0.33 | 0.20 | 1.00 | **PASS** |
| **Q06** | What is Retrieval-Augmented Generation (RAG)? | `guide_rag_basics.pdf:1` | `guide_rag_basics.pdf` | 0.33 | 0.20 | 1.00 | **PASS** |
| **Q07** | What is Precision@k in RAG evaluation? | `guide_evaluation_metrics.pdf:1` | `guide_evaluation_metrics.pdf` | 0.33 | 0.20 | 1.00 | **PASS** |
| **Q08** | What is sliding window chunking? | `guide_chunking_strategy.pdf:1` | `guide_chunking_strategy.pdf` | 0.33 | 0.20 | 1.00 | **PASS** |
| **Q09** | Why is chunk overlap necessary? | `guide_chunking_strategy.pdf:1` | `guide_chunking_strategy.pdf` | 0.33 | 0.20 | 1.00 | **PASS** |
| **Q10** | How does vector similarity search work? | `guide_vector_search.pdf:1` | `guide_vector_search.pdf` | 0.33 | 0.20 | 1.00 | **PASS** |
| **Q11** | What happens when evidence is insufficient? | `guide_rag_basics.pdf:1` | `guide_rag_basics.pdf` | 0.33 | 0.20 | 1.00 | **PASS** |
| **Q12** | How is personal user data stored and encrypted? | `policy_privacy_data_use.pdf:1` | `policy_privacy_data_use.pdf` | 0.33 | 0.20 | 1.00 | **PASS** |
| **Q13** | How do I escalate a unresolved support ticket? | `guide_support_escalation.pdf:1` | `guide_support_escalation.pdf` | 0.33 | 0.20 | 1.00 | **PASS** |
| **Q14** | What is a system prompt and how does it prevent hallucinations? | `guide_system_prompting.pdf:1` | `guide_system_prompting.pdf` | 0.33 | 0.20 | 1.00 | **PASS** |
| **Q15** | How are logs monitored and audited? | `guide_logging_monitoring.pdf:1` | `guide_logging_monitoring.pdf` | 0.00 | 0.00 | 0.00 | **FAIL** |

---

## 🔍 Key Insights & Optimization Opportunities

1. **Precision Ceiling in Single-Chunk Datasets**:
   - In the benchmark dataset, each PDF document consists of 1 page and 1 chunk.
   - When candidate retrieval expands query terms (e.g. adding `"policy shipping returns delivery window days"`), generic words like `"policy"` match other documents in the vector index (`policy_payments_security.pdf`, `policy_privacy_data_use.pdf`), dragging down Precision@3 to 33.3% and Precision@5 to 20.0%.
2. **Q15 Retrieval Failure**:
   - Q15 (`"How are logs monitored and audited?"`) fails in the baseline because query expansion / vector search ranks non-target guide files above `guide_logging_monitoring.pdf`.
3. **Primary Objective**:
   - Introduce conservative query normalization (preserving domain terms), weighted reranking (boosting exact phrase matches, query term coverage, and filename/title matches), diversity filtering (MMR), and refined evidence checking to improve Precision@3, Precision@5, Recall@5, and Keyphrase Accuracy.
