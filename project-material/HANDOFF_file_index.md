# File Index: European Football Transfer & Valuation Analytics

This index documents every source file in the project with its relative path, size, and explicit purpose.

| Relative Path | Size | Purpose |
| :--- | :--- | :--- |
| `HANDOFF_data_samples.json` | 56.8 KB | Source script or asset file. |
| `brutal_verification_report.md` | 1.2 KB | Brutal audit verification scorecard documenting initial database issues and resolution. |
| `cloudflared.exe` | 52.35 MB | Cloudflare Tunnel executable establishing secure public tunnels to localhost. |
| `master_checklist_top5_leagues.md` | 3.2 KB | Checklist tracking squad counts and promotion/relegation across all 96 clubs. |
| `package-lock.json` | 182.4 KB | Root npm lockfile. |
| `package.json` | 83 B | Root npm package file managing repository scripts. |
| `run_pinggy.py` | 974 B | Python fallback tunneling utility using pinggy.io SSH tunnels. |
| `vercel.json` | 221 B | Root Vercel configuration file. |
| `backend/Dockerfile` | 472 B | Docker container definition for running the FastAPI backend service in containerized environments. |
| `backend/Procfile` | 104 B | Deployment process definition for cloud PaaS hosts (Heroku, Render) to start uvicorn. |
| `backend/add_missing_stars.py` | 2.3 KB | Source script or asset file. |
| `backend/audit_barcelona.py` | 209 B | Targeted audit script for FC Barcelona squad roster and contract clauses. |
| `backend/audit_dataset.py` | 2.9 KB | Data validation script auditing squad sizes, position distributions, and null value counts. |
| `backend/audit_teams.py` | 545 B | Team normalization audit checking for club name variations and league assignments. |
| `backend/brutal_sweep.py` | 3.1 KB | Adversarial verification script scanning for missing stars, unlinked loans, and outlier values. |
| `backend/brutal_verification_loop.py` | 6.4 KB | Automated verification loop comparing SQLite database against verified ground-truth rosters. |
| `backend/calculate_modern_value.py` | 13.4 KB | Contract-aware valuation script with age-decay multipliers, club tiers, and superstar power-law adjustments. |
| `backend/check_transfers.py` | 332 B | Quick inspection utility checking recent transfer destinations in the SQLite database. |
| `backend/cleanup_duplicates.py` | 1.3 KB | Deduplication script merging redundant player rows based on fuzzy name and birth year matching. |
| `backend/compute_ratings_and_seasons.py` | 11.0 KB | Engine computing 0-100 Gaussian OVR ratings, econometric valuations, and 3-season competition breakdowns. |
| `backend/database.py` | 483 B | Database engine and sessionmaker configuration for SQLite (sql_app.db). |
| `backend/enrich_all_squads.py` | 47.9 KB | Batch enrichment script adding 2024-2026 performance stats across all 96 Top-5 league clubs. |
| `backend/enrich_and_deduplicate.py` | 8.4 KB | Integrated script performing simultaneous fuzzy deduplication and metric enrichment. |
| `backend/enrich_career_and_trophies.py` | 30.8 KB | Enrichment script generating silverware cabinets, hat-tricks, 10/10 masterclasses, and international caps. |
| `backend/enrich_contracts.py` | 7.6 KB | Script generating contract expiry years (2026-2035), weekly wages in EUR, and release clauses. |
| `backend/execute_transfers_and_departures.py` | 39.2 KB | Transfer execution script updating clubs for inter-league moves and pruning non-Top-5 departures. |
| `backend/fetch_api_football.py` | 4.6 KB | Scraping script interfacing with API-Football (v3.football.api-sports.io) to fetch league topscorers. |
| `backend/final_brutal_loop.py` | 1.3 KB | Final sanity checker verifying that every club has 20-33 players and zero null values. |
| `backend/fix_anomalies.py` | 5.3 KB | Heuristic fixer resolving impossible minutes, negative values, and inconsistent position labels. |
| `backend/fix_kdb.py` | 406 B | Targeted fix script for Kevin De Bruyne contract clauses and Manchester City squad alignment. |
| `backend/fix_se.py` | 601 B | Targeted fix script for AS Saint-Étienne Ligue 1 squad spelling and promotions. |
| `backend/fix_teams.py` | 2.0 KB | Reconciliation script fixing club name mismatches between FBref datasets and Transfermarkt. |
| `backend/full_cleanup_and_valuation.py` | 13.2 KB | Master script running complete pipeline from deduplication to rating calculation. |
| `backend/fuzzy_cleanup.py` | 1.7 KB | Fuzzy string matching script detecting variant spellings of player names (e.g., accents). |
| `backend/generate_data.py` | 5.9 KB | Synthetic data generator used for fallback testing when live scrapers are rate-limited. |
| `backend/generate_textbook_diagram.py` | 7.2 KB | Matplotlib script generating the textbook-style Gaussian distribution and valuation curve. |
| `backend/insert_all_missing_players.py` | 5.8 KB | Script parsing raw_data_*.txt to insert newly discovered players into the SQLite database. |
| `backend/live_updater.py` | 9.8 KB | Live data updater module handling web synchronization, late transfer application, and JSON export to frontend. |
| `backend/main.py` | 5.5 KB | FastAPI application entry point containing REST endpoints for players, summary stats, live sync triggers, and CORS middleware. |
| `backend/mega_2026_inter_league_sweep.py` | 875 B | Comprehensive sweep script tracking all Summer 2026 transfers across Europe's top 5 leagues. |
| `backend/migrate_db.py` | 836 B | Schema migration script adding release_clause_eur and wage columns to existing SQLite tables. |
| `backend/models.py` | 3.4 KB | SQLAlchemy ORM models declaring the Player and PlayerCompetitionStat relational database tables. |
| `backend/normalize_teams.py` | 7.5 KB | Team name normalization dictionary mapping 200+ raw scraped names to 96 canonical clubs. |
| `backend/phase1_cleanup_relegated.py` | 3.5 KB | Pruning script removing clubs relegated to Championship, Segunda, Serie B, 2. Bundesliga, Ligue 2. |
| `backend/phase2_pl_crossref.py` | 22.7 KB | Cross-reference script validating Premier League squads against official PremierLeague.com rosters. |
| `backend/plot_textbook_consistency.py` | 4.0 KB | Matplotlib script plotting competition minute conservation and career hierarchy diagrams. |
| `backend/populate_all_missing_squads.py` | 38.9 KB | Squad population script filling out incomplete rosters to ensure minimum 20 players per club. |
| `backend/populate_competition_stats.py` | 19.9 KB | Populates player_competition_stats table with league, cup, UCL, and international metrics. |
| `backend/raw_data_bundesliga.txt` | 23.2 KB | Scraped 2024-2025 Bundesliga first-team squads (18 clubs). |
| `backend/raw_data_laliga.txt` | 24.7 KB | Scraped 2024-2025 La Liga first-team squads (20 clubs). |
| `backend/raw_data_ligue1.txt` | 21.2 KB | Scraped 2024-2025 Ligue 1 first-team squads (18 clubs). |
| `backend/raw_data_pl.txt` | 28.1 KB | Scraped 2024-2025 Premier League first-team squads (20 clubs). |
| `backend/raw_data_seriea.txt` | 24.5 KB | Scraped 2024-2025 Serie A first-team squads (20 clubs). |
| `backend/real_data.csv` | 1.64 MB | Historical FBref / StatsBomb European 5 Leagues dataset with 2,921 players and 143 raw metrics. |
| `backend/requirements.txt` | 58 B | Python pip dependencies for FastAPI backend (fastapi, uvicorn, sqlalchemy, pydantic). |
| `backend/schemas.py` | 2.1 KB | Pydantic validation schemas defining data contracts for player objects and competition statistics. |
| `backend/show_top.py` | 948 B | CLI utility printing top 20 most valuable players from SQLite database. |
| `backend/sql_app.db` | 3.71 MB | SQLite database containing 2,521 players and 24,384 multi-season competition records. |
| `backend/sync_modern_rosters_2026.py` | 9.2 KB | Sync script aligning squads with August 30, 2026 verified transfer window closure rosters. |
| `backend/test_adversarial_integrity.py` | 37.3 KB | Test suite with 50+ adversarial assertions validating data integrity and mathematical consistency. |
| `backend/top_up_all_squads_to_20.py` | 16.3 KB | Fallback population script ensuring no top-5 club has fewer than 20 first-team players. |
| `backend/truth_prune.py` | 4.1 KB | Pruning script removing retired players and free agents who left Europe's top 5 leagues. |
| `backend/update_database_2025.py` | 4.8 KB | Database update script advancing player ages and applying 2025/2026 season statistics. |
| `backend/update_minor_transfers.py` | 659 B | Applies secondary and loan transfers for mid-table and promoted clubs. |
| `backend/update_transfers.py` | 778 B | Applies marquee summer transfers (Mbappé to Real Madrid, Olise to Bayern, etc.). |
| `backend/venezia.csv` | 903 B | Promoted Serie A squad export for Venezia FC containing newly promoted roster players. |
| `backend/verify_all_squads.py` | 1.0 KB | Verification script printing squad counts per team and flagging squads outside 20-33 range. |
| `backend/verify_database_integrity.py` | 29.8 KB | Comprehensive database verification script checking 20+ invariants across all 2,521 players. |
| `backend/verify_system.py` | 3.5 KB | End-to-end integration test verifying backend API endpoints and data consistency. |
| `dbt/dbt_project.yml` | 428 B | dbt project configuration defining models and data transformation stages for PostgreSQL/Snowflake. |
| `dbt/profiles.yml` | 560 B | dbt database connection profile for development and production analytics warehouses. |
| `frontend/.gitignore` | 491 B | Source script or asset file. |
| `frontend/AGENTS.md` | 678 B | Source script or asset file. |
| `frontend/CLAUDE.md` | 11 B | Source script or asset file. |
| `frontend/README.md` | 1.4 KB | Frontend setup documentation and development instructions. |
| `frontend/eslint.config.mjs` | 465 B | ESLint rules configuration for Next.js application. |
| `frontend/next-env.d.ts` | 288 B | Source script or asset file. |
| `frontend/next.config.ts` | 325 B | Next.js configuration enabling standalone output mode and Turbopack options. |
| `frontend/package-lock.json` | 229.5 KB | Source script or asset file. |
| `frontend/package.json` | 531 B | Node.js dependencies and npm scripts for Next.js 16, React 19, Lucide, and Tailwind. |
| `frontend/postcss.config.mjs` | 94 B | PostCSS configuration for Tailwind CSS compilation. |
| `frontend/tsconfig.json` | 670 B | TypeScript compiler options with strict type checking and '@/*' path aliases. |
| `frontend/vercel.json` | 28 B | Vercel deployment configuration specifying framework preset and build settings. |
| `frontend/public/file.svg` | 391 B | Source script or asset file. |
| `frontend/public/globe.svg` | 1.0 KB | Source script or asset file. |
| `frontend/public/next.svg` | 1.3 KB | Source script or asset file. |
| `frontend/public/vercel.svg` | 128 B | Source script or asset file. |
| `frontend/public/window.svg` | 385 B | Source script or asset file. |
| `frontend/src/app/favicon.ico` | 25.3 KB | Application favicon icon. |
| `frontend/src/app/globals.css` | 488 B | Tailwind CSS directives, theme colors, and custom scrollbar styling. |
| `frontend/src/app/layout.tsx` | 690 B | Root Next.js layout providing global HTML shell, metadata, and Tailwind font configurations. |
| `frontend/src/app/page.tsx` | 49.3 KB | Main Next.js dashboard UI featuring player search, filters, career stats strip, and trophy cabinet. |
| `frontend/src/app/api/players/route.ts` | 4.1 KB | API route returning paginated, filtered players from backend proxy or bundled players.json. |
| `frontend/src/app/api/players/[id]/route.ts` | 759 B | API route returning a single player by ID with competition stats. |
| `frontend/src/app/api/stats/summary/route.ts` | 487 B | API route returning total players, release clause counts, and top player metrics. |
| `frontend/src/app/api/sync/route.ts` | 1.2 KB | API route handling POST trigger to initiate live synchronization with backend or serverless engine. |
| `frontend/src/app/docs/route.ts` | 1.1 KB | API route serving interactive Swagger UI documentation for Next.js API routes. |
| `frontend/src/app/openapi.json/route.ts` | 772 B | API route serving OpenAPI 3.0 specification for frontend API endpoints. |
| `frontend/src/data/players.json` | 13.58 MB | Bundled 14MB JSON database containing all 2,521 players and their 24,384 competition records. |
| `frontend/src/data/summary.json` | 342 B | Precomputed summary statistics for instant zero-latency loading on Vercel. |
| `ingestion/ingest.py` | 3.6 KB | ETL script fetching transfer data from API-Football and staging JSON records to AWS S3. |
| `ingestion/requirements.txt` | 45 B | Python dependencies for ingestion pipeline (requests, pandas, boto3). |
| `ml_model/requirements.txt` | 104 B | Python dependencies for ML training (xgboost, scikit-learn, pandas, joblib, sqlalchemy). |
| `ml_model/train.py` | 3.2 KB | Machine learning training script training an XGBoost regressor on player transfer features. |
| `terraform/alb.tf` | 875 B | Terraform configuration provisioning Application Load Balancer with HTTP/HTTPS listeners. |
| `terraform/ecs.tf` | 516 B | Terraform configuration provisioning AWS ECS Fargate cluster for backend and scraper tasks. |
| `terraform/main.tf` | 369 B | Terraform root module configuring AWS infrastructure resources. |
| `terraform/providers.tf` | 162 B | Terraform provider declaration for AWS (hashicorp/aws). |
| `terraform/rds.tf` | 1.2 KB | Terraform configuration provisioning PostgreSQL RDS instance for player analytics database. |
| `terraform/s3.tf` | 316 B | Terraform configuration provisioning AWS S3 buckets for raw ingestion staging and models. |
| `terraform/variables.tf` | 337 B | Terraform input variable definitions for AWS VPC, RDS, and ECS clusters. |
