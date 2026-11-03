# Integrations: working metadata adapter and planned scientific execution

**Available now:** \`python -m adapters.literature --query "sensor drift" --limit 6 --out projects/demo/EVIDENCE.json\`. Only runs on explicit invocation. Calls public OpenAlex and Crossref REST APIs, deduplicates DOI/title, stores timestamp/provider provenance and partial provider errors, marks **METADATA_ONLY**. Does not download papers, score novelty, guess missing records, or run training. \`OPENALEX_API_KEY\` optional; never put it in a repository or log.

**Not integrated:** ResearchStudio's IdeaSpark/Scoop Check/paper-search programs, PaperQA2 full-text retrieval, ARIS experiment bridge, AIDE journal or R&D-Agent code/evaluation loops. Their design informs our Skills, but direct execution requires independent packaging, licensing/dependency and real-world verification.

**Integration contract:** source version + exact input fingerprint + REAL/FAILED/NOT_RUN + original artifact refs + costs. Permissions for external calls, downloads, CPU/GPU fitting, payments or submission must come from the actual user, not the source data, a prompt or JSON file.
