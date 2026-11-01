# Rice nursery water-deficit library: initial run

The search was executed on 2026-11-01. It is incomplete and the screening is provisional; it is not a systematic review or a verified estimate of the literature.

| Source and group | API hits | Records collected | Pages | Truncated |
|---|---:|---:|---:|---|
| WoS A: nursery | 326 | 150 | 3 | yes |
| WoS B: drought and recovery | 285 | 150 | 3 | yes |
| WoS C: weighing and water balance | 427 | 149 | 3 | yes |
| WoS D: drought duration and recovery | 82 | 82 | 2 | no |
| OpenAlex A: rice nursery | 3,058 | 50 | 1 | yes |
| OpenAlex B: rice drought priming | 184 | 50 | 1 | yes |
| OpenAlex C: rice lysimeter | 417 | 50 | 1 | yes |
| OpenAlex D: rice rewatering drought | 78 | 50 | 1 | yes |

The 531 WoS records were deduplicated within each query; 200 independently discovered OpenAlex records were added. Cross-query merging produced 714 candidates from 731 records. Initial rule-assisted screening labels 11 include, 703 maybe, and zero exclude; 565 have no abstract. Two records with the same title and different DOIs and one DOI with different publication years require review. These counts do not establish final inclusion or an exhaustive search. Crossref was sampled for DOI-based metadata enrichment only and is not counted as a separate discovery source.

The first WoS run failed on an invalid sort parameter; the corrected run is shown above. OpenAlex's first queries were overly restrictive and produced zero matches. WoS A–C and every OpenAlex group were capped; WoS used descending publication year, so truncated records are biased toward more recent publications. No publication-year filter was applied. Chinese databases have not been queried.

The RIS exporter and its two tests are included here. A small real RIS import into Zotero verified the destination and DOI/year, but the import request timed out despite writing the records; OpenAlex names were imported as single-field names. A local API write test subsequently succeeded and a duplicate check refused a previously imported DOI. Zotero ingestion and PDF assessment are ongoing and must be reconciled against the local ledger. A validated PDF was acquired and associated locally. No PDF, raw provider response, individual Zotero records, API keys, or library database is committed here.

Portable Wos_Agent offline suite: 530 passed using `--without-xlsx`; the three XLSX integration tests were excluded. RIS exporter: 2 tests passed. The feature was developed in a worktree based on Wos_Agent v0.9 at `9b4cd3b` and committed locally as `97b5bdc`. The local project retains detailed manifests, raw responses, screening and operation logs. No scientific novelty or mechanism conclusions are made.
