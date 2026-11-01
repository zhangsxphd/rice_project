# Rice nursery water-deficit literature library

This repository contains the search plan, an aggregate progress report, and a minimal RIS exporter for the first stage of a Zotero literature-library project. Results are preliminary and searches are explicitly truncated. The source project is `zhangsxphd/Wos_Agent`; the exporter was developed on a branch derived from its v0.9 research-flow branch.

The complete local run index, raw responses, screening decisions, Zotero operation ledger, and locally acquired PDFs are stored in the local Rice-seeding project directory. Raw provider records, Zotero library data, PDFs, and credentials are intentionally excluded from this public repository. See `PUBLIC_RUN_REPORT.md` for limitations and current counts.

`search_plan_cross_crop.yaml` is the revised cross-species search plan. The historical 23-row selection is no longer used for automatic inclusion. `scripts/screen_focus.py` is an entry point to `scripts/screen_v2.py`, a deterministic, conservative title/abstract triage; every category requires review and is not a final inclusion decision. `REVIEW_REPORT.md` documents the audit, results, and limits. Local raw provider data and Zotero snapshots are not published here.
