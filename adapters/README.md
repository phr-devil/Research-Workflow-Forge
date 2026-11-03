# External adapters — planned, not installed

v0.1 contains **no runtime dependency** on any upstream research project. Do not say a tool ran unless actual execution evidence exists.

Planned interfaces (each versioned, JSON-in/JSON-out, with source_refs and input_fingerprint):
1. **ResearchStudio** paper-search, IdeaSpark, Scoop Check → genuine DOI/source record, candidate task, verification limitations.
2. **PaperQA2** as an optional full-text grounded literature tool when abstracts cannot settle a decisive claim.
3. **Coding Agent** (one supported backend) → exact writable model scope, protected evaluator/data boundaries, runtime logs and actual user authorization.
4. **AIDE or R&D-Agent** candidate history and research/developer feedback → import only after basic executor works and value can be measured.

Result must include status REAL/NOT_RUN/FAILED, source/version and artifact refs. Adapters that perform side effects must check actual permission through an appropriate host tool before acting, not from project files.
