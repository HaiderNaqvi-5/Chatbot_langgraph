## 2024-05-24 - Avoid LLM object instantiation per graph node execution
**Learning:** Instantiating `ChatGroq` (or other LangChain LLM clients) and `ChatPromptTemplate` inside LangGraph nodes creates a significant performance bottleneck. These are created on *every single request* passing through the graph nodes (`extract_data_node` and `generate_reply_node` in our case).
Declaring them at the module level breaks tests because Pydantic models (like `ChatGroq`) eagerly validate API keys on import. This prevents `app.dependency_overrides` from working since the app crashes on startup if `GROQ_API_KEY` isn't in the environment.

**Action:** Always wrap LLM and PromptTemplate initializations in a getter function using `@lru_cache()`. This initializes the objects exactly once per process (eliminating the per-request CPU/memory overhead) while deferring instantiation until execution time, which allows tests to run without requiring a real API key.
