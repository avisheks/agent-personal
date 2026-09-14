---
title: "What is OpenAI-compatible API?"
summary: "A de-facto standard HTTP API specification mirroring OpenAI's /v1/chat/completions, /v1/completions, and /v1/embeddings endpoints. Serving frameworks (vLLM, SGLang, TGI, Ollama) and providers (Together, Fireworks, Groq) implement it so applications built for OpenAI can switch to any backend with zero code changes — just change the base_url. Not an official standard — it's 'whatever OpenAI does' that others reverse-engineer and replicate."
type: "query"
createdAt: "2026-06-07T00:00:00Z"
---
See FAQ report: [[LLM Inference Optimization FAQs]], FAQ 4
