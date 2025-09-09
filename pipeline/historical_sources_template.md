# Historical Dump Source Template

Populate this with candidate mirrors before integrity validation.

| Transition | Phase | URL / Path | Expected Lines | SHA256 (to verify) | Status | Notes |
|------------|-------|-----------|----------------|--------------------|--------|-------|
| gpt4_to_4o | pre   |  |  |  | pending |  |
| gpt4_to_4o | post  |  |  |  | pending |  |
| 4o_to_5    | pre   |  |  |  | pending |  |
| 4o_to_5    | post  |  |  |  | pending |  |

After download:
1. Run integrity: `python pipeline/archive_integrity.py --files data/raw/*.jsonl --out pipeline/data/archive_integrity_report.json`
2. Build map: `python pipeline/build_archive_map.py --integrity pipeline/data/archive_integrity_report.json --plan pipeline/archive_plan.json --out pipeline/data/archive_map.json`
3. Coverage: `python pipeline/archive_coverage.py --map pipeline/data/archive_map.json --out pipeline/data/archive_coverage_report.json`
