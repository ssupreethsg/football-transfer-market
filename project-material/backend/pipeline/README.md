# Data pipeline

Builds the website's player dataset from real match data. Nothing is estimated or projected:
a number the source does not have is stored as `null` and shown as "–" on the site.

```
scrape_fotmob.py  ->  cache/ (raw JSON, git-ignored)  ->  build_dataset.py  ->  frontend/public/data/
                                                              |
                                                       verify_dataset.py (Understat cross-check)
```

## Sources

| Data | Source |
|---|---|
| Squads (current season), player bio, full career by season and competition | FotMob (match data by Opta / Stats Perform) |
| Detailed stats per season and competition (minutes, xG, xA, shots, dribbles, tackles, ...) | FotMob, last 4 seasons |
| Market value | SciSports, via FotMob |
| Independent check of league appearances, goals and assists | Understat |

## Run

```bash
pip install requests
python scrape_fotmob.py squads             # 96 clubs, ~2,700 players
python scrape_fotmob.py profiles --workers 10
python scrape_fotmob.py deep --workers 10 --seasons 4
python build_dataset.py                    # writes frontend/public/data
python verify_dataset.py                   # writes verification_report.json
```

Every request is cached in `cache/`, so a stopped run resumes where it left off.
Delete `cache/` (or parts of it) to refresh. `--player <id>` limits a stage to one player.

## Output

- `index.json`: one row per player (club, position, this season, last season, career totals, market value)
- `players/<id>.json`: the full player file
  - `career_totals`: whole career, plus detailed totals for the seasons that have them
  - `career_by_competition`: cumulative totals split by competition (league, cups, Europe, national team)
  - `seasons[]`: each season with its totals and one entry per competition played
- `meta.json`: build time, season, counts

Friendlies are excluded. National-team tournaments are filed in the club season they are played in,
following FotMob's grouping (e.g. the 2026 World Cup sits in 2026/2027).
