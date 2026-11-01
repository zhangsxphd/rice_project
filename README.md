# Rice nursery water-deficit literature library

This repository contains the search plan, an aggregate progress report, and a minimal RIS exporter for the first stage of a Zotero literature-library project. Results are preliminary and searches are explicitly truncated. The source project is `zhangsxphd/Wos_Agent`; the exporter was developed on a branch derived from its v0.9 research-flow branch.

The complete local run index, raw responses, screening decisions, Zotero operation ledger, and locally acquired PDFs are stored in the local Rice-seeding project directory. Raw provider records, Zotero library data, PDFs, and credentials are intentionally excluded from this public repository. See `PUBLIC_RUN_REPORT.md` for limitations and current counts.

`search_plan_cross_crop.yaml` is the revised cross-species search plan. `scripts/screen_focus.py` records the conservative screening rules and the 23 title/abstract decisions made against one frozen local dataset. Its hash guard prevents applying those row-specific decisions to a differently ordered dataset. Because raw provider data are excluded here, this script requires the original local `stage_focus/deduplicated.jsonl` to replay that exact run.
