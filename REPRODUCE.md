# Reproduce (local, no external calls)

Quick run:

- make pilot-reports   # agreement, disagreements, early κ, per-tag κ, tables/figs
- make tables          # includes Table1 sampling & coverage
- make figs            # figure CSV slices
- make drawio-export   # system figure exports (once .drawio exists)
- make probes          # scaffold manifest + empty stats
- make regression      # scaffold dataset + placeholder regression results

Notes:
- Historical dumps are still needed for drift/regression beyond pilot. Provide mirrors+SHA256 to proceed.
- Probes do not call external APIs here; populate responses offline and rerun probe_stats.
