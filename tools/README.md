# Tools — implemented vs planned

**Implemented offline:** \`python -m core.cli\` init, route, record, history, validate, compare. Handoff uses evidence-file hash; \`compare\` rejects noncomparable VALID developer runs and sealed experiments. The CLI does **not** execute models or certify scientific contribution.

**Implemented explicit online:** \`python -m adapters.literature\` fetches public OpenAlex/Crossref metadata. CI tests use mocked responses. Need public network at runtime.

**Planned:** official data manifests/files/hashes/split safety audits; evaluator-isolated authorized runner; group-level effect+uncertainty; candidate journal/MLflow optional; full-text named-nearest-work checker; frozen independent confirmation.

Prefer narrowly adapted verified upstream code over wholesale framework installs. No unnecessary images, all original logs retained.
