# meteoscat — server (`cepdata`)

Repo: <https://github.com/mrHumildad/cepdata>

Data half of the **meteoscat** project. It scrapes Meteocat XEMA observations,
aggregates them into daily per-station shards, and publishes those shards as
this repo's GitHub Pages **data site**. The React app lives in the separate
**client** repo and consumes the shards over HTTP.

Splitting the repos is deliberate: the daily cron job commits here every
morning, so the client's git history and Pages deploys stay untouched by data
churn.

## Layout

| Path | What it is |
| :--- | :--- |
| `meteokat/scrapeMap.py` | Scrapes the XEMA daily page for a rolling window of days → `meteokat/full_dades.json` (gitignored) |
| `meteokat/aggregate.py` | Turns the raw payloads into `data/daily/YYYY-MM-DD.json` + `data/daily/index.json` |
| `data/daily/` | **The published artifact** — committed by CI, served by Pages |
| `config/stations.json` | Server-local copy of the client's `src/logic/stations.json` (station-code seed list) |
| `meteokat/build_lithology.py` | One-off: builds the geology grid into `build/` (needs ICGC GeoPackage in `meteokat/raw/`) |
| `meteokat/mcsc_sample.py` | One-off: samples the MCSC land-cover map per station into `build/` |
| `meteokat/litho_units_audit.json` | Curation audit produced by `build_lithology.py` (committed) |
| `.github/workflows/daily-data.yml` | Daily scrape → aggregate → commit `data/daily` |
| `.github/workflows/deploy-data.yml` | Publishes `data/` to GitHub Pages |

## Daily pipeline

```
scrapeMap.py ──▶ meteokat/full_dades.json ──▶ aggregate.py ──▶ data/daily/*.json
                                                                     │
                                          commit (CI) ───────────────┘
                                                                     │
                                          deploy-data.yml ──▶ Pages data site
```

Run it by hand:

```bash
pip install -r meteokat/requirements.txt
cd meteokat
python scrapeMap.py 60   # writes meteokat/full_dades.json
python aggregate.py      # writes ../data/daily/
```

`aggregate.py` mirrors `src/logic/refineData.js` in the client exactly, so the
shards are numerically identical to the old in-bundle aggregation.

### Setup after creating the repo

1. Enable **Settings → Pages → Source: GitHub Actions** in this repo.
2. The data site is then `https://mrhumildad.github.io/cepdata/`, so shards are
   at `https://mrhumildad.github.io/cepdata/daily/index.json`.
3. Put that URL in the client's `VITE_DATA_BASE_URL` (see `client/.env.production`).

## One-off build scripts

These generate static artifacts that belong to the **client** repo's
`public/logic/`. They are not part of the daily job and not run by CI.

```bash
python3 -m venv meteokat/venv
meteokat/venv/bin/pip install -r meteokat/requirements-build.txt

meteokat/venv/bin/python meteokat/build_lithology.py   # → build/litho_grid.json
python3 meteokat/mcsc_sample.py                        # → build/forest_types.json

# then publish them into the client repo:
cp build/litho_grid.json build/forest_types.json ../client/public/logic/
```

`config/stations.json` is a copy of the client's `src/logic/stations.json`.
Stations change rarely (a handful of times a year); when the client's list
changes, refresh the copy here so newly added stations get summarized:

```bash
cp ../client/src/logic/stations.json config/stations.json
```
