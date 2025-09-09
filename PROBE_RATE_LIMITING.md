# Probe Rate Limiting & Budgeting (v0.1)

Goal: Keep total cost/time bounded while collecting stable probe metrics.

- Models: target historical (archived) vs current; if historical not callable, run only current and mark as pending.
- Per-prompt seeds: N=3 (if supported) for variance; else N=1.
- Throttle: max 30 RPM, burst ≤ 5 concurrent; backoff: 2x on 429 with jitter.
- Token cap: 512 output tokens; input prompts ≤ 120 tokens.
- Daily cap: 200 prompts/day/model; stop on budget hit.
- Logging: write JSONL with fields (timestamp, model, prompt_id, seed, temperature, response_tokens, total_tokens).
- Repro: fixed seeds per prompt; freeze temperatures per category (see probe_suite_spec.md).
- Safety: Avoid high-intensity emotional content; do not store PII.

Checklist before run:
- [ ] API keys configured via env.
- [ ] Dry-run 2 prompts to verify logging.
- [ ] Confirm budget file updated.

