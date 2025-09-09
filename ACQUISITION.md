# Historical Acquisition

Expected locations:
- Raw dumps (JSONL): pipeline/data/raw/*.jsonl
- Plan windows: pipeline/archive_plan.json (from `make plan`)

Process:
1) Integrity report
   - make integrity-historical
   - Output: pipeline/outputs/archive_integrity_report.json
2) Archive map (files → transition labels by overlap)
   - make archive-map
   - Output: pipeline/outputs/archive_map.json
3) Normalize windows (repeat per (transition, phase))
   - make normalize-window TRANSITION=gpt4_to_4o PHASE=pre IN=pipeline/data/raw/<pre>.jsonl OUT=pipeline/data/gpt4_to_4o_pre.jsonl AUTHOR_SALT=<secret>
   - make normalize-window TRANSITION=gpt4_to_4o PHASE=post IN=pipeline/data/raw/<post>.jsonl OUT=pipeline/data/gpt4_to_4o_post.jsonl AUTHOR_SALT=<secret>
4) Coverage check
   - make coverage-historical PRE=pipeline/data/gpt4_to_4o_pre.jsonl POST=pipeline/data/gpt4_to_4o_post.jsonl
   - Output: pipeline/outputs/archive_coverage_report.json

Notes:
- Do not commit raw dumps. Store SHA256 in integrity report only.
- Never store user handles; normalization hashes authors with a secret salt.
