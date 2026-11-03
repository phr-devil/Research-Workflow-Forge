# v0.7 upgrade: metric provenance, event chain and Agent handoff

- WP1: independent DEV classification metric recomputation from SHA-bound CSV/manifest and fixed group-held-out fold; strict Run/Champion/CLI comparison.
- WP2: seq+prev_digest+event_digest in EVENTS and STATE anchor, full-chain check in history/brief/recovery. Explicit `migrate-ledger` preview/apply. Sealed Run blocked in development events; independent confirmation not implemented.
- WP3: paired group-bootstrap exploratory interval and previous Challenger count in Champion preview; no mandatory p-value or automatic project STOP.
- WP4: external Agent prediction importer `adapters.agent_bridge` with trusted DEV metric recomputation. No autonomous arbitrary-code execution/sandbox yet.
- CI uses synthetic data and adversarial tests, not real research outcomes.

Back up legacy projects; preview `python -m core.cli migrate-ledger --dir PROJECT`, then `--apply` only after reviewing the log. Historical Runs require real source artifacts to be re-verified. Adaptive DEV comparison intervals cannot support independent scientific Claims.
