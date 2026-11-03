# Progress: collateral merge (branch claude/collateral-merge)

## Done (all pushed)
- Staged 165 collateral people from the book data already in app.js (calendar, CLAIMS, STORIES, CLIPPINGS, CENSUS) in `collateral/people.json`.
- One fact-check note per person in `collateral/notes.json`, plus a log of 8 duplicates matched to existing tree people.
- 32 spouse links and 17 unconfirmed parent suggestions in `collateral/relationships.json`.
- `collateral/build.py` regenerates the files from app.js. `collateral/validate.py` checks them and passes.
- Summary, conflicts and privacy notes in `COLLATERAL_MERGE.md`.
- app.js and main are untouched. No PR opened.

## Blocked / next
- The real sources are not in the repo: the book scan `books/tellas-about-ourselves-1991.pdf` (where the ~395 people are) and the `obituaries/*.txt` captures. Matthew needs to commit them, or a transcription.
- After that: extend build.py to read the book's genealogy section and the obituary survivor lists, then re-run validate.py.
- Matthew to rule on the 12 conflicts listed in COLLATERAL_MERGE.md.
