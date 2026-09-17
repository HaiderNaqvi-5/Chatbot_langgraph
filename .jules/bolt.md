## 2024-05-15 - Cached LLM Instantiation

**Learning:** Instantiating `ChatGroq` repeatedly inside graph node functions causes substantial performance latency (e.g., ~0.06s per instantiation) due to Pydantic validation overhead and setup processes.
**Action:** Always use `@lru_cache` on getter functions for `ChatGroq` instances and `ChatPromptTemplate`s in LangGraph nodes to avoid repetitive initialization delays. This also defers Pydantic validation until execution, solving issues where missing API keys on import could break dependency injection overrides in tests.
