---
name: rag-systems
description: Use when designing, implementing, or evaluating retrieval-augmented generation systems, embeddings, chunking, vector stores, reranking, grounding, citations, and hallucination controls.
---

# RAG Systems

## Workflow

1. Define user questions, corpus, freshness, and grounding requirements.
2. Choose ingestion, chunking, metadata, embeddings, vector store, and reranking strategy.
3. Evaluate retrieval and answer quality separately.
4. Add citations and refusal behavior where needed.
5. Monitor drift, stale documents, and failure cases.

## Guardrails

- Do not evaluate only generated answers; evaluate retrieval.
- Do not omit source attribution when factual accuracy matters.
