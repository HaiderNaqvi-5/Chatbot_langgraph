## 2024-05-14 - [Caching LangChain objects in Pydantic environments]
**Learning:** Initializing LangChain objects (like ChatGroq) inside a node function takes around ~80-90ms. However, caching them using module-level global variables breaks test dependency overrides because Pydantic validation happens immediately on import, raising errors (e.g., missing GROQ_API_KEY).
**Action:** Use `@lru_cache` on getter functions instead of module-level globals to defer Pydantic validation until execution while still avoiding initialization overhead.
