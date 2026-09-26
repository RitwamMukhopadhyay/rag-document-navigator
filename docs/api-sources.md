# External Data Sources & Research Tool Specifications

This document details the data coverage, API contracts, rate limits, fallback behaviors, and responsible-use guidelines for all integrated research tools in the **Pharma Research & Intelligence Agent**.

---

## 1. PubMed / NCBI E-utilities API

- **Provider**: National Center for Biotechnology Information (NCBI) / U.S. National Library of Medicine
- **Base Endpoint**: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils`
- **Sub-tools Used**:
  - `esearch.fcgi`: Search term query expansion, retrieving PubMed Unique Identifiers (PMIDs).
  - `esummary.fcgi`: Batch retrieval of article titles, publication dates, journal names, and authors.
- **Normalization**:
  - `source_type`: `pubmed`
  - `source_identifier`: `PMID:<id>`
  - `url`: `https://pubmed.ncbi.nlm.nih.gov/<pmid>/`
- **Rate Limits & Politeness**:
  - Max 3 requests per second without API key; 10 requests per second with `NCBI_API_KEY`.
- **Fallback / Error Handling**:
  - Automatic HTTP timeout enforcement (8.0 seconds).
  - Graceful fallback to verified offline mock paper dataset if network is unreachable.

---

## 2. ClinicalTrials.gov API v2

- **Provider**: U.S. National Library of Medicine
- **Base Endpoint**: `https://clinicaltrials.gov/api/v2/studies`
- **Coverage**: Over 450,000 registered interventional and observational clinical trials worldwide.
- **Retrieved Parameters**:
  - NCT Identifier (`nctId`)
  - Official / Brief Study Title
  - Overall Recruitment Status (`COMPLETED`, `RECRUITING`, `ACTIVE_NOT_RECRUITING`)
  - Study Phases (`PHASE1`, `PHASE2`, `PHASE3`, `PHASE4`)
  - Target Conditions and Interventions
- **Normalization**:
  - `source_type`: `clinical_trials`
  - `source_identifier`: `NCT<number>`
  - `url`: `https://clinicaltrials.gov/study/<nct_id>`
- **Fallback / Error Handling**:
  - 8.0s request deadline.
  - Fallback to mock clinical trial registry when offline.

---

## 3. openFDA Drug Label API

- **Provider**: U.S. Food and Drug Administration (FDA)
- **Base Endpoint**: `https://api.fda.gov/drug/label.json`
- **Coverage**: Official FDA-approved drug package insert labels and structured product labeling (SPL).
- **Retrieved Fields**:
  - Brand name & Generic name
  - Boxed Warnings (`boxed_warning`)
  - Warnings & Cautions (`warnings_and_cautions`)
  - Indications & Usage (`indications_and_usage`)
  - FDA Set Identifier (`id`)
- **Normalization**:
  - `source_type`: `openfda`
  - `source_identifier`: `FDA-SET:<id>`
  - `url`: `https://labels.fda.gov/`

---

## 4. Document RAG Subsystem

- **Scope**: User-uploaded reference PDF study papers and clinical protocols.
- **Indexing Engine**: Page-by-page text extraction via PyPDF, windowed paragraph chunking (~500 chars), TF-IDF word overlap vector scoring.
- **Normalization**:
  - `source_type`: `document`
  - `source_identifier`: `[<filename>, p. <page_number>]`

---

## 5. Responsible Use & Compliance Statement

> **CRITICAL DISCLAIMER**: All public API queries and retrieved data are intended strictly for computational academic research, competitive market intelligence, and literature synthesis. This application does NOT provide medical advice, diagnosis, or treatment guidelines.
