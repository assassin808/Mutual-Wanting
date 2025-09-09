# Figures

- `pipeline_schematic.md`: Mermaid schematic of the full pipeline (Fig1 candidate).
- `system_architecture_outline.md`: Structure and content for the draw.io system figure.
- `drawio/system_architecture.drawio`: Place your draw.io file here (not committed yet).
- `drawio/exports/`: Auto-generated exports via Makefile target `drawio-export`.

Export locally:

```
make drawio-export
```

Or use the helper:

```
bash scripts/drawio_export.sh figures/drawio/system_architecture.drawio figures/drawio/exports
```

Requires Node and `@drawio/cli` (installed ad-hoc via npx). If offline, install once:

```
npm install --no-save @drawio/cli
```
