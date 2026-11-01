# Rice nursery / cyclic water deficit literature search: preliminary report

Searches were run on 2026-11-01. The research focus was clarified during the run: **water-use and transpiration responses to recurring water deficits and recovery after rewatering**. Rice nurseries remain an application context, but relevant process and measurement studies in other crops and species are eligible. The project does not draw novelty, mechanism or experimental-design conclusions.

The initial broad search results were imported into Zotero too eagerly. The resulting broad collection contains 1,133 records, including clearly off-topic records; it must not be presented as a curated library. After the user corrected the scope, broad automatic imports stopped. Existing items and attachments were preserved and a separate focus subcollection was created. The focus collection contains 20 records, selected after inspecting their titles and abstracts; three additional preliminary inclusions await identity review. This is an assistant screening pass, not a final human-reviewed inclusion set.

| Source and query group | Reported hits | Collected | Pages | Completeness |
|---|---:|---:|---:|---|
| WoS A rice nursery | 326 | 326 | 7 | exhausted |
| WoS B rice seedlings and recovery | 286 | 286 | 6 | exhausted |
| WoS C weighing and water balance | 428 | 427 unique | 9 | exhausted; one within-query duplicate |
| WoS D deficit and recovery | 82 | 82 | 2 | exhausted |
| WoS E repeated deficit and water use across species | 82 | 82 | 2 | exhausted |
| WoS F rewatering and water use across species | 571 | 571 | 12 | exhausted |
| WoS G drought and weighing methods across species | 237 | 237 | 5 | exhausted |
| WoS H timing, intensity and recovery across species | 180 | 179 unique | 4 | exhausted; one within-query duplicate |
| OpenAlex A rice nursery | 3,058 | 3,058 | 16 | one Work ID repeated across pages; completeness uncertain |
| OpenAlex B rice drought priming | 184 | 184 | 1 | exhausted |
| OpenAlex C rice lysimeter | 417 | 417 | 3 | exhausted |
| OpenAlex D rice rewatering drought | 78 | 78 | 1 | exhausted |

The first WoS run failed with HTTP 400 because its sort parameter was invalid; later corrected runs are preserved. Earlier OpenAlex queries were too restrictive and returned zero; a first-page pilot preceded the paginated run. No year filter was applied. The merged input contains 6,127 record instances, including 200 records from the earlier OpenAlex pilot that were searched again in the paginated run; these are not independent papers. After deduplication there are 5,576 candidates. Of these, 23 are preliminary include, 5,438 maybe and 115 automatic preliminary exclude; 1,760 lack abstracts and none was excluded solely for lacking an abstract. The vast majority still need individual human screening. The merge marked 202 candidate records with identity concerns and 43 DOIs with differing years across sources; these counts can overlap. A possible preprint / final version pair is retained for review.

Crossref DOI-only enrichment inspected 1,009 records and returned 306 accepted abstracts, of which 241 filled missing values in the combined dataset. OpenAlex DOI-only enrichment of 907 cross-species records supplied another 504 abstracts. These lookups are enrichment, not additional discovery counts. All raw pages, local audit files and detailed screening decisions remain in the local project, not this public repository.

The focus subcollection has 20 verified Zotero records. Fifteen have PDFs checked against the DOI or title and publication details; five currently lack an attachment. Six PDFs were obtained from J-STAGE during this run, including scanned first pages checked visually. Three other focus candidates are not yet in Zotero because identity is uncertain. Some existing attachments came from Sci-Hub; the user later allowed that source. No PDFs, raw provider records, private Zotero data or credentials are committed here.

Wos_Agent's portable offline suite ran 530 tests successfully using `--without-xlsx`; three XLSX integration tests were omitted. Two RIS tests passed, and a real small RIS import plus local Zotero API writes and an existing-DOI refusal were checked. RIS contains 5,576 entries. A synthetic offline pagination check confirmed repeated OpenAlex IDs are flagged as incomplete; synthetic test data were not included in the search results. Full human screening, all attachment checks and comprehensive repeated-run validation remain unfinished.
